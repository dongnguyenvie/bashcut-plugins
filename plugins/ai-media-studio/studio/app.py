"""AI Media Studio phase 2."""
from . import state
from .speech import synthesize
from .vibi import Client, MODELS
from .credits import estimate_tts_credits
from pathlib import Path
import hashlib
PLUGIN_ID="bashcut.ai-media-studio"
PROVIDER_ID=PLUGIN_ID+".vibi"

def button(id,title,**extra):
    return dict(type='button',id=id,title=title,**extra)


def field(id,label,value=None):
    node = dict(type='textField',id=id,label=label)
    if value is not None:
        node['value']=value
    return node


def client(request):
    return Client((request.params.get('options') or {}).get('apiKey',''))


def balance(request):
    account = client(request).account()
    nested = account.get('user') or account.get('data') or account
    return str(nested.get('credit_balance',nested.get('credits','Unknown')))


def show(request,view):
    return request.call('plugins.show-view',{'plugin':PLUGIN_ID,'view':view})


def speak(request,text,takes=1):
    if not text.strip():
        raise ValueError('Write text to speak first.')
    request.render([{'type':'progress','label':'Generating Vibi speech…'}])
    result = request.wait_job(request.call('voice.speak',{'text':text,'takes':int(takes),'provider':PROVIDER_ID,
        'keepTakes':True}))
    paths = [str(t['path']) for t in result.get('takes',[]) if t.get('path')]
    # BashCut moves provider outputs into generated/voiceover; relocate the SRT alongside its project take.
    last = state.read().get('lastTake') or {}
    if paths and last.get('srt') and Path(last['srt']).is_file():
        import shutil
        target = Path(paths[-1]).with_suffix('.srt')
        if Path(last['srt']).resolve()!=target.resolve():
            shutil.copy2(last['srt'],target)
        state.update(lastTake={'audio':paths[-1],'srt':str(target)})
    return result


def view(request):
    values = dict(request.params.get('values') or {})
    view_state = dict(request.params.get('state') or {})
    event = request.params.get('event') or {}
    node = event.get('node')
    if event.get('type') in ('change','submit'):
        values[node]=event.get('value')
    name = request.params.get('view')
    handlers = {'studio':studio_view,'voices':voices_view,'watermark':watermark_view,'build':build_view}
    if name not in handlers:
        raise ValueError('Unknown AI Media Studio view.')
    result = handlers[name](request,view_state,values,event)
    # Input state only contains visible non-secret fields, never the options object.
    return result


def studio_view(request,view_state,values,event):
    node = event.get('node')
    if node=='credits':
        view_state['credits']=balance(request)
    elif node in ('voices','build','watermark'):
        show(request,node)
    elif node=='speak':
        result = speak(request,str(values.get('text','')),takes=1)
        view_state['takes']=[{'path':t['path']} for t in result.get('takes',[]) if t.get('path')]
        view_state['message']='Speech ready.'
    elif node=='captions':
        last = state.read().get('lastTake') or {}
        if not last.get('srt') or not Path(last['srt']).is_file():
            raise ValueError('Generate a take with Request SRT transcript enabled first.')
        current = request.call('timeline.get')
        request.call('captions.import',{'text':Path(last['srt']).read_text(encoding='utf-8-sig'),
                                       'baseRev':current['rev'],'replace':False})
        view_state['message']='Captions imported.'
    options = request.params.get('options') or {}
    selected = state.read().get('selectedVoice') or {}
    provider = selected.get('provider') or options.get('provider','elevenlabs')
    voice = selected.get('name') or options.get('voice') or 'Choose in Voices'
    model = options.get('model',MODELS[provider][0])
    if model not in MODELS[provider]:
        model=MODELS[provider][0]
    text = str(values.get('text') or '')
    estimate = estimate_tts_credits(text,provider,model)
    if options.get('transcript'):
        estimate=int(estimate*1.15+.999)
    body=[{'type':'keyValue','items':[{'key':'Credits','value':view_state.get('credits','Refresh to check')},
           {'key':'Voice','value':str(voice)},{'key':'Provider','value':provider}]},
          button('credits','Refresh balance'),button('voices','Browse voices'),
          {'type':'textArea','id':'text','label':'Voiceover text','height':120},
          {'type':'text','text':f'{len(text)} characters · about {estimate} credits · 1 paid take','style':'caption'},
          button('speak','Generate voiceover',style='primary'),button('captions','Import last SRT captions'),
          {'type':'divider'},button('build','Build timeline from scenes…'),
          {'type':'text','text':'Select project media and use Remove watermark from its context menu.','style':'secondary'}]
    if view_state.get('message'):
        body.append({'type':'text','text':view_state['message']})
    for i,take in enumerate(view_state.get('takes',[])[:3]):
        body.append({'type':'audio','path':take['path'],'title':f'Play take {i+1}'})
    if client(request).fake:
        body.insert(0,{'type':'badge','text':'DEMO · fake Vibi, no credits spent','color':'orange'})
    return {'title':'Studio','body':body,'state':view_state}


