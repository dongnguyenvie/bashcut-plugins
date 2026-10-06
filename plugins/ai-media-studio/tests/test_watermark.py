import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from support import HAS_RUNTIME
if HAS_RUNTIME:
    import numpy as np
    from PIL import Image
    from studio.watermark import GeminiWatermarkRemover
    from studio.video_watermark import VideoWatermarkRemover,get_veo3_text_box,heal_upscaled_video_edge_seam
    from studio.media import run_ffmpeg


@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class WatermarkTests(unittest.TestCase):
    def test_image_alpha_preserved_and_outside_roi_unchanged(self):
        pixels=np.full((512,512,4),110,dtype=np.uint8);pixels[:,:,3]=np.arange(512)%255
        before=Image.fromarray(pixels)
        after,meta=GeminiWatermarkRemover().remove_watermark(before,preset_mode='classic')
        result=np.asarray(after)
        self.assertTrue(np.array_equal(result[:,:,3],pixels[:,:,3]))
        self.assertTrue(np.array_equal(result[:200],pixels[:200]))
        self.assertEqual(after.mode,'RGBA')

    def test_veo_inverse_alpha_and_orientation(self):
        remover=VideoWatermarkRemover()
        h,w=720,1280
        clean=np.random.default_rng(10).integers(30,180,(h,w,3),dtype=np.uint8)
        marked=clean.copy();box=get_veo3_text_box(w,h)
        x,y,bw,bh=(box[k] for k in ('x','y','width','height'))
        alpha=np.asarray(remover.veo3_mask.getchannel('A'),dtype=np.float32)/255
        marked[y:y+bh,x:x+bw]=np.clip(clean[y:y+bh,x:x+bw]*(1-alpha[:,:,None])+255*alpha[:,:,None]+.5,0,255)
        restored,meta=remover.remove_veo3_frame(marked)
        self.assertEqual(meta['box'],box)
        self.assertLessEqual(np.abs(restored.astype(np.int16)-clean).max(),2)
        self.assertTrue(np.array_equal(restored[:y],marked[:y]))
        self.assertEqual(get_veo3_text_box(720,1280)['width'],34)

    def test_vectorized_seam_matches_reference_at_edges_and_interior(self):
        frame=np.random.default_rng(3).integers(0,255,(40,50,3),dtype=np.uint8)
        for box in ({'x':0,'y':0,'width':12,'height':12},{'x':20,'y':20,'width':20,'height':20}):
            for border in (1,2):
                expected=frame.copy();x,y=box['x'],box['y'];right=x+box['width'];bottom=y+box['height']
                for row in range(max(0,y-border),min(40,bottom+border)):
                    for col in range(max(0,x-border),min(50,right+border)):
                        if x+border<=col<right-border and y+border<=row<bottom-border:continue
                        avg=frame[max(0,row-1):min(40,row+2),max(0,col-1):min(50,col+2)].astype(np.float32).mean((0,1))
                        expected[row,col]=np.clip(frame[row,col].astype(np.float32)*.35+avg*.65,0,255).astype(np.uint8)
                self.assertTrue(np.array_equal(heal_upscaled_video_edge_seam(frame,box,border),expected))

    def test_video_generated_clip_audio_copy_and_original_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.mp4';target=Path(tmp)/'clean.mp4'
            run_ffmpeg(['-y','-f','lavfi','-i','color=c=gray:s=1280x720:r=24:d=0.3',
                        '-f','lavfi','-i','sine=frequency=440:duration=0.3','-shortest',
                        '-c:v','libx264','-c:a','aac',source])
            original=source.read_bytes()
            remover=VideoWatermarkRemover()
            with patch('shutil.which',return_value=None):
                info=remover.probe(source)
            self.assertEqual((info.width,info.height),(1280,720))
            result=remover.process_file(source,target,mode='veo3')
            self.assertTrue(result['success'],result)
            self.assertGreater(result['frames_processed'],0)
            self.assertEqual(source.read_bytes(),original)
            self.assertTrue(target.is_file())
            # Demux audio packets unchanged to verify copy, rather than trusting argv.
            a=Path(tmp)/'before.aac';b=Path(tmp)/'after.aac'
            for video,audio in ((source,a),(target,b)):
                run_ffmpeg(['-y','-i',video,'-vn','-c:a','copy','-f','adts',audio])
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with self.assertRaises(FileExistsError):remover.process_file(source,target,mode='veo3')

    def test_cancel_video_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.mp4';target=Path(tmp)/'clean.mp4'
            run_ffmpeg(['-y','-f','lavfi','-i','color=s=1280x720:r=24:d=0.3','-c:v','libx264',source])
            result=VideoWatermarkRemover().process_file(source,target,mode='veo3',is_cancelled=lambda:True)
            self.assertTrue(result['cancelled']);self.assertFalse(target.exists())
            self.assertFalse(list(Path(tmp).glob('.clean.*')))
