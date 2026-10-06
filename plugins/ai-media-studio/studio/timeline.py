"""Prepare a complete atomic BashCut edit, validate it, then commit the reviewed plan."""
import hashlib
import json
import math
import uuid
from pathlib import Path
from . import state
from .media import duration, frame, media_entry
from .scenes import parse_json_data, compute_timeline, parse_srt_file
from .scene_motion import normalize_motion, _motion_range
from .edit_document import load_document, document_timeline, media_path


def fingerprint(paths):
    result = []
    for path in paths:
        path = Path(path).resolve()
        stat = path.stat()
        result.append([str(path), stat.st_size, stat.st_mtime_ns])
    return hashlib.sha256(json.dumps(result).encode()).hexdigest()


def motion_keys(motion, length, width, height):
    motion = normalize_motion(motion)
    if motion['type'] in ('none', 'shake') or length < 2:
        return {}
    # Native keyframes preserve the source's strengths. Drift becomes a subtle pan in v1.
    if motion['type'].startswith('drift_'):
        motion = {'type': motion['type'].replace('drift_', 'pan_'), 'strength': 'subtle'}
    z0,z1,x0,x1,y0,y1 = _motion_range(motion)
    keys = {}
    for property, start, end in [('zoom',z0,z1), ('pan',x0*width,x1*width), ('tilt',-y0*height,-y1*height)]:
        if start != end or property == 'zoom' and start != 1:
            keys[property] = [{'frame':0, 'value':start, 'ease':'inOut'},
                              {'frame':length-1, 'value':end}]
    return keys


def inputs(values):
    script = Path(str(values.get('scenes') or '')).expanduser().resolve()
    if not values.get('scenes') or not script.is_file():
        raise ValueError('Choose an existing scenes.json or edit document.')
    raw = json.loads(script.read_text(encoding='utf-8-sig'))
    if isinstance(raw, dict) and 'version' in raw and 'tracks' in raw:
        doc = load_document(script)
        base = script.parent
        audio = media_path(base, doc['sources']['audio']).resolve()
        srt = media_path(base, doc['sources']['srt']).resolve()
        scene_list = document_timeline(base, doc)
    else:
        if not values.get('images') or not values.get('audio') or not values.get('srt'):
            raise ValueError('Choose the image folder, voice file and SRT.')
        images = Path(values['images']).expanduser().resolve()
        audio = Path(values['audio']).expanduser().resolve()
        srt = Path(values['srt']).expanduser().resolve()
        if not images.is_dir():
            raise ValueError('Image folder does not exist.')
        subtitles = parse_srt_file(srt)
        scenes = parse_json_data(raw, sorted(subtitles))
        scene_list = compute_timeline(scenes, subtitles, duration(audio), images)
    for path in (audio,srt):
        if not path.is_file():
            raise ValueError('Voice file or SRT does not exist.')
    cues = parse_srt_file(srt)
    if not cues:
        raise ValueError('SRT contains no valid captions.')
    if not scene_list:
        raise ValueError('Script contains no scenes.')
    missing = [s['id'] for s in scene_list if not s.get('image') or not Path(s['image']).is_file()]
    if missing:
        return scene_list, audio, cues, [script,audio,srt], missing
    seconds = duration(audio)
    previous = 0.0
    for scene in scene_list:
        start,end = float(scene['start']),float(scene['end'])
        if not all(math.isfinite(t) for t in (start,end)) or start < 0 or end <= start:
            raise ValueError('Scene timing must have positive, finite duration.')
        if abs(start-previous) > .001 or end > seconds+.02:
            raise ValueError('Scenes must be contiguous from zero and fit inside the voice duration.')
        if end-start > 3600:
            raise ValueError('A still-image scene cannot exceed one hour.')
        previous = end
    if abs(previous-seconds) > .02:
        raise ValueError('The final scene must end at the voice duration.')
    return scene_list, audio, cues, [script,audio,srt]+[s['image'] for s in scene_list], []


