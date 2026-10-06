"""Vibi REST client, adapted from Editor-AI-App, without PyQt or app settings."""
import math
import os
import re
import time
import wave
from pathlib import Path
from urllib.parse import quote, urlparse
import requests

MODELS = {'elevenlabs': ['eleven_v3', 'eleven_multilingual_v2', 'eleven_flash_v2_5', 'eleven_turbo_v2_5'],
          'minimax': ['speech-2.8-hd', 'speech-2.8-turbo', 'speech-2.6-hd', 'speech-2.6-turbo', 'speech-02-hd', 'speech-01-hd'],
          'capcut': ['capcut']}
LANGUAGES = {'vi': 'Vietnamese', 'en': 'English', 'zh': 'Chinese (Mandarin)', 'ja': 'Japanese',
             'ko': 'Korean', 'fr': 'French', 'de': 'German', 'es': 'Spanish', 'pt': 'Portuguese',
             'id': 'Indonesian', 'th': 'Thai'}
SOURCES = {'community': '/v1/community/voices', 'elevenlabs-default': '/v1/default-voices',
           'elevenlabs-shared': '/v1/shared-voices', 'minimax-system': '/v1/minimax/system-voices',
           'minimax-cloned': '/v1/minimax/voices', 'capcut': '/v1/capcut/system-voices'}


class VibiError(ValueError):
    pass


def language_code(provider, language):
    code = str(language or 'vi').replace('_', '-').split('-')[0].lower()
    if provider == 'minimax':
        if language in LANGUAGES.values():
            return language
        if code not in LANGUAGES:
            raise VibiError('Unsupported MiniMax language.')
        return LANGUAGES[code]
    return code


def number(options, key, default, minimum, maximum):
    value = float(options.get(key, default))
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise VibiError(f'{key} must be between {minimum} and {maximum}.')
    return value


def body(text, language, options):
    provider = options.get('provider', 'elevenlabs')
    if provider not in MODELS:
        raise VibiError('Choose ElevenLabs, MiniMax or CapCut.')
    model = options.get('model') or MODELS[provider][0]
    # Host has one enum for all providers: switching provider chooses its default model.
    if model not in MODELS[provider]:
        model = MODELS[provider][0]
    settings = {'speed': number(options, 'speed', 1, .7, 1.5)}
    if provider == 'elevenlabs':
        settings.update(stability=number(options, 'stability', .5, 0, 1),
                        similarity_boost=number(options, 'similarity', .75, 0, 1))
    else:
        settings['pitch'] = int(number(options, 'pitch', 0, -12, 12))
        if provider == 'minimax':
            settings['vol'] = number(options, 'volume', 1, 0, 1)
    payload = {'text': text, 'language_code': language_code(provider, language),
               'voice_settings': settings, 'export_transcript': bool(options.get('transcript', False))}
    if provider != 'capcut':
        payload['model_id'] = model
    if provider != 'elevenlabs':
        payload['provider'] = provider
    return payload


def split_text(text, limit=3500):
    if limit < 1:
        raise ValueError('Chunk limit must be positive.')
    text = text.strip()
    chunks = []
    while len(text) > limit:
        prefix = text[:limit + 1]
        ends = [m.end() for m in re.finditer(r'[.!?\n]\s+', prefix) if m.end() <= limit]
        cut = ends[-1] if ends else prefix.rfind(' ', 0, limit + 1)
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut].strip())
        text = text[cut:].lstrip()
    if text:
        chunks.append(text)
    return chunks


