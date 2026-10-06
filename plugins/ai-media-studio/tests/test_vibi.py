import unittest
from unittest.mock import Mock,patch
from support import HAS_RUNTIME
if HAS_RUNTIME:
    import requests
    from studio.vibi import Client,body,split_text,language_code,VibiError


@unittest.skipUnless(HAS_RUNTIME,'Run tests in the documented private test environment.')
class VibiTests(unittest.TestCase):
    def test_provider_bodies(self):
        eleven=body('Hi','vi',{})
        self.assertNotIn('provider',eleven)
        self.assertEqual(eleven['model_id'],'eleven_v3')
        self.assertEqual(eleven['voice_settings'],{'speed':1,'stability':.5,'similarity_boost':.75})
        mini=body('Hi','vi',{'provider':'minimax','pitch':-2,'volume':.7})
        self.assertEqual(mini['language_code'],'Vietnamese')
        self.assertEqual(mini['voice_settings'],{'speed':1,'pitch':-2,'vol':.7})
        self.assertEqual(mini['model_id'],'speech-2.8-hd')
        cap=body('Hi','en',{'provider':'capcut','transcript':True})
        self.assertNotIn('model_id',cap)
        self.assertEqual(cap['provider'],'capcut')
        self.assertEqual(cap['voice_settings'],{'speed':1,'pitch':0})
        self.assertTrue(cap['export_transcript'])

    def test_ranges_and_languages(self):
        self.assertEqual(language_code('elevenlabs','vi-VN'),'vi')
        self.assertEqual(language_code('minimax','zh-CN'),'Chinese (Mandarin)')
        self.assertEqual(language_code('minimax','Japanese'),'Japanese')
        for options in ({'speed':float('nan')},{'speed':2},{'pitch':20,'provider':'minimax'},{'provider':'bad'}):
            with self.assertRaises(VibiError):body('Hi','vi',options)

    def test_split_including_unpunctuated_and_long_sentence(self):
        for text in ('word '*3000,'x'*9000,('Hello world. '*600)):
            chunks=split_text(text)
            self.assertTrue(all(0<len(c)<=3500 for c in chunks))
            self.assertEqual(''.join(text.split()),''.join(''.join(chunks).split()))
        self.assertEqual(split_text('  Xin chào!  '),['Xin chào!'])
        self.assertEqual(split_text('   '),[])

    def test_http_headers_and_safe_errors(self):
        session=Mock()
        session.request.return_value=Mock(status_code=200,json=lambda:{'credits':12})
        client=Client('SECRET',session=session,fake=False)
        self.assertEqual(client.account()['credits'],12)
        self.assertEqual(session.request.call_args.kwargs['headers']['xi-api-key'],'SECRET')
        session.request.return_value=Mock(status_code=401)
        with self.assertRaisesRegex(VibiError,'invalid or expired'):client.account()
        session.request.side_effect=requests.RequestException('SECRET https://signed.example')
        with self.assertRaises(VibiError) as caught:client.account()
        self.assertNotIn('SECRET',str(caught.exception))
        self.assertNotIn('signed',str(caught.exception))

    def test_poll_completed_failed_cancel_and_timeout(self):
        client=Client(fake=False)
        client.request=Mock(side_effect=[{'status':'pending'},{'status':'completed','result':{'audio_url':'x'}}])
        progress=Mock()
        self.assertEqual(client.wait('id',progress,lambda:False,interval=0),{'audio_url':'x'})
        self.assertEqual(progress.call_count,2)
        client.request=Mock(return_value={'status':'failed','error':'SECRET'})
        with self.assertRaisesRegex(VibiError,'could not complete'):client.wait('id',progress,lambda:False)
        with self.assertRaisesRegex(VibiError,'cancelled'):client.wait('id',progress,lambda:True)
        with self.assertRaisesRegex(VibiError,'timed out'):client.wait('id',progress,lambda:False,timeout=0)

    def test_voice_endpoints_and_page_bases(self):
        client=Client('key',fake=False)
        client.request=Mock(return_value={'voices':[{'voice_id':'1','name':'Demo','provider':'elevenlabs'}],
                                           'has_more':True})
        client.voices('elevenlabs-shared',page=2,size=999,language='vi')
        query=client.request.call_args.kwargs['params']
        self.assertEqual(query['page'],1);self.assertEqual(query['page_size'],100)
        self.assertEqual(query['required_languages'],'vi')
        client.voices('community',page=3,size=30)
        self.assertEqual(client.request.call_args.kwargs['params']['offset'],60)
        client.request=Mock(return_value={'voice_list':[{'voice_id':'m','voice_name':'Mini','sample_audio':'https://audio'}]})
        result=client.voices('minimax-system',language='vi')
        self.assertEqual(result['voices'][0]['preview'],'https://audio')
        self.assertEqual(client.request.call_args.kwargs['params']['language'],'Vietnamese')

    def test_fake_has_no_network(self):
        client=Client(fake=True)
        client.request=Mock(side_effect=AssertionError('Network forbidden'))
        self.assertEqual(client.account()['credits'],100000)
        self.assertEqual(len(client.voices()['voices']),30)

    def test_download_has_no_api_headers_and_cleans_failed_files(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'audio.mp3'
            response=Mock()
            response.iter_content.return_value=[b'audio']
            manager=Mock();manager.__enter__=Mock(return_value=response);manager.__exit__=Mock(return_value=False)
            with patch('requests.get',return_value=manager) as get:
                Client('SECRET',fake=False).download('https://cdn.example/audio',target)
                self.assertEqual(target.read_bytes(),b'audio')
                self.assertNotIn('headers',get.call_args.kwargs)
                with self.assertRaises(VibiError):
                    Client('SECRET',fake=False).download('https://cdn.example/audio',target,cancelled=lambda:True)
                self.assertFalse(target.exists())
            with self.assertRaises(VibiError):
                Client('SECRET',fake=False).download('http://unsafe.example/audio',target)
