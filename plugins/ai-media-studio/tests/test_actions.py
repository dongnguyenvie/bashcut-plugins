import json
import unittest
from pathlib import Path
from support import HAS_RUNTIME,Session
from test_timeline import fixture,host_timeline
if HAS_RUNTIME:
    from PIL import Image

@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class ActionTests(unittest.TestCase):
    def setUp(self):self.s=Session({'timeline.get':host_timeline(),'schema.get':{},'timeline.apply':{'changed':True}})
    def tearDown(self):self.s.close()
    def test_image_preview_then_save_registers_generated_media(self):
        path=self.s.root/'original.png';Image.new('RGBA',(512,512),(100,120,80,90)).save(path)
        original=path.read_bytes()
        params={'action':'bashcut.ai-media-studio.clean-image-file',
                'context':{'project':{'root':str(self.s.root),'rev':4}},'options':{},
                'outputDirectory':str(self.s.root/'generated/clean'),
                'params':{'path':str(path),'mode':'classic','preview':True}}
        preview=self.s.request('plugin.action',params)
        self.assertIn('result',preview,preview)
        self.assertNotIn('operations',preview['result'])
        self.assertEqual(self.s.calls[-1][0],'plugins.show-view')
        view=self.s.view('watermark')['result']
        self.assertEqual(view['body'][0]['type'],'imageCompare')
        params['params']['preview']=False
        result=self.s.request('plugin.action',params)['result']
        self.assertEqual(result['operations'][0]['op'],'addMedia')
        self.assertTrue(Path(result['data']['path']).is_file())
        self.assertEqual(path.read_bytes(),original)
        self.assertEqual(result['baseRev'],4)
    def test_build_action_dry_run_and_commit(self):
        values=fixture(self.s.root)
        params={'action':'bashcut.ai-media-studio.build-timeline','params':dict(values,dryRun=True),
                'context':{'project':{'root':str(self.s.root),'rev':4}}}
        result=self.s.request('plugin.action',params)['result']
        self.assertEqual(result['data']['scenes'],2)
        self.assertTrue(all(p['dryRun'] for m,p in self.s.calls if m=='timeline.apply'))
        params['params']['dryRun']=False
        result=self.s.request('plugin.action',params)['result']
        edits=[p for m,p in self.s.calls if m=='timeline.apply' and not p['dryRun']]
        self.assertEqual(len(edits),1)
        self.assertIn('one undoable edit',result['message'])
    def test_build_sheet_requires_preview_and_refuses_changed_inputs(self):
        values=fixture(self.s.root)
        first=self.s.view('build',values=values,event={'node':'preview','type':'click'})['result']
        self.assertIn('plan',first['state']['summary'])
        changed=dict(values,images='other-folder')
        error=self.s.view('build',state=first['state'],values=changed,event={'node':'build','type':'click'})
        self.assertIn('Inputs changed',error['error']['message'])
        edits=[p for m,p in self.s.calls if m=='timeline.apply' and not p['dryRun']]
        self.assertEqual(edits,[])
    def test_bad_path_error_does_not_echo_key(self):
        result=self.s.request('plugin.action',{'action':'bashcut.ai-media-studio.clean-image-file',
            'params':{'path':'SECRET'},'options':{'apiKey':'SECRET'}})
        self.assertIn('error',result)
        self.assertNotIn('SECRET',json.dumps(result))
