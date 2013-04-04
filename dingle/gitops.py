"""Implements local git operations needed for the DE backend"""

import os
import os.path
import shutil
import fabric.operations as ops

class GitMergeError(Exception):
    """Exception raised on merge errors."""
    pass

class GitCloneError(Exception):
    """Exception raised on clone errors."""
    pass

def create_local_staging(staging_dir):
    """Creates a local directory at 'staging_dir'. If 'staging_dir'
    already exists, it's first deleted and then created."""
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

def use_staging_dir(staging_dir):
    """Sets up the staging dir and makes it the current working
    directory."""
    if not os.path.exists(staging_dir):
        create_local_staging(staging_dir)

    if not os.getcwd() == staging_dir:
        os.chdir(staging_dir)

def git_clone(repository, staging_dir):
    """Changes the current working directory to the staging directory,
    clones the repository, and changes the current working directory
    back."""
    orig_cwd = os.getcwd()
    try:
        use_staging_dir(staging_dir)
        result = ops.local("git clone " + repository)
        if not result.succeeded:
            raise GitCloneError(repository)
    finally:
        os.chdir(orig_cwd)

def dir_from_repo(repository):
    """Returns the directory name of a repository based on its
    repository URL"""
    return os.path.basename(repository).strip(".git")

def git_merge(frombranch, intobranch, repository, staging_dir):
    """Merges changes from the 'frombranch' from branch into the
    'intobranch' branch and then pushes the result into the remote
    'intobranch' branch if the merge succeeds."""
    orig_cwd = os.getcwd()
    try:
        repodir = dir_from_repo(repository)
        repopath = os.path.join(staging_dir, repodir)
        use_staging_dir(repopath)
        ops.local("git checkout %s" % frombranch)
        ops.local("git pull origin %s" % frombranch)
        ops.local("git checkout %s" % intobranch)
        ops.local("git pull origin %s" % intobranch)
        result = ops.local("git merge %s" % frombranch)
        if not result.succeeded:
            raise GitMergeError(repository)
        ops.local("git push origin %s" % intobranch)
    finally:
        os.chdir(orig_cwd)

def git_tag(tag, branch, repository, staging_dir):
    """Tags the current state of 'branch' in repo 'repository' with
    'tag'. 'repository' should be the repository URL and the repo
    should already be cloned into 'staging_dir'."""
    orig_cwd = os.getcwd()
    try:
        repodir = os.path.join(staging_dir, dir_from_repo(repository))
        use_staging_dir(repodir)
        ops.local("git checkout %s" % branch)
        ops.local("git tag -a '%s' -m '%s'" % (tag, tag))
        ops.local("git push --tags")
    finally:
        os.chdir(orig_cwd)
