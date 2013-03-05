"""
Contains code to run on remote systems. Contains functions for listing,
uploading, and copying RPMs and updating yum repositories.
"""

import os.path
import fabric.operations as ops

BASE_DIR = "/home/vhosts/projects.iplantcollaborative.org/html/rpms/"
DEV_RPMS_DIR = os.path.join(BASE_DIR, "dev/CentOS/5/iplant/x86_64/")
QA_RPMS_DIR = os.path.join(BASE_DIR, "qa/CentOS/5/iplant/x86_64/")
STAGE_RPMS_DIR = os.path.join(BASE_DIR, "stage/CentOS/5/iplant/x86_64/")
PROD_RPMS_DIR = os.path.join(BASE_DIR, "prod/CentOS/5/iplant/x86_64/")

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
    return list_fs(DEV_RPMS_DIR)

def list_qa_fs():
    """Lists the contents of the qa RPM directory."""
    return list_fs(QA_RPMS_DIR)

def list_stage_fs():
    """Lists the contents of the stage RPM directory."""
    return list_fs(STAGE_RPMS_DIR)

def list_prod_fs():
    """Lists the contents of the prod RPM directory."""
    return list_fs(PROD_RPMS_DIR)

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

def new_rpms_for_qa():
    """Returns a list containing the RPM filenames that are in the dev
    directory but aren't in the qa directory."""
    return list(set(dev_fs_rpms()) - set(qa_fs_rpms()))

def new_rpms_for_stage():
    """Returns a list containing the RPM filenames that are in the qa
    directory but aren't in the stage directory"""
    return list(set(qa_fs_rpms()) - set(stage_fs_rpms()))

def new_rpms_for_prod():
    """Returns a list containing the RPM filenames that are in the stage
    directory but aren't in the prod directory"""
    return list(set(stage_fs_rpms()) - set((prod_fs_rpms())))
