"""Optional integration through BashCut's real Swift validation and inverse edit engine."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from support import FOLDER,HAS_RUNTIME
from test_timeline import fixture,host_timeline
if HAS_RUNTIME:
    from studio import timeline

@unittest.skipUnless(HAS_RUNTIME and os.environ.get('STUDIO_NATIVE_VALIDATOR'),
                     'Set STUDIO_NATIVE_VALIDATOR to the optional compiled API 8 test harness.')
class NativeTests(unittest.TestCase):
    def test_native_codec_atomic_edit_and_undo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);values=fixture(root)
            scenes,audio,cues,_,_=timeline.inputs(values)
            cues[3]={'id':3,'start':1,'end':3,'text':'Overlapping caption'}
            host=host_timeline();host['tracks']=[t for t in host['tracks'] if t['role']!='voiceover']
            ops,_=timeline.operations(scenes,audio,cues,host,root)
            project=dict(schema='bashcut.project/1',id='studio-test',name='Generated native validation',
                         media=[],contentLanguage='vi',**host)
            project['format']['sampleRate']=48000
            project_path=root/'project.json';ops_path=root/'ops.json'
            project_path.write_text(json.dumps(project));ops_path.write_text(json.dumps(ops))
            result=subprocess.run([os.environ['STUDIO_NATIVE_VALIDATOR'],str(FOLDER/'plugin.json'),
                str(project_path),str(ops_path)],capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('one undo restores',result.stdout)
