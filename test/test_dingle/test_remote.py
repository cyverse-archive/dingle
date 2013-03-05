"""Runs unit tests for dingle.remote"""
import mock
from dingle import remote

RPMS = [
    "foo.rpm",
    "bar.rpm",
    "baz.rpm",
    "quuz.rpm"
]

NEW_RPMS = [
    "lol.rpm",
    "cat.rpm"
]

PREV_STAGE_RPMS = RPMS + NEW_RPMS

LISTING = [
    "foo",
    "bar",
    "bar",
    "baz",
    "quux"
] + RPMS

remote.list_fs = mock.Mock(return_value=LISTING)

def test_list_dev_fs():
    """Test for list_dev_fs()"""
    assert remote.list_dev_fs() == LISTING

def test_list_qa_fs():
    """Test for list_qa_fs()"""
    assert remote.list_qa_fs() == LISTING

def test_list_stage_fs():
    """Test for list_stage_fs()"""
    assert remote.list_stage_fs() == LISTING

def test_list_prod_fs():
    """Test for list_prod_fs()"""
    assert remote.list_prod_fs() == LISTING

def test_dev_fs_rpms():
    """Test for dev_fs_rpms()"""
    assert remote.dev_fs_rpms() == RPMS

def test_qa_fs_rpms():
    """Test for qa_fs_rpms()"""
    assert remote.qa_fs_rpms() == RPMS

def test_stage_fs_rpms():
    """Test for stage_fs_rpms()"""
    assert remote.stage_fs_rpms() == RPMS

def test_prod_fs_rpms():
    """Test for prod_fs_rpms()"""
    assert remote.prod_fs_rpms() == RPMS

def test_new_rpms_for_qa():
    """Test for new_rpms_for_qa()"""
    old_val = remote.dev_fs_rpms
    remote.dev_fs_rpms = mock.Mock(return_value=PREV_STAGE_RPMS)

    assert remote.new_rpms_for_qa() == NEW_RPMS

    remote.dev_fs_rpms = old_val

def test_new_rpms_for_stage():
    """Test for new_rpms_for_stage()"""
    old_val = remote.qa_fs_rpms
    remote.qa_fs_rpms = mock.Mock(return_value=PREV_STAGE_RPMS)

    assert remote.new_rpms_for_stage() == NEW_RPMS

    remote.qa_fs_rpms = old_val

def test_new_rpms_for_prod():
    """Test for new_rpms_for_prod()"""
    old_val = remote.stage_fs_rpms
    remote.stage_fs_rpms = mock.Mock(return_value=PREV_STAGE_RPMS)

    assert remote.new_rpms_for_prod() == NEW_RPMS

    remote.stage_fs_rpms = old_val

