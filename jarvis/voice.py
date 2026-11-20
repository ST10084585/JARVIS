"""On-demand local speech; no devices or models opened at import time."""
import json
import queue
import threading
import time
import wave
from pathlib import Path


class SpeechService:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self._stop = threading.Event()
        self._lock = threading.Lock()

    def devices(self):
        import sounddevice as sd
        return [dict(d, index=i) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0]

    def _model(self):
        if not (self.model_path / 'am' / 'final.mdl').is_file():
            raise FileNotFoundError(f'Vosk speech model unavailable: {self.model_path}')
        from vosk import Model
        return Model(str(self.model_path))

    def stop(self):
        self._stop.set()

    def listen(self, cancel, seconds=12, device=None):
        if cancel.is_set():
            return ''
        if not 0 < seconds <= 30:
            raise ValueError('Recording duration must be between 0 and 30 seconds')
        with self._lock:
            self._stop.clear()
            model = self._model()
            import sounddevice as sd
            from vosk import KaldiRecognizer
            rec = KaldiRecognizer(model, 16000)
            chunks = queue.Queue(maxsize=64)
            words = []
            def callback(data, frames, timing, status):
                try:
                    chunks.put_nowait(bytes(data))
                except queue.Full:
                    pass
            try:
                with sd.RawInputStream(samplerate=16000, blocksize=1600, device=device,
                                       dtype='int16', channels=1, callback=callback):
                    deadline = time.monotonic() + seconds
                    while time.monotonic() < deadline and not cancel.is_set() and not self._stop.is_set():
                        try:
                            data = chunks.get(timeout=.1)
                        except queue.Empty:
                            continue
                        if rec.AcceptWaveform(data):
                            words.append(json.loads(rec.Result()).get('text', ''))
                if cancel.is_set() or self._stop.is_set():
                    return ''
                words.append(json.loads(rec.FinalResult()).get('text', ''))
                return ' '.join(filter(None, words))
            finally:
                del rec, model

    def transcribe_wav(self, path):
        model = self._model()
        from vosk import KaldiRecognizer
        try:
            with wave.open(str(path), 'rb') as wav:
                if wav.getnchannels() != 1 or wav.getsampwidth() != 2 or wav.getcomptype() != 'NONE':
                    raise ValueError('Speech WAV must be mono 16-bit uncompressed PCM')
                if wav.getnframes() / wav.getframerate() > 120:
                    raise ValueError('Speech WAV exceeds 120 seconds')
                rec = KaldiRecognizer(model, wav.getframerate())
                words = []
                while data := wav.readframes(4000):
                    if rec.AcceptWaveform(data):
                        words.append(json.loads(rec.Result()).get('text', ''))
                words.append(json.loads(rec.FinalResult()).get('text', ''))
                return ' '.join(filter(None, words))
        finally:
            del model

    def speak(self, text, cancel=None):
        if cancel is not None and cancel.is_set():
            return
        with self._lock:
            self._stop.clear()
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            voice = None
            try:
                voice = win32com.client.Dispatch('SAPI.SpVoice')
                # Async plus XML-disabled: arbitrary assistant text is plain speech.
                voice.Speak(str(text)[:20000], 1 | 16)
                while not voice.WaitUntilDone(50):
                    if self._stop.is_set() or (cancel is not None and cancel.is_set()):
                        voice.Speak('', 2)
                        break
                    pythoncom.PumpWaitingMessages()
            finally:
                voice = None
                pythoncom.CoUninitialize()
