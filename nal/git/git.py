from ..config.nal import read_config
from pathlib import Path
import git


def get_file(repo, filename, pull=True):
    # read config
    config = read_config()
    if repo not in config['git']:
        return {"success": False, "reason": "config error; unknown repo %s" % repo}

    path = config['git'][repo]['local']

    # get the local directory
    if repo not in config['git'] or 'local' not in config['git'][repo]:
        return {"success": False, "reason": "config error; local dir of %s does not exists" % repo}

    repo = git.Repo(path)
    if pull:
        repo.remotes.origin.pull()
    if repo is not None and pull:
        try:
            repo.remotes.origin.pull()
        except Exception as exc:
            return {'success': False, 'reason': 'got exception %s' % exc}

    # check if path exists
    local_path = Path("%s/%s" % (path, filename))
    if local_path.is_file():
        content = local_path.read_text()
    else:
        return {"success": False, "filename": filename, "reason": "file does not exists"}

    return {"success": True, "filename": filename, "content": content}


def repo_differs(repo, branch):

    differs = {'differs': False}

    local_diff = [item.a_path for item in repo.index.diff(None)]
    if local_diff:
        differs = True

    repo.remotes.origin.fetch()
    remote_diff = str(repo.git.diff('origin/%s' % branch)).splitlines()
    if remote_diff:
        differs = True

    return differs