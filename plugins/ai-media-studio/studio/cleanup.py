"""Preview watermark cleanup in cache; save new files into BashCut's action directory."""
import uuid
from fractions import Fraction
from pathlib import Path
from PIL import Image
from . import state
from .media import media_entry, thumbnail
from .timeline import project_root, fingerprint
from .watermark import GeminiWatermarkRemover
from .video_watermark import VideoWatermarkRemover


def source_file(request, values, kind):
    path = values.get('path') or ((request.params.get('context') or {}).get('media') or {}).get('absolutePath')
    if not path or not Path(path).expanduser().is_file():
        raise ValueError('Choose an existing source file, or select media in BashCut.')
    return Path(path).expanduser().resolve()


def settings(values, kind):
    mode = values.get('mode') or ('auto' if kind=='image' else 'veo3')
    if kind=='video' and mode in ('auto','classic'):
        mode = 'veo3'
    if kind=='image' and mode not in ('auto','classic') or kind=='video' and mode not in ('veo3','gemini'):
        raise ValueError('Choose the correct watermark mode for this file.')
    scale = float(values.get('scale') or 0)
    if not 0 <= scale <= 4:
        raise ValueError('Mask scale must be between 0 and 4.')
    sx = values.get('offsetX', '')
    sy = values.get('offsetY', '')
    ox,oy = (None if v in ('',None) else int(v) for v in (sx,sy))
    return {'mode':mode,'scale':scale or None,'offsetX':ox,'offsetY':oy}


def clean_image(image, options):
    return GeminiWatermarkRemover().remove_watermark(image,scale=options['scale'],
        offset_x=options['offsetX'],offset_y=options['offsetY'],preset_mode=options['mode'])[0]


def preview(request, values, kind):
    source = source_file(request,values,kind)
    options = settings(values,kind)
    cache = state.folder(True)/'watermarks'/str(uuid.uuid4())
    cache.mkdir(parents=True)
    before,after = cache/'before.png',cache/'after.png'
    if kind=='image':
        with Image.open(source) as image:
            cleaned = clean_image(image,options)
            cleaned.thumbnail((640,640));cleaned.save(after)
        thumbnail(source,before)
    else:
        # Clean at the original resolution, THEN shrink the frame for UI display.
        from .media import run_ffmpeg
        import numpy as np
        full = cache/'frame.png'
        run_ffmpeg(['-y','-i',source,'-frames:v','1',full])
        with Image.open(full) as image:
            frame = np.array(image.convert('RGB'))
        remover = VideoWatermarkRemover()
        if options['mode']=='veo3':
            cleaned,_ = remover.remove_veo3_frame(frame,scale=options["scale"] or 1.0,offset_x=options["offsetX"] or 0,offset_y=options["offsetY"] or 0)
        else:
            from .video_watermark import heal_upscaled_video_edge_seam
            cleaned,meta = remover.remove_frame(frame,scale=options['scale'] or 1.01,
                offset_x=options['offsetX'] if options['offsetX'] is not None else -24,
                offset_y=options['offsetY'] if options['offsetY'] is not None else -24)
            cleaned = heal_upscaled_video_edge_seam(cleaned,meta['box'])
        thumbnail(full,before)
        image = Image.fromarray(cleaned);image.thumbnail((640,640));image.save(after)
        full.unlink(missing_ok=True)
    preview = dict(source=str(source),kind=kind,options=options,before=str(before),after=str(after),
                   root=project_root(request),fingerprint=fingerprint([source]))
    state.update(watermark=preview)
    return preview


def save(request, values, kind):
    source = source_file(request,values,kind)
    options = settings(values,kind)
    root = project_root(request)
    timeline = request.call('timeline.get')
    out = Path(request.params['outputDirectory']).resolve()
    out.mkdir(parents=True,exist_ok=True)
    out.relative_to(Path(root).resolve())
    target = out/(source.stem+'_clean'+('.png' if kind=='image' else '.mp4'))
    if target == source or target.exists():
        raise ValueError('Choose a new output file; originals are never overwritten.')
    request.check_cancelled()
    if kind=='image':
        with Image.open(source) as image:
            clean_image(image,options).save(target,'PNG')
        entry = media_entry(target,'image',root,timeline['format']['fps'])
    else:
        remover = VideoWatermarkRemover()
        info = remover.probe(source)
        previous = [-1]
        def progress(current,total):
            # Limit UI traffic without slowing the frame loop.
            percent = int(100*current/total) if total else current//30
            if percent != previous[0]:
                previous[0]=percent
                request.progress(current/total if total else None,f'Cleaning video: {current} frames')
                request.render([{'type':'progress','value':min(1,current/total) if total else 0,
                                 'label':f'Cleaning video: {current} frames'}])
        result = remover.process_file(source,target,mode=options['mode'],scale=options['scale'],
            offset_x=options['offsetX'],offset_y=options['offsetY'],
            progress_callback=progress,is_cancelled=request.cancelled)
        if not result.get('success'):
            if result.get('cancelled'):
                request.check_cancelled()
            raise ValueError('Video cleanup failed. Verify that ffmpeg can decode the source and copy its audio into MP4.')
        fps = Fraction(info.fps).limit_denominator(100000)
        entry = media_entry(target,'video',root,[fps.numerator,fps.denominator],
                            result['frames_processed']/info.fps)
        entry.update(width=info.width,height=info.height)
        # Probe audio through bundled ffmpeg instead of assuming the source has it.
        import subprocess
        from .media import get_ffmpeg_path
        probe = subprocess.run([get_ffmpeg_path(),'-nostdin','-i',str(source)],capture_output=True,text=True,timeout=30)
        entry['hasAudio']='Audio:' in probe.stderr
    return {'message':'Clean file added to project media.','label':'Remove watermark',
            'baseRev':timeline['rev'],'operations':[{'op':'addMedia','media':entry}],
            'files':[target.name],'data':{'path':str(target)}}
