import json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from support import HAS_RUNTIME
if HAS_RUNTIME:
    from studio import speech,state
    from studio.protocol import safe_error
    from studio.vibi import VibiError

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


