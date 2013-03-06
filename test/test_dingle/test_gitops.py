"""Runs unit tests for gitops.py"""

import os
import os.path
import shutil
import mock
import fabric.operations as ops

from dingle import gitops

STAGE_DIR = "test/staging"

def test_create_local_staging():
    """Tests create_local_staging()"""
    gitops.create_local_staging(STAGE_DIR)
    assert os.path.exists(STAGE_DIR)

    testfile = open(os.path.join(STAGE_DIR, "foo.txt"), "w")
    testfile.close()

    gitops.create_local_staging(STAGE_DIR)
    assert not os.path.exists(os.path.join(STAGE_DIR, "foo.txt"))

def test_use_staging_dir():
    """Tests use_staging_dir()"""
    orig_cwd = os.getcwd()
    stage_abspath = os.path.abspath(STAGE_DIR)
    gitops.use_staging_dir(STAGE_DIR)
    assert os.getcwd() == stage_abspath
    os.chdir(orig_cwd)
    shutil.rmtree(STAGE_DIR)

def test_git_clone():
    """Tests git_clone()"""
    repo = "git@github.com:iPlantCollaborativeOpenSource/fake.git"
    orig_cwd = os.getcwd()
    ops.local = mock.Mock(return_value=True)
    gitops.git_clone(repo, STAGE_DIR)
    ops.local.assert_any_call("git clone %s" % repo)
    assert os.getcwd() == orig_cwd

def test_dir_from_repo():
    """Tests dir_from_repo()"""
    repo = "git@github.com:toolong/fake.git"
    assert gitops.dir_from_repo(repo) == "fake"

class FakeReturn(object):
    """Fake return value"""
    def __init__(self, success=True):
        self.succeeded = success

    def ugh(self):
        """fake method"""
        pass

    def asdfasd(self):
        """shut up pylint"""
        pass

def test_git_merge():
    """Tests git_merge()"""
    repo = "git@github.com:toolong/fake.git"
    frombranch = "from"
    intobranch = "into"
    orig_cwd = os.getcwd()
    ops.local = mock.Mock(return_value=FakeReturn())
    gitops.git_merge(frombranch, intobranch, repo, STAGE_DIR)
    ops.local.assert_any_call("git checkout %s" % frombranch)
    ops.local.assert_any_call("git pull origin %s" % frombranch)
    ops.local.assert_any_call("git checkout %s" % intobranch)
    ops.local.assert_any_call("git pull origin %s" % intobranch)
    ops.local.assert_any_call("git merge %s" % frombranch)
    ops.local.assert_any_call("git push origin %s" % intobranch)
    assert os.getcwd() == orig_cwd

def test_git_tag():
    """Tests git_tag()"""
    repo = "git@github.com:toolong/fake.git"
    branch = "from"
    tag = "gat"
    orig_cwd = os.getcwd()
    ops.local = mock.Mock(return_value=FakeReturn())
    gitops.git_tag(tag, branch, repo, STAGE_DIR)
    ops.local.assert_any_call("git checkout %s" % branch)
    ops.local.assert_any_call("git tag -a '%s' -m '%s'" % (tag, tag))
    ops.local.assert_any_call("git push --tags")
    assert os.getcwd() == orig_cwd
