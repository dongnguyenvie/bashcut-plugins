def handle(request):
    if request.method in ('view.render','view.event'):
        return {'title':request.params.get('view','Studio').title(),'body':[],'state':{}}
    raise ValueError('This feature is implemented in the following phases.')
