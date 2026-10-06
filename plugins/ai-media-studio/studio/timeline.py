import json,hashlib
from pathlib import Path
from . import state
def fingerprint(paths):
    result = []
    for path in paths:
        path = Path(path).resolve()
        stat = path.stat()
        result.append([str(path), stat.st_size, stat.st_mtime_ns])
    return hashlib.sha256(json.dumps(result).encode()).hexdigest()


def project_root(request):
    project = (request.params.get('context') or {}).get('project') or {}
    if not project.get('root'):
        raise ValueError('Open a saved BashCut project first.')
    return str(Path(project['root']).resolve())


