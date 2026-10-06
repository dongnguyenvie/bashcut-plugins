import importlib.util
import json
import os
import select
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FOLDER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(FOLDER))
sys.path.insert(0,str(FOLDER.parents[1]/'scripts'))
HAS_RUNTIME=all(importlib.util.find_spec(n) for n in ('numpy','PIL','requests','imageio_ffmpeg'))


def nodes(body):
    for node in body:
        yield node
        yield from nodes(node.get('children',[]))


class Session:
    def __init__(self, answers=None):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',VIBI_FAKE='1',
            BASHCUT_PLUGIN_CACHE=str(self.root/'cache'),BASHCUT_PLUGIN_DATA=str(self.root/'data'))
        self.process=subprocess.Popen([sys.executable,'-B','-m','studio.protocol','session'],cwd=FOLDER,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=self.env)
        self.calls=[];self.events=[];self.progress=[];self.answers=answers or {}
        self.write({'type':'hello','apiVersion':8,'features':['views','views.audio','views.imageCompare']})
        assert self.read()['type']=='hello'

    def write(self,message):
        self.process.stdin.write(json.dumps(message)+'\n');self.process.stdin.flush()

    def read(self,timeout=20):
        # A thread timeout protects tests from protocol deadlocks without busy polling.
        import threading,queue
        messages=queue.Queue()
        thread=threading.Thread(target=lambda:messages.put(self.process.stdout.readline()),daemon=True)
        thread.start()
        line=messages.get(timeout=timeout)
        if not line:
            raise AssertionError('Plugin exited: '+self.process.stderr.read())
        return json.loads(line)

    def request(self,method,params):
        self.write({'type':'request','id':'r1','apiVersion':8,'method':method,'params':params})
        while True:
            message=self.read()
            kind=message.get('type')
            if kind=='call':
                self.calls.append((message['method'],message['params']))
                answer=self.answers.get(message['method'],{})
                result=answer(message['params']) if callable(answer) else answer
                self.write({'type':'callResult','callId':message['callId'],'result':result})
            elif kind=='event':self.events.append(message['event'])
            elif kind=='progress':self.progress.append(message)
            else:return message

    def view(self,view,state=None,values=None,event=None,context=None):
        params={'view':view,'state':state,'values':values or {},'context':context or {'project':{'root':str(self.root)}},
                'options':{},'locale':'en'}
        if event:params['event']=event
        return self.request('view.event' if event else 'view.render',params)

    def close(self):
        self.write({'type':'shutdown'})
        self.process.wait(timeout=10)
        self.process.stdin.close();self.process.stdout.close();self.process.stderr.close()
        self.temp.cleanup()
