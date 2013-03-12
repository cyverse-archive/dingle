"""Contains the main section and parses command-line arguments."""

import os.path
import sys
import types
import argparse
from dingle import config, workflows, remote
from fabric.api import env

env.use_ssh_config = True

def setup_args():
    """Defines the command-line interface"""
    parser = argparse.ArgumentParser(description='DE Drop Automation')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-n',
        '--new-rpms',
        action='store',
        choices=['dev', 'qa', 'stage', 'prod'],
        help='List new rpms for the specified environment.'
    )
    group.add_argument(
        '-m',
        '--merge',
        action='store',
        choices=['prereqs', 'repos'],
        help="Set of repos to merge and tag. Requires --tag."
    )
    group.add_argument(
        '-u',
        '--update-yum-repo',
        action='store',
        choices=['dev', 'qa', 'stage', 'prod'],
        help="Yum repo to update with new rpms."
    )
    group.add_argument(
        '-l',
        '--list-fs',
        action='store',
        choices=['dev', 'qa', 'stage', 'prod'],
        help="Directory to list. Prints off only RPMS."
    )
    parser.add_argument(
        '-c',
        '--config',
        action='store',
        default='~/.dingle/dingle.json',
        help='Path to the dingle configuration file.'
    )
    parser.add_argument(
        '-t',
        '--tag',
        action='store',
        help='Tag to apply to a merge.'
    )
    return parser

def _err_exit(error_msg):
    """Prints off an error message to stderr and exits."""
    sys.stderr.write(error_msg + "\n")
    sys.exit(-1)

def parse_arguments(parser):
    """Parses the command-line with the specified parser and validates
    the options passed in. Returns the object containing the
    settings."""
    settings = parser.parse_args()

    if not os.path.exists(settings.config):
        _err_exit("--config setting '%s' does not exist." % settings.config)

    if settings.merge and not settings.tag:
        _err_exit("--merge require --tag to be set.")

    return settings

def _validate_keys(cfg, cfg_path, keys):
    """Validates the keys in 'cfg'."""
    missing_cfgs = cfg.missing_keys(keys)
    if missing_cfgs:
        err_str = "%s is missing the following settings:" % cfg_path
        for missing_cfg in missing_cfgs:
            err_str = err_str + "\t%s\n" % missing_cfg
        _err_exit(err_str)

def _validate_types(cfg, cfg_path, typemap):
    """Validates the types of the values in 'cfg'"""
    err_tmpl = "%s is of type %s and should be of type %s in %s.\n"
    err_str = ""
    for cfg_key, cfg_type in typemap.iteritems():
        if not type(cfg.get(cfg_key)) is cfg_type:
            err_str = err_str + err_tmpl % \
                (cfg_key, type(cfg.get(cfg_key)), cfg_type, cfg_path)
    if err_str:
        _err_exit(err_str)

def _validate_config(cfg, cfg_path):
    """Validates the already parsed config file 'cfg'."""
    required_configs = {
        "staging_dir" : types.UnicodeType,
        "yum_repo_host" : types.UnicodeType,
        "yum_dev_dir" : types.UnicodeType,
        "yum_qa_dir" : types.UnicodeType,
        "yum_stage_dir" : types.UnicodeType,
        "yum_prod_dir" : types.UnicodeType,
        "rpm_names" : types.ListType,
        "prereq_repos" : types.ListType,
        "list_of_repos" : types.ListType
    }
    _validate_keys(cfg, cfg_path, required_configs.keys())
    _validate_types(cfg, cfg_path, required_configs)

def _handle_new_rpms(settings):
    """Handles the --new-rpms option."""
    env = settings.new_rpms
    rpms = None

    if env == 'dev':
        rpms = workflows.latest_dev_rpms()
    elif env == 'qa':
        rpms = workflows.latest_new_qa_rpms()
    elif env == 'stage':
        rpms = workflows.latest_new_stage_rpms()
    else:
        rpms = workflows.latest_new_prod_rpms()

    print "-- RPMs for the %s environment:" % env
    if rpms:
        for rpm in rpms:
            print rpm

def _handle_merge(cfg, settings):
    """Handles the --merge option."""
    repo_type = settings.merge

    if repo_type == 'prereqs':
        workflows.merge_and_tag_prereqs(settings.tag, cfg)
    else:
        workflows.merge_and_tag_repos(settings.tag, cfg)

def _handle_update_yum_repo(cfg, settings):
    """Handles the --update-yum-repo option."""
    repo = settings.update_yum_repo

    if repo == 'dev':
        workflows.update_dev_repo(cfg)
    elif repo == 'qa':
        workflows.update_qa_repo(cfg)
    elif repo == 'stage':
        workflows.update_stage_repo(cfg)
    else:
        workflows.update_prod_repo(cfg)

def _handle_list_fs(settings):
    """Handles the --list-fs option."""
    dirname = settings.list_fs
    rpms = None

    if settings.list_fs == 'dev':
        rpms = remote.dev_fs_rpms()
    elif settings.list_fs == 'qa':
        rpms = remote.qa_fs_rpms()
    elif settings.list_fs == 'stage':
        rpms = remote.stage_fs_rpms()
    else:
        rpms = remote.prod_fs_rpms()

    print "-- RPM listing for the %s directory." % dirname
    for rpm in sorted(rpms):
        print rpm

def execute():
    """The main execution flow of Dingle. Parses the config and calls
    out to workflow."""
    parser = setup_args()
    settings = parse_arguments(parser)
    cfg = config.DingleConfig.configure(settings.config)
    _validate_config(cfg, settings.config)

    if settings.new_rpms:
        _handle_new_rpms(settings)
    elif settings.merge:
        _handle_merge(cfg, settings)
    elif settings.update_yum_repo:
        _handle_update_yum_repo(cfg, settings)
    else:
        _handle_list_fs(settings)

if __name__ == "__main__":
    execute()




