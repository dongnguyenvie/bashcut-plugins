from .speech import synthesize
def handle(request):
    if request.method=='voice.synthesize':return synthesize(request)
    if request.method in ('view.render','view.event'):
        return {'title':request.params.get('view','Studio').title(),'body':[],'state':{}}
    raise ValueError('Views and tools are implemented in the following phases.')
