"""Paid-take guard, long speech concatenation and correctly offset SubRip files."""
import tempfile
from pathlib import Path
from . import state
from .vibi import Client, VibiError, split_text, body
from .media import duration, run_ffmpeg
from .scenes import parse_srt_file


def timestamp(seconds):
    ms = max(0, int(float(seconds)*1000+.5))
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'


def synthesize(request):
    params = request.params
    options = dict(params.get('options') or {})
    selected = state.read().get('selectedVoice') or {}
    if selected:
        options.update(provider=selected['provider'], voice=selected['id'])
    count, offset = int(params.get('takeCount', 1)), int(params.get('takeOffset', 0))
    maximum = int(options.get('maxTakes', 1))
    if not 1 <= maximum <= 3 or count < 1 or offset < 0 or offset + count > maximum:
        raise VibiError('Paid-take limit exceeded. Set Voice takes to 1, or raise Maximum paid takes in plugin options.')
    text = str(params.get('text') or '').strip()
    chunks = split_text(text)
    if not chunks:
        raise VibiError('Write text to speak first.')
    if len(chunks) > 100:
        raise VibiError('Speech is limited to 100 chunks per generation.')
    voice = str(options.get('voice') or '').strip()
    client = Client(options.get('apiKey', ''))
    if not voice:
        if client.fake:
            voice = 'demo'
        else:
            raise VibiError('Choose a voice in the Voices tab, or set Voice ID in plugin options.')
    # Validate local options before checking the account or making any paid request.
    body(chunks[0], params.get('language', 'vi'), options)
    client.account()
    output = Path(params['outputDirectory']).resolve()
    output.mkdir(parents=True, exist_ok=True)
    takes = []
    for take_index in range(count):
        request.check_cancelled()
        name = f'take-{offset + take_index + 1}'
        audio, srt = output / (name+'.mp3'), output / (name+'.srt')
        with tempfile.TemporaryDirectory(prefix='.parts-', dir=output) as temporary:
            parts, cues, elapsed = [], [], 0.0
            for index, chunk in enumerate(chunks):
                request.check_cancelled()
                request.progress((take_index + index/len(chunks))/count,
                                 f'Generating take {offset+take_index+1}, part {index+1}/{len(chunks)}')
                part = Path(temporary) / f'part-{index}.mp3'
                client.synthesize_part(voice, chunk, params.get('language', 'vi'), options, part,
                    lambda status: request.progress(None, 'Vibi: '+status), request.cancelled)
                seconds = duration(part)
                if options.get('transcript'):
                    for cue in parse_srt_file(part.with_suffix('.srt')).values():
                        cues.append(dict(start=cue['start']+elapsed, end=cue['end']+elapsed, text=cue['text']))
                elapsed += seconds
                parts.append(part)
            request.progress(None, 'Preparing audio and transcript')
            # Relative generated names need no user-path or shell escaping.
            concat = Path(temporary)/'parts.txt'
            concat.write_text(''.join(f"file '{part.name}'\n" for part in parts))
            run_ffmpeg(['-y', '-f', 'concat', '-safe', '1', '-i', concat, '-c:a', 'libmp3lame',
                        '-q:a', '2', audio])
            if options.get('transcript'):
                if not cues:
                    raise VibiError('The requested transcript contains no valid captions.')
                srt.write_text('\n\n'.join(f"{i+1}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}"
                                            for i,c in enumerate(cues))+'\n', encoding='utf-8')
        takes.append({'audioPath': audio.name})
        state.update(lastTake={'audio': str(audio), 'srt': str(srt) if srt.exists() else None})
    request.progress(1, 'Speech ready')
    return {'takes': takes}