class Client:
    def __init__(self, key='', session=None, fake=None):
        self.key = str(key).strip()
        self.session = session or requests.Session()
        self.fake = os.environ.get('VIBI_FAKE') == '1' if fake is None else fake

    def request(self, method, path, **kwargs):
        if not self.key:
            raise VibiError('Enter your Vibi API key in AI Media Studio options.')
        try:
            response = self.session.request(method, 'https://api.vibi.pro' + path,
                headers={'xi-api-key': self.key, 'Content-Type': 'application/json',
                         'User-Agent': 'BashCut-AI-Media-Studio/0.0.1'},
                timeout=60 if method == 'POST' else 15, allow_redirects=False, **kwargs)
            if response.status_code == 401:
                raise VibiError('Vibi API key is invalid or expired.')
            if response.status_code == 402:
                raise VibiError('Vibi credits are insufficient.')
            if not 200 <= response.status_code < 300:
                raise VibiError(f'Vibi request failed (HTTP {response.status_code}).')
            return response.json()
        except (requests.RequestException, ValueError) as error:
            if isinstance(error, VibiError):
                raise
            # Never echo response bodies, headers, signed URLs or requests exceptions.
            raise VibiError('Could not reach Vibi or read its response.') from None

    def account(self):
        if self.fake:
            return {'credits': 100000, 'fake': True}
        return self.request('GET', '/v1/auth/me')

    def voices(self, source='community', page=1, size=30, search='', gender='all', language='all'):
        if source not in SOURCES:
            raise VibiError('Unknown voice library source.')
        page, size = max(1, int(page)), max(1, min(100, int(size)))
        if self.fake:
            return {'voices': [{'id': f'{source}-{n}', 'name': f'Demo voice {n}',
                                'provider': 'minimax' if source.startswith('minimax') else
                                'capcut' if source == 'capcut' else 'elevenlabs',
                                'language': 'vi', 'preview': ''} for n in range((page-1)*size, page*size)],
                    'hasMore': page < 3}
        query = {'search': search} if search else {}
        if source == 'community':
            query.update(limit=size, offset=(page-1)*size)
        elif source in ('elevenlabs-default', 'minimax-cloned'):
            query['page_size'] = 100
        else:
            query.update(page_size=size, page=page-1 if source == 'elevenlabs-shared' else page)
        if gender != 'all':
            query['gender'] = gender.capitalize() if source in ('minimax-system', 'capcut') else gender.lower()
        if language != 'all':
            query['required_languages' if source == 'elevenlabs-shared' else 'language'] = language_code(
                'minimax' if source.startswith('minimax') else 'elevenlabs', language)
        data = self.request('GET', SOURCES[source], params=query)
        raw = data if isinstance(data, list) else data.get('voices', data.get('voice_list', []))
        total = data.get('total', data.get('total_count')) if isinstance(data, dict) else None
        more = bool(data.get('has_more', data.get('has_more_voices', False))) if isinstance(data, dict) else False
        if source in ('elevenlabs-default', 'minimax-cloned'):
            raw = [v for v in raw if (not search or search.lower() in str(v).lower()) and
                   (gender == 'all' or str(v.get('gender', '')).lower() == gender.lower()) and
                   (language == 'all' or str(v.get('language', '')).lower() in
                    (language.lower(), language_code('minimax', language).lower()))]
            more = page * size < len(raw)
            raw = raw[(page-1)*size:page*size]
        elif total is not None:
            more = page * size < int(total)
        elif not isinstance(data, dict) or 'has_more' not in data and 'has_more_voices' not in data:
            more = len(raw) >= size
        voices = []
        for v in raw[:size]:
            voice_id = v.get('voice_id') or v.get('id')
            if not voice_id:
                continue
            provider = v.get('provider') or ('minimax' if source.startswith('minimax') else
                                            'capcut' if source == 'capcut' else 'elevenlabs')
            voices.append({'id': str(voice_id), 'name': str(v.get('name') or v.get('voice_name') or voice_id),
                           'provider': provider, 'language': str(v.get('language') or 'vi'),
                           'preview': v.get('sample_audio') or v.get('preview_url') or '',
                           'description': str(v.get('description') or '')[:300]})
        return {'voices': voices, 'hasMore': more}

    def wait(self, task_id, progress, cancelled, timeout=180, interval=1.5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if cancelled():
                raise VibiError('Speech generation cancelled.')
            task = self.request('GET', '/v1/history/' + quote(str(task_id), safe=''))
            status = task.get('status')
            progress(str(status or 'Waiting for Vibi'))
            if status == 'completed':
                return task.get('result') or {}
            if status in ('failed', 'cancelled'):
                raise VibiError('Vibi could not complete speech generation.')
            until = min(time.monotonic() + interval, deadline)
            while time.monotonic() < until:
                if cancelled():
                    raise VibiError('Speech generation cancelled.')
                time.sleep(min(.1, max(0, until-time.monotonic())))
        raise VibiError('Vibi speech generation timed out after 180 seconds.')

    def download(self, url, target, cancelled=lambda: False):
        if urlparse(url).scheme != 'https':
            raise VibiError('Vibi returned an invalid download URL.')
        target = Path(target)
        try:
            # Downloads must never carry xi-api-key to a third-party audio CDN.
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()
                with target.open('wb') as output:
                    for chunk in response.iter_content(65536):
                        if cancelled():
                            raise VibiError('Download cancelled.')
                        output.write(chunk)
            return target
        except Exception:
            target.unlink(missing_ok=True)
            raise VibiError('Could not download Vibi media.') from None

    def synthesize_part(self, voice, text, language, options, target, progress, cancelled):
        if cancelled():
            raise VibiError('Speech generation cancelled.')
        if self.fake:
            seconds = max(.25, len(text)/100)
            with wave.open(str(target), 'wb') as output:
                output.setnchannels(1); output.setsampwidth(2); output.setframerate(16000)
                output.writeframes(b'\0\0' * round(seconds * 16000))
            if options.get('transcript'):
                from .speech import timestamp
                target.with_suffix('.srt').write_text(f'1\n00:00:00,000 --> {timestamp(seconds)}\n{text}\n')
            return target
        task = self.request('POST', '/v1/text-to-speech/' + quote(voice, safe=''), json=body(text, language, options))
        if not task.get('id'):
            raise VibiError('Vibi did not return a task ID.')
        result = self.wait(task['id'], progress, cancelled)
        if not result.get('audio_url'):
            raise VibiError('Vibi completed without an audio file.')
        self.download(result['audio_url'], target, cancelled)
        if options.get('transcript'):
            if not result.get('srt_url'):
                raise VibiError('Vibi completed without the requested transcript.')
            self.download(result['srt_url'], target.with_suffix('.srt'), cancelled)
        return target
