"""
Contains code to run on remote systems. Contains functions for listing,
uploading, and copying RPMs and updating yum repositories.
"""

import os.path
import fabric.operations as ops
from dingle.config import DingleConfig

def split_ls_output(run_output):
    """Separates the output of an 'ls' command (not 'ls -l') into a
    flattened list of entries.

    See stackoverflow for an explanation of the flattening list
    comprehension: http://stackoverflow.com/a/952952
    """
    lines = [l.split() for l in run_output.splitlines()]
    return [item for line in lines for item in line]

def list_fs(fs_dir):
    """Lists the contents of the provided directory"""
    return split_ls_output(ops.run("ls " + fs_dir, quiet=True))

def list_dev_fs():
    """Lists the contents of the dev RPM directory."""
    return list_fs(DingleConfig.config.get('yum_dev_dir'))

def list_qa_fs():
    """Lists the contents of the qa RPM directory."""
    return list_fs(DingleConfig.config.get('yum_qa_dir'))

def list_stage_fs():
    """Lists the contents of the stage RPM directory."""
    return list_fs(DingleConfig.config.get('yum_stage_dir'))

def list_prod_fs():
    """Lists the contents of the prod RPM directory."""
    return list_fs(DingleConfig.config.get('yum_prod_dir'))

def fs_rpms(list_fs_func):
    """Returns the RPM entries from the output of the provided listing
    function."""
    return [rpm for rpm in list_fs_func() if rpm.endswith(".rpm")]

def dev_fs_rpms():
    """Returns the RPM entries for a listing of the dev directory."""
    return fs_rpms(list_dev_fs)

def qa_fs_rpms():
    """Returns the RPM entries for a listing of the qa directory."""
    return fs_rpms(list_qa_fs)

def stage_fs_rpms():
    """Returns the RPM entries for a listing of the stage directory."""
    return fs_rpms(list_stage_fs)

def prod_fs_rpms():
    """Returns the RPM entries for a listing of the prod directory."""
    return fs_rpms(list_prod_fs)

def new_rpms(rpm_func_1, rpm_func_2):
    """Returns a tuple of containing the following:
        * list of rpms that are in the retval of rpm_func_1() but aren't
          int the retval of rpm_func_2().
        * A listing of rpm_func_1()
        * A listing of rpm_func_1()"""
    listing_1 = rpm_func_1()
    listing_2 = rpm_func_2()
    new_list = list(set(listing_1) - set(listing_2))
    return new_list, listing_1, listing_2

def new_rpms_for_qa():
    """Returns a list containing the RPM filenames that are in the dev
    directory but aren't in the qa directory."""
    return new_rpms(dev_fs_rpms, qa_fs_rpms)

def new_rpms_for_stage():
    """Returns a list containing the RPM filenames that are in the qa
    directory but aren't in the stage directory"""
    return new_rpms(qa_fs_rpms, stage_fs_rpms)

def new_rpms_for_prod():
    """Returns a list containing the RPM filenames that are in the stage
    directory but aren't in the prod directory"""
    return new_rpms(stage_fs_rpms, prod_fs_rpms)

def copy_remote_files(flist, rsource, rdest, run_func=ops.sudo):
    """Copies the filenames included in 'flist' from the remote source
    directory 'rsource' into the remote destination directory
    'rdest'. Requires sudo access."""
    cmd_string = ""
    for fname in flist:
        src_fpath = os.path.join(rsource, fname)
        copy_cmd = "cp %(src)s %(dest)s; " % \
                   {"src" : src_fpath, "dest" : rdest}
        cmd_string = cmd_string + copy_cmd
    return [{cmd_string : run_func(cmd_string)}]

def update_yum_repo(repo_path, run_func=ops.sudo):
    """Runs 'createrepo --update' on the path passed in."""
    cmd_str = "createrepo --update " + repo_path
    return [{cmd_str : run_func(cmd_str)}]

def chown(fpath, owner_group, recurse=False, run_func=ops.sudo):
    """Runs 'chown' on a path. owner_group must be in the format that
    the chown command accepts. If recurse is True, then a -R will be
    added to the chown command."""
    cmd_str = "chown "
    if recurse:
        cmd_str = cmd_str + "-R "
    cmd_str = cmd_str + owner_group + " "
    cmd_str = cmd_str + fpath
    return [{cmd_str : run_func(cmd_str)}]

