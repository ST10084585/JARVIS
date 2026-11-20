"""Real local inference and prerecorded speech smoke tests; never opens a microphone."""
import json
import tempfile
import time
from pathlib import Path
from jarvis.inference import OllamaClient
from jarvis.voice import SpeechService

result={}
client=OllamaClient()
try:
    result['models']=client.models()
    result['inference']=client.benchmark()
    client.unload()
    with client._session() as session: result['loaded_after_unload']=session.get(client.BASE_URL+'/api/ps',timeout=10).json()
except Exception as e:result['inference_error']=f'{type(e).__name__}: {e}'

try:
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    try:
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'speech.wav'
            speaker=win32com.client.Dispatch('SAPI.SpVoice')
            stream=win32com.client.Dispatch('SAPI.SpFileStream')
            stream.Format.Type=22  # 22.05 kHz, mono, 16-bit PCM
            stream.Open(str(path),3)
            speaker.AudioOutputStream=stream
            phrase='Hello. The computer is ready. Please open the report.'
            speaker.Speak(phrase,16)
            stream.Close();speaker=None;stream=None
            speech=SpeechService(Path('speech-model'))
            start=time.perf_counter()
            text=speech.transcribe_wav(path)
            result['speech']={'input':phrase,'recognized':text,'seconds':round(time.perf_counter()-start,2),'wav_bytes':path.stat().st_size,'microphone_tested':False,'audible_playback_tested':False}
            result['audio_devices']=speech.devices()
    finally:pythoncom.CoUninitialize()
except Exception as e:result['speech_error']=f'{type(e).__name__}: {e}'
Path('records/local-integration.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
