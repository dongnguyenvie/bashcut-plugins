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


class ManifestTests(unittest.TestCase):
    def test_manifest_and_skill(self):
        manifest=json.loads((FOLDER/'plugin.json').read_text())
        self.assertEqual(manifest_problems(manifest),[])
        self.assertEqual(skill_problems(FOLDER,manifest),[])
        self.assertEqual(manifest['apiVersion'],8)
        self.assertEqual([v['location'] for v in manifest['contributes']['views']],['panel','dock','sheet','sheet'])
        self.assertEqual(next(o for o in manifest['options'] if o['id']=='apiKey')['type'],'secret')
        self.assertTrue(os.access(FOLDER/'bin/provider',os.X_OK))


@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class SpeechTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.env=patch.dict(os.environ,VIBI_FAKE='1',BASHCUT_PLUGIN_DATA=str(self.root/'data'),
                            BASHCUT_PLUGIN_CACHE=str(self.root/'cache'));self.env.start()
    def tearDown(self):self.env.stop();self.tmp.cleanup()
    def request(self,text='Xin chào.',count=1,offset=0,options=None):
        req=Mock()
        req.params={'text':text,'language':'vi','takeCount':count,'takeOffset':offset,
                    'outputDirectory':str(self.root/'output'),'options':options or {'transcript':True}}
        req.cancelled.return_value=False
        return req
    def test_fake_audio_and_srt(self):
        req=self.request()
        with patch('requests.Session.request',side_effect=AssertionError('Network forbidden')):
            result=speech.synthesize(req)
        self.assertEqual(result['takes'],[{'audioPath':'take-1.mp3'}])
        self.assertTrue((self.root/'output/take-1.mp3').stat().st_size>0)
        self.assertIn('Xin chào',(self.root/'output/take-1.srt').read_text())
        self.assertFalse(list((self.root/'output').glob('.parts-*')))
    def test_paid_guard_runs_before_account_or_task(self):
        for count,offset in ((3,0),(1,1),(0,0)):
            with patch('studio.speech.Client') as client:
                with self.assertRaisesRegex(VibiError,'Paid-take limit'):
                    speech.synthesize(self.request(count=count,offset=offset))
                client.assert_not_called()
    def test_long_chunks_concatenate_and_offset_cues(self):
        text=('Xin chào. '*500).strip()
        result=speech.synthesize(self.request(text))
        from studio.scenes import parse_srt_file
        cues=list(parse_srt_file(self.root/'output/take-1.srt').values())
        self.assertEqual(len(cues),2)
        self.assertGreater(cues[1]['start'],0)
        self.assertGreaterEqual(cues[1]['start'],cues[0]['end']-.02)
        self.assertEqual(len(result['takes']),1)
    def test_selected_voice_shared_with_provider_without_storing_secret(self):
        state.update(selectedVoice={'id':'selected','name':'Demo','provider':'minimax','language':'vi'})
        with patch('studio.speech.body',wraps=speech.body) as builder:
            speech.synthesize(self.request(options={'apiKey':'SECRET','voice':'manual','transcript':False}))
        self.assertEqual(builder.call_args.args[2]['provider'],'minimax')
        self.assertNotIn('SECRET',(self.root/'data/preferences.json').read_text())
    def test_error_sanitization_and_preference_allowlist(self):
        result=safe_error(ValueError('invalid SECRET'),{'options':{'apiKey':'SECRET'}})
        self.assertNotIn('SECRET',json.dumps(result))
        with self.assertRaises(ValueError):state.update(apiKey='SECRET')


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
