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

show branches
git log --graph --pretty=oneline --abbrev-commit

"""


def switch_branch(repo_name, branch):

    # read config
    config = helper.read_config()
    if repo_name not in config['git']:
        return {"success": False,
                "error": "config error; no git entry for %s found" % repo_name}

    # path to local directory of the repo
    local_git_path = helper.get_value_from_dict(config, ['git',
                                                         repo_name,
                                                         'local_gitdir'])
    if local_git_path is None:
        return {"success": False,
                "error": "config error; local dir of 'config_contexts' does not exists"}

    # get GIT object
    repo = git.Repo(local_git_path)
    if repo is None:
        return {"success": False,
                "error": "could not get repo %s" % local_git_path}

    # check if there is a branch for this device
    remote_branches = repo.remote().refs
    found_branch = False
    for b in remote_branches:
        if b.name == "origin/%s" % branch:
            print("found branch of device %s" % branch)
            repo.git.checkout(branch)
            found_branch = True

    if not found_branch:
        # there is no branch for this device. Create one
        print("creating new branch %s" % branch)
        new_branch = repo.create_head(branch)
        repo.git.checkout(branch)

    return {'success': True,
            'id': 0,
            'log': "switched to %s/%s" % (repo, branch)}


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


def edit_file(newconfig):

    # init used variables
    content = {}
    name_of_repo = newconfig.get('repo')
    filename = newconfig.get('filename')
    if name_of_repo is None or filename is None:
        return {"success": False,
                "error": "config error; no repo or filename found"}

    # read config
    config = helper.read_config()
    if name_of_repo not in config['git']:
        return {"success": False,
                "error": "config error; no git entry for %s found" % name_of_repo}

    # path to local directory of the repo
    local_git_path = helper.get_value_from_dict(config, ['git',
                                                         name_of_repo,
                                                         'local_gitdir'])
    # check if local path exists. If not raise an error
    if local_git_path is None:
        return {"success": False,
                "error": "config error; local dir of %s does not exists" % name_of_repo}

    # the content may be in a subdir of the repo
    subdir = helper.get_value_from_dict(config, ['git', name_of_repo, 'local_content'])
    if subdir is None:
        subdir = "/"

    if 'subdir' in newconfig:
        subdir += "/%s" % newconfig['subdir']

    # pull: True => do pull before writing context
    pull = newconfig.get('pull')

    # now try to get the GIT object
    repo = git.Repo(local_git_path)
    if repo is not None and pull:
        try:
            repo.remotes.origin.pull()
        except Exception as exc:
            return {'success': False,
                    'error': 'got exception %s' % exc}

    # we need the name of the current branch to push the update later
    current_branch = repo.active_branch.name

    content_filename = "%s/%s/%s" % (local_git_path, subdir, filename)
    # check if file exists
    if os.path.isfile(content_filename):
        comment = "updated %s in %s" % (filename, name_of_repo)
        logmessage = "%s updated in %s/%s" % (filename,
                                              current_branch,
                                              name_of_repo)
        # set id to 2 means updated in sot
        id = 2
        # check if the content of the two dicts must be merged
        if newconfig.get('action') == "merge":
            # merge file on disk and new config
            new_config = newconfig['content']
            with open(content_filename) as f:
                content = yaml.load(f, Loader=SafeLoader)
            content.update(new_config)
        else:
            # no merge; the config in newconfig is the one we use
            content = newconfig['content']
    else:
        # it is a new file, set id to 0
        id = 0
        comment = "%s in %s/%s added to sot" % (filename,
                                                current_branch,
                                                name_of_repo)
        logmessage = "%s in %s/%s added to sot" % (filename,
                                                   current_branch,
                                                   name_of_repo)
        content = newconfig['content']

    # write content to to disk
    with open(content_filename, "w") as filehandler:
        filehandler.write(content)
        filehandler.close()

    # add file to git
    # even the file exists before writing the new config to the local
    # file leads to the situation that the file must be added to our repo
    repo.index.add(content_filename)

    # commit changes
    repo.index.commit(comment)
    # try:
    #     repo.remotes.origin.push(refspec=current_branch)
    # except Exception as exc:
    #     return {'success': False,
    #             'error': 'got exception %s' % exc}

    return {'success': True,
            'id': id,
            'log': logmessage}
