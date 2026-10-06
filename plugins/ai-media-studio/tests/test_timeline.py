import json
import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from support import HAS_RUNTIME
from studio.scenes import parse_json_data,compute_timeline,parse_srt_file
from studio.edit_document import create_document,validate_document,save_document,load_document
from studio.scene_motion import normalize_motion
if HAS_RUNTIME:
    from PIL import Image
    from studio import timeline


def host_timeline():
    return {'rev':4,'format':{'fps':[30000,1001],'width':1920,'height':1080},'tracks':[
        {'id':'dynamic-main','kind':'video','role':'main','name':'Main','magnetic':True,'items':[]},
        {'id':'dynamic-captions','kind':'text','role':'captions','name':'Captions','items':[]},
        {'id':'dynamic-audio','kind':'audio','role':'voiceover','name':'Voice','items':[]}]}


def fixture(root):
    images=root/'images';images.mkdir()
    for n in (1,2):Image.new('RGB',(64,48),(n*30,60,100)).save(images/f'SC{n:02d}.png')
    audio=root/'voice.wav'
    with wave.open(str(audio),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(16000);f.writeframes(b'\0\0'*64000)
    srt=root/'voice.srt'
    srt.write_text('1\n00:00:00,000 --> 00:00:02,000\nXin chào\n\n2\n00:00:02,000 --> 00:00:04,000\nTạm biệt\n')
    script=root/'scenes.json'
    script.write_text(json.dumps([{'id':f'SC{n:02d}','character':'','character_info':'','prompt':'Image',
        'subtitle_ids':[n],'start_at':f'00:00:0{(n-1)*2},000',
        'end_at':'00:00:02,000' if n==1 else 'AUDIO_END',
        'motion':{'type':'zoom_in','strength':'subtle'}} for n in (1,2)]))
    return {'scenes':str(script),'images':str(images),'audio':str(audio),'srt':str(srt)}


class SceneParserTests(unittest.TestCase):
    def test_legacy_dict_list_ranges_and_auto_distribution(self):
        self.assertEqual(parse_json_data({'SC01':'1-3, 5','SC02':6},list(range(1,7)))[0]['subtitles'],[1,2,3,5])
        result=parse_json_data(['SC01','SC02'],[1,2,3,4,5])
        self.assertEqual([s['subtitles'] for s in result],[[1,2,3],[4,5]])
        self.assertEqual(parse_json_data([{'scene':'SC01','subs':[1]}],[1])[0]['id'],'SC01')

    def test_strict_schema_rejects_discontinuous_and_wrong_order(self):
        scene={'id':'SC01','character':'','character_info':'','prompt':'x','subtitle_ids':[1],
               'start_at':'00:00:00,000','end_at':'AUDIO_END'}
        self.assertEqual(parse_json_data([scene],[1])[0]['id'],'SC01')
        wrong=dict(scene,start_at='00:00:01,000')
        with self.assertRaises(ValueError):parse_json_data([wrong],[1])
        with self.assertRaises(ValueError):parse_json_data([dict(scene,subtitle_ids=[2])],[1])
        wrong={'prompt':'x',**scene};wrong['prompt']='x'
        with self.assertRaises(ValueError):parse_json_data([wrong],[1])

    def test_srt_multiline_duplicate_and_invalid_times(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'voice.srt'
            path.write_text('\ufeff1\r\n00:00:00,000 --> 00:00:01,500\r\nLine 1\r\nLine 2\r\n')
            self.assertEqual(parse_srt_file(path)[1]['text'],'Line 1\nLine 2')
            for text in ('1\n00:00:60,000 --> 00:01:01,000\nBad',
                         '1\n00:00:01,000 --> 00:00:00,000\nBad',
                         '1\n00:00:00,000 --> 00:00:01,000\nA\n\n1\n00:00:02,000 --> 00:00:03,000\nB'):
                path.write_text(text)
                with self.assertRaises(ValueError):parse_srt_file(path)

    def test_motion_validation(self):
        self.assertEqual(normalize_motion({'type':'shake','strength':'medium'})['type'],'shake')
        self.assertEqual(normalize_motion({'type':'unknown','strength':'subtle'})['type'],'none')


@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.env=patch.dict(os.environ,{'BASHCUT_PLUGIN_DATA':str(self.root/'data'),
                                       'BASHCUT_PLUGIN_CACHE':str(self.root/'cache')});self.env.start()
        self.values=fixture(self.root)

    def tearDown(self):self.env.stop();self.tmp.cleanup()

    def request(self,rev=4):
        class Fake:
            params={'context':{'project':{'root':str(self.root)}}}
            calls=[]
            def check_cancelled(self):pass
            def call(inner,method,params=None):
                inner.calls.append((method,params))
                return dict(host_timeline(),rev=rev) if method=='timeline.get' else {'valid':True}
        return Fake()

    def test_atomic_operations_include_media_motion_voice_and_captions(self):
        request=self.request()
        summary=timeline.prepare(request,self.values)
        self.assertEqual(summary['scenes'],2)
        apply=[p for m,p in request.calls if m=='timeline.apply']
        self.assertEqual(len(apply),1);self.assertTrue(apply[0]['dryRun'])
        ops=apply[0]['ops']
        self.assertEqual(sum(o['op']=='addMedia' for o in ops),3)
        insert=[o for o in ops if o['op']=='insert']
        self.assertEqual(len(insert),5)
        pictures=[o['item'] for o in insert if o['track']=='dynamic-main']
        self.assertEqual(pictures[0]['at']+pictures[0]['dur'],pictures[1]['at'])
        self.assertIn('zoom',pictures[0]['keyframes'])
        self.assertEqual(pictures[0]['keyframes']['zoom'][-1]['value'],1.05)
        timeline.commit(request,summary['plan'])
        self.assertFalse(request.calls[-1][1]['dryRun'])
        self.assertEqual(request.calls[-1][1]['ops'],ops)

    def test_stale_revision_and_sources_refuse_commit(self):
        summary=timeline.prepare(self.request(),self.values)
        with self.assertRaisesRegex(ValueError,'Timeline changed'):
            timeline.commit(self.request(rev=5),summary['plan'])
        Path(self.values['scenes']).write_text('[]')
        with self.assertRaisesRegex(ValueError,'source files changed'):
            timeline.commit(self.request(),summary['plan'])

    def test_missing_images_prevent_host_edits(self):
        for p in (self.root/'images').iterdir():p.unlink()
        request=self.request();summary=timeline.prepare(request,self.values)
        self.assertEqual(summary['missing'],['SC01','SC02'])
        self.assertEqual(request.calls,[])

    def test_occupied_main_refused(self):
        host=host_timeline();host['tracks'][0]['items']=[{'id':'old','at':0,'dur':20}]
        scenes,audio,cues,paths,missing=timeline.inputs(self.values)
        with self.assertRaisesRegex(ValueError,'empty main'):
            timeline.operations(scenes,audio,cues,host,self.root)

    def test_caption_overflow_creates_text_layer_before_audio(self):
        scenes,audio,cues,_,_=timeline.inputs(self.values)
        cues[3]={'id':3,'start':1,'end':3,'text':'Overlap'}
        ops,_=timeline.operations(scenes,audio,cues,host_timeline(),self.root)
        layers=[o for o in ops if o['op']=='addTrack']
        self.assertEqual(len(layers),1)
        self.assertEqual(layers[0]['atIndex'],2)
        self.assertEqual(layers[0]['track']['kind'],'text')
        self.assertEqual(layers[0]['track']['items'],[])

    def test_clean_image_preferred_deterministically(self):
        Image.new('RGB',(64,48)).save(self.root/'images'/'SC01_clean.png')
        scenes,_,_,_,_=timeline.inputs(self.values)
        self.assertEqual(scenes[0]['image'].name,'SC01_clean.png')

    def test_document_roundtrip_and_unknown_fields(self):
        scenes,audio,cues,_,_=timeline.inputs(self.values)
        doc=create_document(self.root,scenes,cues,self.root/'images',audio,Path(self.values['srt']),
                            '16:9',30,4,True)
        doc['futureField']={'kept':True}
        path=self.root/'edit.json';save_document(path,doc)
        with self.assertRaises(FileExistsError):save_document(path,doc)
        self.assertEqual(load_document(path)['futureField'],{'kept':True})
        scenes2,audio2,_,_,_=timeline.inputs({'scenes':str(path)})
        self.assertEqual(scenes2[0]['id'],'SC01');self.assertEqual(audio2,audio)
        doc['version']=2
        with self.assertRaises(ValueError):validate_document(doc)
