import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,Mock
from support import FOLDER,HAS_RUNTIME,Session,nodes
from plugin_manifest import manifest_problems,skill_problems
if HAS_RUNTIME:
    from studio import speech,state
    from studio.protocol import safe_error
    from studio.vibi import VibiError


@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class SessionTests(unittest.TestCase):
    def setUp(self):self.session=Session()
    def tearDown(self):self.session.close()
    def test_all_views_have_unique_nodes_and_render_without_network(self):
        for view in ('studio','voices','watermark','build'):
            result=self.session.view(view)
            self.assertIn('result',result,result)
            ids=[n['id'] for n in nodes(result['result']['body']) if 'id' in n]
            self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(self.session.calls,[])
    def test_voice_paging_and_use_persist(self):
        first=self.session.view('voices',event={'node':'refresh','type':'click'})['result']
        self.assertEqual(len(first['state']['voices']),30)
        second=self.session.view('voices',state=first['state'],event={'node':'next','type':'click'})['result']
        self.assertEqual(second['state']['page'],2)
        voice=second['state']['voices'][0]
        chosen=self.session.view('voices',state=second['state'],event={'node':'voices','type':'action',
            'value':{'item':voice['id'],'action':'use'}})['result']
        prefs=json.loads((self.session.root/'data/preferences.json').read_text())
        self.assertEqual(prefs['selectedVoice']['id'],voice['id'])
        studio=self.session.view('studio')['result']
        self.assertIn(voice['name'],json.dumps(studio))
    def test_credits_only_refresh_on_user_event(self):
        result=self.session.view('studio',event={'node':'credits','type':'click'})['result']
        self.assertIn('100000',json.dumps(result))
        self.assertNotIn('refreshSeconds',result)
    def test_unknown_method_error_does_not_crash_session(self):
        error=self.session.request('bad.method',{})
        self.assertIn('error',error)
        self.assertIn('result',self.session.view('studio'))
    def test_host_call_handles_overlapping_provider_request(self):
        s=self.session
        s.write({'type':'request','id':'view1','method':'view.event','params':{'view':'studio','values':{'text':'Hi'},
                  'event':{'node':'speak','type':'click'},'options':{}}})
        while True:
            message=s.read()
            if message.get('type')=='call':break
        self.assertEqual(message['method'],'voice.speak')
        call_id=message['callId']
        s.write({'type':'request','id':'voice1','method':'voice.synthesize','params':{'text':'Hi','language':'en',
            'takeCount':1,'takeOffset':0,'options':{},'outputDirectory':str(s.root/'speech')}})
        while True:
            reply=s.read()
            if reply.get('id')=='voice1' and 'result' in reply:break
        self.assertEqual(reply['result']['takes'][0]['audioPath'],'take-1.mp3')
        s.write({'type':'callResult','callId':call_id,'result':{'takes':[{'path':str(s.root/'speech/take-1.mp3')}]}})
        while True:
            reply=s.read()
            if reply.get('id')=='view1' and 'result' in reply:break
        self.assertIn('Speech ready',json.dumps(reply))
    def test_cancel_while_waiting_for_host(self):
        s=self.session
        s.write({'type':'request','id':'cancelme','method':'plugin.action','params':{'action':'bashcut.ai-media-studio.voices'}})
        while True:
            message=s.read()
            if message.get('type')=='call':break
        s.write({'type':'cancel','id':'cancelme'})
        reply=s.read()
        self.assertEqual(reply['error']['code'],'cancelled')
        s.write({'type':'callResult','callId':message['callId'],'result':{}})
        self.assertIn('result',s.view('studio'))