def voices_view(request,view_state,values,event):
    node = event.get('node')
    source = str(values.get('source',view_state.get('source','community')))
    page = int(view_state.get('page',1))
    if node in ('source','search','gender','language'):
        page=1
    elif node=='next':
        page+=1
    elif node=='previous':
        page=max(1,page-1)
    if node in ('refresh','next','previous','source','search','gender','language'):
        request.render([{'type':'progress','label':'Loading Vibi voices…'}])
        result=client(request).voices(source,page=page,search=str(values.get('search','')),
            gender=str(values.get('gender','all')),language=str(values.get('language','all')))
        view_state.update(voices=result['voices'],hasMore=result['hasMore'],page=page,source=source)
    elif node=='voices' and event.get('type')=='action':
        item = event['value'].get('item')
        action = event['value'].get('action')
        voice=next((v for v in view_state.get('voices',[]) if v['id']==item),None)
        if not voice:
            raise ValueError('Refresh the voice list before choosing this row.')
        if action=='use':
            state.update(selectedVoice={k:voice[k] for k in ('id','name','provider','language')})
            view_state['message']='Default voice: '+voice['name']+'.'
        elif action=='preview':
            if not voice.get('preview'):
                raise ValueError('This voice has no preview sample.')
            path=state.folder(True)/('voice-'+hashlib.sha256(voice['preview'].encode()).hexdigest()+'.mp3')
            if not path.exists():
                client(request).download(voice['preview'],path,request.cancelled)
            view_state['preview']=str(path)
        elif action=='favorite':
            favorites=state.read().get('favorites') or []
            key=voice['provider']+':'+voice['id']
            favorites=[f for f in favorites if f!=key] if key in favorites else favorites+[key]
            state.update(favorites=favorites[:500])
    favorites=set(state.read().get('favorites') or [])
    items=[]
    for v in view_state.get('voices',[])[:100]:
        items.append({'id':v['id'],'title':v['name'],
            'subtitle':v['provider']+' · '+v['language'],
            'badge':'★' if v['provider']+':'+v['id'] in favorites else '',
            'actions':[{'id':'use','title':'Use'},{'id':'preview','title':'Preview'},
                       {'id':'favorite','title':'Favorite'}]})
    body=[{'type':'picker','id':'source','label':'Voice library','value':source,
           'options':['community','elevenlabs-default','elevenlabs-shared','minimax-system','minimax-cloned','capcut']},
          dict(field('search','Search voices'),search=True),
          {'type':'picker','id':'gender','label':'Gender','options':['all','male','female']},
          {'type':'picker','id':'language','label':'Language','options':['all','vi','en','zh','ja','ko','fr','de','es','pt','id','th']},
          button('refresh','Load voices'),{'type':'list','id':'voices','items':items,'empty':'Click Load voices to browse.'},
          {'type':'row','children':[button('previous','Previous',disabled=page<=1),
                                   button('next','Next',disabled=not view_state.get('hasMore',False))]},
          {'type':'text','text':f'Page {page} · {len(items)} voices','style':'caption'}]
    if view_state.get('message'):
        body.append({'type':'text','text':view_state['message']})
    if view_state.get('preview'):
        body.append({'type':'audio','path':view_state['preview'],'title':'Voice preview'})
    return {'title':'Vibi Voices','body':body,'state':view_state}


def handle(request):
    if request.method=='voice.synthesize':
        return synthesize(request)
    if request.method in ('view.render','view.event'):
        return view(request)
    if request.method!='plugin.action':
        raise ValueError('Unknown AI Media Studio method.')
    action = request.params.get('action','').removeprefix(PLUGIN_ID+'.')
    values = request.params.get('params') or {}
    if action=='voices':
        show(request,'voices');return {'message':'Opened the Vibi voice library.'}
    if action=='credits':
        return {'message':'Vibi balance: '+balance(request)+' credits.'}
    if action=='speak':
        return {'message':'Vibi speech ready.','data':speak(request,str(values.get('text','')),
                takes=values.get('takes',1))}
    if action=='build-timeline':
        show(request,'build');return {'message':'Scene build is added in phase 4.'}
    if action.startswith('clean-'):
        raise ValueError('Watermark tools are added in phase 3.')
    raise ValueError('Unknown AI Media Studio action.')


def watermark_view(request,view_state,values,event):
    return {'title':'Watermark','body':[{'type':'text','text':'This tool is added in the next phase.'}]}

def build_view(request,view_state,values,event):
    return {'title':'Build','body':[{'type':'text','text':'This tool is added in the next phase.'}]}

