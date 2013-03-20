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
    example2 = "iplant-clavin-1.0.0-10.noarch.rpm"
    assert rpmutils.get_rpm_name(example) == "foo"
    assert rpmutils.get_rpm_name(example2) == "iplant-clavin"

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

def test_latest_rpms():
    """Tests latest_rpms()"""
    example = [
        "foo-1.0.0-10.n.rpm",
        "foo-1.0.0-9.n.rpm",
        "foo-1.0.0-8.n.rpm",
        "bar-2.1.0-1.n.rpm",
        "bar-2.2.0-1.n.rpm",
        "bar-2.2.1-1.n.rpm"
    ]
    assert rpmutils.latest_rpms(example) == [
        "bar-2.2.1-1.n.rpm",
        "foo-1.0.0-10.n.rpm"
    ]

def test_rpm_name_version_map():
    """Tests rpm_name_version_map()"""
    example = [
        "foo-1.0.0-10.n.rpm",
        "foo-1.0.0-9.n.rpm",
        "foo-1.0.0-8.n.rpm",
        "bar-2.1.0-1.n.rpm",
        "bar-2.2.0-1.n.rpm",
        "bar-2.2.1-1.n.rpm"
    ]
    retval = rpmutils.rpm_name_version_map(example)
    assert retval["foo"] == [[1, 0, 0, 10], [1, 0, 0, 9], [1, 0, 0, 8]]
    assert retval["bar"] == [[2, 1, 0, 1], [2, 2, 0, 1], [2, 2, 1, 1]]

def test_has_later_rpm():
    """Test has_later_rpm()"""
    example = [
        "foo-1.0.0-10.n.rpm",
        "foo-1.0.0-9.n.rpm",
        "foo-1.0.0-8.n.rpm",
        "bar-2.1.0-1.n.rpm",
        "bar-2.2.0-1.n.rpm",
        "bar-2.2.1-1.n.rpm"
    ]
    assert rpmutils.has_later_rpm("foo-1.0.0-7.n.rpm", example)
    assert not rpmutils.has_later_rpm("foo-1.2.0-1.n.rpm", example)
    assert rpmutils.has_later_rpm("bar-2.0.1-1.n.rpm", example)
    assert not rpmutils.has_later_rpm("bar-2.2.2-1.n.rpm", example)
