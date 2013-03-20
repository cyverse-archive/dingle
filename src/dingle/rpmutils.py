"""Contains functions for dealing with iPlant's RPMs"""

import operator

def convert_version_element(version_string):
    """Converts 'version_string' into an int if it doesn't contain
    any non-digit characters. Otherwise, returns the original
    string."""
    if version_string.isdigit():
        return int(version_string)
    return version_string

def get_version_list(rpm_filename):
    """Returns the version portion of an iPlant RPM filename as a list
    of integers. This will only work on RPMs that use the RPM version
    convention that we use for the iPlant DE RPMs, namely:
       {name}-#.#.#-##.{arch}.rpm
    The first three digits are the version fields. The last two digits
    are the release/build number."""
    rpm_filename = rpm_filename.strip(".rpm")
    chunks = rpm_filename.split('-')[-2:]
    version_list = chunks[0].split('.')
    version_list.append(chunks[1].split('.')[0])
    return [convert_version_element(v) for v in version_list]

def get_rpm_name(rpm_filename):
    """Returns the name portion of an iPlant RPM filename. As with
    get_version_list(), this will probably only work on RPMs that use
    the RPM naming convention for the DE RPMs."""
    chunks = rpm_filename.split('-')[:-2]
    return "-".join(chunks)

def sort_rpms(rpm_filenames):
    """Returns a sorted list of RPM files based on version. Note that
    ONLY the versions are compared."""
    rpm_map = {}
    for fname in rpm_filenames:
        rpm_map[fname] = get_version_list(fname)
    itemkey = operator.itemgetter(1)
    return [t[0] for t in sorted(rpm_map.iteritems(), key=itemkey)]

def rpm_name_version_map(rpm_filenames):
    """Returns a map where the keys are the rpm names and the value
    is a list of version lists"""
    rpm_map = {}
    for fname in rpm_filenames:
        rpm_name = get_rpm_name(fname)
        rpm_version = get_version_list(fname)
        if not rpm_map.has_key(rpm_name):
            rpm_map[rpm_name] = []
        rpm_map[rpm_name].append(rpm_version)
    return rpm_map

def has_later_rpm(rpm_filename, potential_later_rpms):
    """Returns True if the rpm_map created with potential_later_rpms
    (as returned by rpm_name_verison_map()) contains a version number
    greater than the one in the rpm filename, 'rpm_filename'."""
    retval = False
    rpm_map = rpm_name_version_map(potential_later_rpms)
    rpm_name = get_rpm_name(rpm_filename)
    rpm_version = get_version_list(rpm_filename)

    if not rpm_map.has_key(rpm_name):
        return retval

    for version_list in rpm_map[rpm_name]:
        if version_list > rpm_version:
            retval = True

    return retval

def latest_rpms(rpm_filenames):
    """Returns a list of RPM filenames representing only the latest
    versions of the rpms in the list. RPMs in the list that is returned
    are sorted by filename."""
    rpm_map = {}

    for fname in rpm_filenames:
        rpm_name = get_rpm_name(fname)
        if not rpm_map.has_key(rpm_name):
            rpm_map[rpm_name] = []
        rpm_map[rpm_name].append(fname)

    for key, val in rpm_map.items():
        rpm_map[key] = sort_rpms(val)[-1]

    return sorted(rpm_map.values())


