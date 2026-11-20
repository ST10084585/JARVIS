import tempfile
import os
import threading
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from jarvis.browser import BrowserSession, WatchLearn, validate_url, recorded_url, _fetch
from jarvis.voice import SpeechService


class IntegrationPolicyTests(unittest.TestCase):
    def test_private_urls_blocked(self):
        for url in ['file:///etc/passwd', 'http://127.0.0.1', 'http://[::1]',
                    'http://169.254.169.254/', 'https://user:secret@example.org']:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_dns_private_and_mixed_blocked(self):
        with patch('socket.getaddrinfo', return_value=[(2, 1, 6, '', ('10.0.0.1', 443))]):
            with self.assertRaises(ValueError):
                validate_url('https://example.org')

    def test_redirect_private_host_blocked_before_connection(self):
        sock = MagicMock()
        response = MagicMock(status=302)
        response.getheader.return_value = 'http://127.0.0.1/private'
        connection = MagicMock()
        connection.getresponse.return_value = response
        def dns(host, *args, **kwargs):
            return [(2, 1, 6, '', ('127.0.0.1' if host == '127.0.0.1' else '93.184.215.14', 80))]
        with patch('socket.getaddrinfo', side_effect=dns), patch('socket.create_connection', return_value=sock) as connect, patch('http.client.HTTPConnection', return_value=connection):
            with self.assertRaises(ValueError):
                _fetch('http://example.org')
            self.assertEqual(connect.call_count, 1)
            self.assertEqual(connect.call_args.args[0][0], '93.184.215.14')

    def test_large_document_blocked_without_reading(self):
        response = MagicMock(status=200)
        response.getheader.side_effect = lambda name, default=None: {'Content-Type': 'text/html', 'Content-Length': '3000000'}.get(name, default)
        connection = MagicMock()
        connection.getresponse.return_value = response
        with patch('socket.getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.215.14', 80))]), patch('socket.create_connection', return_value=MagicMock()), patch('http.client.HTTPConnection', return_value=connection):
            with self.assertRaises(ValueError):
                _fetch('http://example.org')
            response.read1.assert_not_called()

    def test_recorded_urls_exclude_query_fragment_and_token_paths(self):
        self.assertEqual(recorded_url('https://example.org/a?q=secret#token'), 'https://example.org/a')
        self.assertIsNone(recorded_url('https://example.org/reset/token123'))

    def test_recording_requires_consent_and_replay_rejects_click(self):
        with tempfile.TemporaryDirectory() as d:
            watch = WatchLearn(Path(d))
            with self.assertRaises(PermissionError):
                watch.start('https://example.org')
            with self.assertRaises(ValueError):
                BrowserSession(Path(d)).replay([{'action': 'click', 'selector': '#pay'}], approved=True)

    def test_pause_stop_and_delete(self):
        with tempfile.TemporaryDirectory() as d:
            w = WatchLearn(Path(d))
            w._active.set()
            w._record({'action': 'navigate', 'url': 'https://example.org/?token=secret'})
            w.pause()
            w._record({'action': 'navigate', 'url': 'https://example.org/ignored'})
            self.assertEqual(len(w.events()), 1)
            self.assertNotIn('secret', str(w.events()))
            w.stop()
            w._record({'action': 'navigate', 'url': 'https://example.org/late'})
            self.assertEqual(len(w.events()), 1)
            w.delete()
            self.assertEqual(w.events(), [])

    def test_cancel_before_microphone_or_browser(self):
        event = threading.Event()
        event.set()
        self.assertEqual(SpeechService(Path('missing')).listen(event), '')
        with tempfile.TemporaryDirectory() as d, self.assertRaises(InterruptedError):
            BrowserSession(Path(d)).read('https://example.org', event)

    def test_missing_model_clear_error(self):
        with self.assertRaises(FileNotFoundError):
            SpeechService(Path('missing')).transcribe_wav(Path('missing.wav'))

    def test_persistence_and_safe_draft(self):
        with tempfile.TemporaryDirectory() as d:
            w = WatchLearn(Path(d))
            w._active.set()
            w._record({'action': 'navigate', 'url': 'https://example.org/a'})
            w._record({'action': 'click', 'url': 'https://example.org/a', 'tag': 'A', 'password': 'secret'})
            other = WatchLearn(Path(d))
            self.assertEqual(other.events(), w.events())
            draft = other.to_workflow()
            self.assertTrue(draft['requires_review'])
            self.assertEqual(draft['steps'], [{'action': 'navigate', 'url': 'https://example.org/a'}])
            self.assertNotIn('secret', str(other.events()))

    def test_replay_review_required_and_code_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            session = BrowserSession(Path(d))
            with self.assertRaises(PermissionError):
                session.replay([{'action': 'read', 'url': 'https://example.org'}])
            with self.assertRaises(ValueError):
                session.replay([{'action': 'read', 'url': 'https://example.org', 'script': 'evil'}], approved=True)


@unittest.skipUnless(os.environ.get('JARVIS_RUN_BROWSER_TEST') == '1', 'requires installed Playwright Chromium')
class RealBrowserTests(unittest.TestCase):
    def test_real_isolated_rendering_with_fixture_fetch(self):
        html = b'<title>Local fixture</title><body><h1>Expected content</h1><script>document.body.innerHTML="BAD"</script></body>'
        with tempfile.TemporaryDirectory() as d, patch('jarvis.browser._fetch', return_value=('https://example.org/', 'text/html', html)):
            result = BrowserSession(Path(d)).read('https://example.org/')
            self.assertEqual(result['title'], 'Local fixture')
            self.assertEqual(result['text'], 'Expected content')


if __name__ == '__main__':
    unittest.main()

def test_existing_edge_uses_isolated_channel():
    from jarvis.browser import browser_options
    from pathlib import Path
    import os
    options=browser_options()
    if (Path(os.environ.get('PROGRAMFILES(X86)',''))/'Microsoft/Edge/Application/msedge.exe').is_file():
        assert options=={'channel':'msedge'}
    assert 'user_data_dir' not in options
