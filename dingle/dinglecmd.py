"""Contains the main section and parses command-line arguments."""

import os.path
import argparse
from dingle import config, workflows, remote, rpmutils
from dingle.utils import err_exit
from fabric.api import env as _env
from fabric.context_managers import settings as _settings

_env.use_ssh_config = True

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
    parser.add_argument(
        '--host',
        action='store',
        required=True,
        help='The host (<user>@<hostname>:<port>) to connect to.'
    )
    parser.add_argument(
        '-s',
        '--skip',
        action='append',
        help='Add an RPM name or RPM filename to a list of files to skip.'
    )
    return parser

def parse_arguments(parser):
    """Parses the command-line with the specified parser and validates
    the options passed in. Returns the object containing the
    settings."""
    settings = parser.parse_args()

    if not os.path.exists(settings.config):
        err_exit("--config setting '%s' does not exist." % settings.config)

    if settings.merge and not settings.tag:
        err_exit("--merge require --tag to be set.")

    return settings

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
        if settings.skip:
            rpms = rpmutils.filter_rpms(rpms, settings.skip)

        for rpm in sorted(rpms):
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
    skips = settings.skip

    if repo == 'dev':
        workflows.update_dev_repo(cfg)
    elif repo == 'qa':
        workflows.update_qa_repo(cfg, skips)
    elif repo == 'stage':
        workflows.update_stage_repo(cfg, skips)
    else:
        workflows.update_prod_repo(cfg, skips)

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

    if settings.skip:
        rpms = rpmutils.filter_rpms(rpms, settings.skip)

    for rpm in sorted(rpms):
        print rpm

def execute():
    """The main execution flow of Dingle. Parses the config and calls
    out to workflow."""
    parser = setup_args()
    settings = parse_arguments(parser)
    cfg = config.DingleConfig.configure(settings.config)
    cfg.validate_config()

    with _settings(host_string=settings.host):
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




