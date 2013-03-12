"""Contains the main section and parses command-line arguments."""

import os.path
import sys
import types
import argparse
from dingle import config, workflows, remote

def setup_args():
    """Defines the command-line interface"""
    parser = argparse.ArgumentParser(description='DE Drop Automation')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-n',
        '--new-rpms',
        type='string',
        action='store',
        choices=['qa', 'stage', 'prod'],
        help="Lists the new rpms for the specified environment."
    )
    group.add_argument(
        '-m',
        '--merge',
        type='string',
        action='store',
        choices=['prereqs', 'repos'],
        help="Which set of repos to merge and tag. Requires --tag."
    )
    group.add_argument(
        '-u',
        '--update-yum-repo',
        type='string',
        action='store',
        choices=['dev', 'qa', 'stage', 'prod'],
        help="Which yum repo to update with new rpms."
    )
    group.add_argument(
        '-l',
        '--list-fs',
        type='string',
        action='store',
        choices=['dev', 'qa', 'stage', 'prod'],
        help="Which directory to list. Prints off only RPMS."
    )
    parser.add_argument(
        '-c',
        '--config',
        type='string',
        action='store',
        default='~/.dingle/dingle.json',
        help='Path to the dingle configuration file.'
    )
    parser.add_argument(
        '-t',
        '--tag',
        type='string',
        action='store',
        help='The tag to apply to a merge.'
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
    err_tmpl = "%s should be of type %s in %s.\n"
    err_str = ""
    for cfg_key, cfg_type in typemap:
        if not type(cfg.get(cfg_key)) is cfg_type:
            err_str = err_str + err_tmpl % (cfg_key, cfg_type, cfg_path)
    if err_str:
        _err_exit(err_str)

def _validate_config(cfg, cfg_path):
    """Validates the already parsed config file 'cfg'."""
    required_configs = {
        "staging" : types.StringType,
        "yum_repo_host" : types.StringType,
        "yum_dev_dir" : types.StringType,
        "yum_qa_dir" : types.StringType,
        "yum_stage_dir" : types.StringType,
        "yum_prod_dir" : types.StringType,
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
        rpms = remote.list_dev_fs()
    elif settings.list_fs == 'qa':
        rpms = remote.list_qa_fs()
    elif settings.list_fs == 'stage':
        rpms = remote.list_stage_fs()
    else:
        rpms = remote.list_prod_fs()

    print "-- RPM listing for the %s directory." % dirname
    for rpm in rpms:
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




