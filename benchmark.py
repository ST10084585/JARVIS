"""Read-only process metrics plus a disposable deterministic file workload."""
import argparse
import ctypes
import json
import tempfile
import time
from pathlib import Path
import psutil
from jarvis.workflows import execute

parser=argparse.ArgumentParser();parser.add_argument('pid',type=int);args=parser.parse_args()
process=psutil.Process(args.pid)
start_cpu=process.cpu_times();start_io=process.io_counters();start=time.monotonic();rss=[]
for _ in range(20):rss.append(process.memory_info().rss);time.sleep(1)
elapsed=time.monotonic()-start;end_cpu=process.cpu_times();end_io=process.io_counters()
result={'pid':args.pid,'sample_seconds':round(elapsed,2),'cpu_percent_one_core':round(100*(end_cpu.user+end_cpu.system-start_cpu.user-start_cpu.system)/elapsed,3),'cpu_percent_machine':round(100*(end_cpu.user+end_cpu.system-start_cpu.user-start_cpu.system)/elapsed/psutil.cpu_count(),3),'rss_mb_max':round(max(rss)/1024**2,2),'read_bytes_delta':end_io.read_bytes-start_io.read_bytes,'write_bytes_delta':end_io.write_bytes-start_io.write_bytes}
user32=ctypes.windll.user32
focus=user32.GetForegroundWindow();clipboard=user32.GetClipboardSequenceNumber()
with tempfile.TemporaryDirectory() as temp:
    source=Path(temp)/'input.csv';destination=Path(temp)/'output.csv'
    source.write_text('Name,VIN\n'+' alice ,123\n'*10000,encoding='utf-8')
    start=time.perf_counter()
    output=execute({'schema_version':1,'steps':[{'op':'strip','columns':['Name']},{'op':'upper','columns':['Name']}],'formula_policy':'escape'},source,destination)
    assert 'ALICE' in destination.read_text(encoding='utf-8')
    result['csv_workload']={'rows':output['rows'],'seconds':round(time.perf_counter()-start,3),'foreground_unchanged':focus==user32.GetForegroundWindow(),'clipboard_sequence_unchanged':clipboard==user32.GetClipboardSequenceNumber(),'scope':'direct engine on disposable files while packaged UI idles; no active typing or mouse movement test'}
Path('records/performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
