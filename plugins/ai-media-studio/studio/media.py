"""Bundled ffmpeg and generated-media helpers; argv only, no system dependency."""
import math
import re
import subprocess
from pathlib import Path
from fractions import Fraction


def get_ffmpeg_path():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def run_ffmpeg(args):
    completed = subprocess.run([get_ffmpeg_path(), '-v', 'error', '-nostdin', *map(str, args)],
                               capture_output=True, timeout=600)
    if completed.returncode:
        raise ValueError('Could not process media with bundled ffmpeg.')


def duration(path):
    result = subprocess.run([get_ffmpeg_path(), '-nostdin', '-i', str(path)],
                            capture_output=True, text=True, timeout=30)
    found = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', result.stderr)
    if not found:
        raise ValueError('Could not measure audio duration.')
    h, m, s = map(float, found.groups())
    value = h * 3600 + m * 60 + s
    if not math.isfinite(value) or value <= 0:
        raise ValueError('Audio duration must be positive.')
    return value


def frame(seconds, fps):
    # Match Swift rounded() (half away from zero), including 30000/1001 projects.
    return math.floor(float(Fraction(str(seconds)) * Fraction(*fps)) + 0.5)


def media_entry(path, kind, root, fps, seconds=None):
    import os, uuid
    entry = {'id': str(uuid.uuid4()), 'path': os.path.relpath(Path(path).resolve(), Path(root).resolve()),
             'kind': kind, 'fps': fps, 'frames': max(1, frame(seconds or 3600, fps))}
    if kind == 'image':
        from PIL import Image
        with Image.open(path) as image:
            entry.update(width=image.width, height=image.height, hasAudio=False)
    else:
        entry['hasAudio'] = kind == 'audio'
    return entry


def thumbnail(path, output, video=False):
    output = Path(output)
    if video:
        run_ffmpeg(['-y', '-i', path, '-frames:v', '1', '-vf', 'scale=640:-1', output])
    else:
        from PIL import Image
        with Image.open(path) as image:
            image.thumbnail((640, 640))
            image.save(output, 'PNG')
    return str(output)
