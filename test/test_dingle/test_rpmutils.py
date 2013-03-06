"""Tests for dingle.rpmutils"""
import mock
from dingle import rpmutils

def test_get_version_list():
    """Tests get_version_list()"""
    example = "foo-1.0.0-10.noarch.rpm"
    assert rpmutils.get_version_list(example) == [1, 0, 0, 10]
    assert not rpmutils.get_version_list(example) == ["1", "0", "0", "10"]

def test_get_rpm_name():
    """Tests get_rpm_name()"""
    example = "foo-1.0.0-10.noarch.rpm"
    assert rpmutils.get_rpm_name(example) == "foo"

def test_sort_rpms():
    """Tests sort_rpms()"""
    example = ["foo-1.0.0-10.n.rpm", "foo-1.0.0-9.n.rpm", "foo-1.0.0-8.n.rpm"]
    assert rpmutils.sort_rpms(example) == [
        "foo-1.0.0-8.n.rpm",
        "foo-1.0.0-9.n.rpm",
        "foo-1.0.0-10.n.rpm"
    ]

    example2 = ["foo-1.0.10-1.n.rpm", "foo-1.0.9-1.n.rpm", "foo-1.0.8-1.n.rpm"]
    assert rpmutils.sort_rpms(example2) == [
        "foo-1.0.8-1.n.rpm",
        "foo-1.0.9-1.n.rpm",
        "foo-1.0.10-1.n.rpm"
    ]

    example3 = ["foo-3.0.0-1.n.rpm", "foo-2.0.0-1.n.rpm", "foo-1.0.0-1.n.rpm"]
    assert rpmutils.sort_rpms(example3) == [
        "foo-1.0.0-1.n.rpm",
        "foo-2.0.0-1.n.rpm",
        "foo-3.0.0-1.n.rpm"
    ]
