from __future__ import annotations
import socket, subprocess, sys, webbrowser, time

def free_port(start=8000):
    for p in range(start,start+100):
        with socket.socket() as s:
            try:s.bind(('127.0.0.1',p));return p
            except OSError:pass
    raise RuntimeError('No free port')
p=free_port(); url=f'http://127.0.0.1:{p}'; print(f'Irvine Atlas: {url}')
proc=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(p)])
time.sleep(1.2); webbrowser.open(url)
try: proc.wait()
except KeyboardInterrupt: proc.terminate()
