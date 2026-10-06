"""Generate tiny demo media in a chosen empty folder: python examples/generate.py /tmp/studio-demo."""
import shutil
import sys
import wave
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(sys.argv[1]).expanduser().resolve()
root.mkdir(parents=True,exist_ok=True)
if any(root.iterdir()):
    raise SystemExit('Choose an empty demo folder.')
images = root/'images';images.mkdir()
for n,color in ((1,(30,70,110)),(2,(90,50,90))):
    image=Image.new('RGB',(1280,720),color)
    draw=ImageDraw.Draw(image);draw.text((600,350),f'SC{n:02d}',fill='white')
    image.save(images/f'SC{n:02d}.png')
with wave.open(str(root/'voice.wav'),'wb') as audio:
    audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(16000)
    audio.writeframes(b'\0\0'*64000)
(root/'voice.srt').write_text('1\n00:00:00,000 --> 00:00:02,000\nXin chào\n\n2\n00:00:02,000 --> 00:00:04,000\nTạm biệt\n')
shutil.copyfile(Path(__file__).with_name('scenes.json'),root/'scenes.json')
print(root)