def operations(scene_list, audio, cues, timeline, root):
    fmt = timeline['format']
    fps = fmt['fps']
    width,height = fmt['width'],fmt['height']
    if len(fps) != 2 or any(type(n) is not int or n <= 0 for n in fps):
        raise ValueError('BashCut project frame rate is invalid.')
    tracks = json.loads(json.dumps(timeline['tracks']))
    main = next((t for t in tracks if t.get('role') == 'main' and t.get('kind') == 'video'),None)
    if not main:
        raise ValueError('The project needs a main video layer.')
    if main.get('locked'):
        raise ValueError('Unlock the main video layer before building.')
    if main.get('items'):
        raise ValueError('Build requires an empty main video layer. Open an empty project first.')
    ops, warnings = [], []
    def add_track(kind, role):
        track = {'id':str(uuid.uuid4()),'kind':kind,'role':role,'name':f'Studio {role}',
                 'magnetic':False,'items':[]}
        at = len(tracks) if kind == 'audio' else next((i for i,t in enumerate(tracks) if t['kind']=='audio'),len(tracks))
        ops.append({'op':'addTrack','track':dict(track,items=[]),'atIndex':at})
        tracks.insert(at,track)
        return track
    def available(kind,role,at,end):
        for track in tracks:
            if track['kind']==kind and track.get('role')==role and not track.get('locked') and all(
                i['at']+i['dur'] <= at or i['at'] >= end for i in track.get('items',[])):
                return track
        return add_track(kind,role)
    def insert(track,item):
        ops.append({'op':'insert','track':track['id'],'item':item})
        track.setdefault('items',[]).append(item)
    assets = {}
    for scene in scene_list:
        path = str(Path(scene['image']).resolve())
        if path not in assets:
            asset = media_entry(path,'image',root,fps)
            assets[path] = asset
            ops.append({'op':'addMedia','media':asset})
        at,end = frame(scene['start'],fps),frame(scene['end'],fps)
        if end <= at:
            raise ValueError(f"Scene {scene['id']} is shorter than one project frame.")
        item = {'id':str(uuid.uuid4()),'media':assets[path]['id'],'at':at,'dur':end-at,'in':0,'fill':True}
        keys = motion_keys(scene.get('motion'),end-at,width,height)
        if keys:
            item['keyframes'] = keys
        if normalize_motion(scene.get('motion'))['type']=='shake':
            warnings.append(f"{scene['id']}: shake has no v1 equivalent; kept still.")
        insert(main,item)
    audio_seconds = duration(audio)
    asset = media_entry(audio,'audio',root,fps,audio_seconds)
    ops.append({'op':'addMedia','media':asset})
    length = asset['frames']
    insert(available('audio','voiceover',0,length),
           {'id':str(uuid.uuid4()),'media':asset['id'],'at':0,'dur':length,'in':0})
    for cue in sorted(cues.values(),key=lambda c:(c['start'],c['id'])):
        at,end = frame(cue['start'],fps),frame(cue['end'],fps)
        if end <= at or end > length:
            raise ValueError('Captions must be at least one frame and fit inside the voice duration.')
        item = {'id':str(uuid.uuid4()),'at':at,'dur':end-at,'in':0,'text':cue['text'],
                'textPreset':'bold-outline'}
        insert(available('text','captions',at,end),item)
    if len(ops)>1000:
        raise ValueError('This script exceeds BashCut’s 1000-operation limit; split it into smaller projects.')
    return ops,warnings


def project_root(request):
    project = (request.params.get('context') or {}).get('project') or {}
    if not project.get('root'):
        raise ValueError('Open a saved BashCut project first.')
    return str(Path(project['root']).resolve())


def prepare(request, values):
    root = project_root(request)
    scene_list,audio,cues,paths,missing = inputs(values)
    summary = {'scenes':len(scene_list),'captions':len(cues),'duration':scene_list[-1]['end'],
               'missing':missing,'warnings':[],
               'sceneRows':[{'id':str(i),'title':str(scene['id'])[:120],
                             'subtitle':f"{scene['start']:.3f}–{scene['end']:.3f} s · {Path(scene['image']).name if scene.get('image') else 'Missing image'}"[:240]}
                            for i,scene in enumerate(scene_list[:100])]}
    if missing:
        return summary
    request.check_cancelled()
    timeline = request.call('timeline.get')
    request.call('schema.get')
    ops,warnings = operations(scene_list,audio,cues,timeline,root)
    request.call('timeline.apply',{'ops':ops,'baseRev':timeline['rev'],'dryRun':True,'label':'Build scene timeline'})
    plan_id = str(uuid.uuid4())
    plan = dict(ops=ops,baseRev=timeline['rev'],root=root,paths=list(map(str,paths)),fingerprint=fingerprint(paths))
    cache = state.folder(True)/'plans'
    cache.mkdir(exist_ok=True)
    (cache/(plan_id+'.json')).write_text(json.dumps(plan))
    summary.update(plan=plan_id,baseRev=timeline['rev'],warnings=warnings)
    return summary


def commit(request, plan_id):
    # IDs never become arbitrary file paths.
    if str(uuid.UUID(plan_id)) != plan_id:
        raise ValueError('Invalid preview plan.')
    path = state.folder(True)/'plans'/(plan_id+'.json')
    if not path.is_file():
        raise ValueError('Preview expired. Preview the scene build again.')
    plan = json.loads(path.read_text())
    if plan['root'] != project_root(request) or plan['fingerprint'] != fingerprint(plan['paths']):
        raise ValueError('Project or source files changed. Preview the scene build again.')
    timeline = request.call('timeline.get')
    if timeline['rev'] != plan['baseRev']:
        raise ValueError('Timeline changed after preview. Preview the scene build again.')
    result = request.call('timeline.apply',{'ops':plan['ops'],'baseRev':plan['baseRev'],
                                          'label':'Build scene timeline','dryRun':False})
    path.unlink(missing_ok=True)
    return result
