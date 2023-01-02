from ..helper import helper
from pathlib import Path
import git
import os
import yaml
from yaml.loader import SafeLoader


"""
some git tips:

see new files that are not added to git
git ls-files . --exclude-standard --others
git status -u


"""


def get_file(repo, filename, pull=True):
    """
    return content of file
    Args:
        repo: str
        filename: str
        pull: bool

    Returns:
        content of file
    """

    # read config
    config = helper.read_config()
    if repo not in config['git']:
        return {"success": False,
                "error": "config error; unknown repo %s" % repo}

    # path to local directory of the repo
    git_path = helper.get_value_from_dict(config, ['git', repo, 'local_gitdir'])
    if git_path is None:
        return {"success": False,
                "error": "config error; local dir of %s does not exists" % repo}

    # the content may be in a subdir of the repo
    subdir = helper.get_value_from_dict(config, ['git', repo, 'local_content'])
    if subdir is None:
        subdir = "/"

    git_repo = git.Repo(git_path)
    if git_repo is None:
        return {"success": False,
                "error": "could not get repo %s" % repo}

    if git_repo is not None and pull:
        try:
            git_repo.remotes.origin.pull()
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}

    # check if path exists
    local_path = Path("%s/%s/%s" % (git_path,
                                    subdir,
                                    filename))
    if local_path.is_file():
        content = local_path.read_text()
    else:
        return {"success": False,
                "filename": filename,
                "error": "file does not exists (%s)" % local_path}

    return {"success": True,
            "filename": filename,
            "local_apth": local_path,
            "content": content}


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


def set_configcontext(device, newconfig):

    # defaults
    device_config = {}
    # set id to 0 means added to sot
    id = 0
    logmessage = "config context added to sot"

    # read config
    config = helper.read_config()
    if 'config_contexts' not in config['git']:
        return {"success": False,
                "error": "config error; no git entry for config_contexts found"}

    # path to local directory of the repo
    local_git_path = helper.get_value_from_dict(config, ['git',
                                                         'config_contexts',
                                                         'local_gitdir'])
    if local_git_path is None:
        return {"success": False,
                "error": "config error; local dir of 'config_contexts' does not exists"}

    # the content may be in a subdir of the repo
    subdir = helper.get_value_from_dict(config, ['git', 'config_contexts', 'local_content'])
    if subdir is None:
        subdir = "/"

    # pull: True => do pull before writing context
    pull = newconfig.get('pull')

    # get GIT object
    repo = git.Repo(local_git_path)
    if repo is not None and pull:
        try:
            repo.remotes.origin.pull()
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}

    comment = "added %s to config_contexts" % device
    # check if file exists
    newfile = True
    cc_file_name = "%s/%s/devices/%s" % (local_git_path, subdir, device)
    if os.path.isfile(cc_file_name):
        # file exists
        newfile = False
        comment = "updated %s in config_contexts" % device

    if not newfile:
        # set id to 1: updated sot
        id = 1
        logmessage = "config context updated in sot"
        # check if we should overwrite the file
        if newconfig.get('action') == "merge":
            # merge file on disk and new config
            new_config = newconfig['configcontext']
            with open(cc_file_name) as f:
                device_config = yaml.load(f, Loader=SafeLoader)
            device_config.update(new_config)
        else:
            device_config = newconfig['configcontext']
    else:
        device_config = newconfig['configcontext']

    # the device_config is a dict but we need a yaml
    yaml_config_context = yaml.dump(device_config,
                                    allow_unicode=True,
                                    default_flow_style=False)

    # write yaml to to disk
    with open(cc_file_name, "w") as cc_file:
        cc_file.write("---\n")
        cc_file.write(yaml_config_context)
        cc_file.close()

    # add file to git
    # even the file exists before writing the new config to the local
    # file leads to the situation that the file must be added to our repo
    repo.index.add(cc_file_name)

    # commit changes
    repo.index.commit(comment)
    try:
        repo.remotes.origin.push()
    except Exception as exc:
        return {'success': False,
                'error': 'got exception %s' % exc}

    return {'success': True,
            'id': id,
            'log': logmessage}
