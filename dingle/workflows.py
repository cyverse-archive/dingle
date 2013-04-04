"""Drop related functionality."""

from dingle import remote, gitops, rpmutils

def _merge_and_tag(tag, repos, stage_dir):
    """Utility function that performs the clone, merge, and tag ops
    on the provided list of repos. You probably don't want to call this
    directly."""
    retval = []
    for repo in repos:
        retval.append(gitops.git_clone(repo, stage_dir))
        retval.append(gitops.git_merge('dev', 'master', repo, stage_dir))
        retval.append(gitops.git_tag(tag, 'master', repo, stage_dir))
    return retval

def merge_and_tag_prereqs(tag, cfg):
    """Clones, merges, tags, and pushes the prereq repos defined in the
    config file as 'prereq-repos'."""
    prereq_repos = cfg.get('prereq_repos')
    stage_dir = cfg.get('staging_dir')
    return _merge_and_tag(tag, prereq_repos, stage_dir)

def merge_and_tag_repos(tag, cfg):
    """Clones, merges, tags, and pushes the prereq repos defined in the
    config file as 'list-of-repos'."""
    repos = cfg.get('list_of_repos')
    stage_dir = cfg.get('staging_dir')
    return _merge_and_tag(tag, repos, stage_dir)

def latest_new_rpms(lister_func):
    """Returns the latest versions of RPMs in the return value from
    'lister_func'."""
    rpms, _, list_2 = lister_func()
    return [
        rpm for rpm in rpms \
        if not rpmutils.has_later_rpm(rpm, list_2) \
        and not rpmutils.has_later_rpm(rpm, rpms) \
    ]

def latest_dev_rpms():
    """Lists the latest versions of RPMs in the dev yum directory."""
    return rpmutils.latest_rpms(remote.dev_fs_rpms())

def latest_new_qa_rpms():
    """List only the latest rpms in dev directory that aren't in QA"""
    return latest_new_rpms(remote.new_rpms_for_qa)

def latest_new_stage_rpms():
    """List only the latest rpms in the QA directory that aren't in
    stage."""
    return latest_new_rpms(remote.new_rpms_for_stage)

def latest_new_prod_rpms():
    """List only the latest rpms in the stage directory that aren't in
    prod."""
    return latest_new_rpms(remote.new_rpms_for_prod)

def copy_rpms_to_qa(cfg, skips):
    """Copies the latest new rpms to QA"""
    new_rpms = rpmutils.filter_rpms(latest_new_qa_rpms(), skips)
    source = cfg.get('yum_dev_dir')
    dest = cfg.get('yum_qa_dir')
    return remote.copy_remote_files(new_rpms, source, dest)

def copy_rpms_to_stage(cfg, skips):
    """Copies the latest new rpms to stage"""
    new_rpms = rpmutils.filter_rpms(latest_new_stage_rpms(), skips)
    source = cfg.get('yum_qa_dir')
    dest = cfg.get('yum_stage_dir')
    return remote.copy_remote_files(new_rpms, source, dest)

def copy_rpms_to_prod(cfg, skips):
    """Copies the latest new rpms to prod"""
    new_rpms = rpmutils.filter_rpms(latest_new_prod_rpms(), skips)
    source = cfg.get('yum_stage_dir')
    dest = cfg.get('yum_prod_dir')
    return remote.copy_remote_files(new_rpms, source, dest)

def update_dev_repo(cfg):
    """Updates the dev repo"""
    devrepo = cfg.get('yum_dev_dir')
    remote.update_yum_repo(devrepo)
    return remote.chown(devrepo, "buildnanny:www", recurse=True)

def update_qa_repo(cfg, skips):
    """Updates the QA repo"""
    qarepo = cfg.get('yum_qa_dir')
    copy_rpms_to_qa(cfg, skips)
    remote.update_yum_repo(qarepo)
    return remote.chown(qarepo, "root:www", recurse=True)

def update_stage_repo(cfg, skips):
    """Updates the stage repo"""
    stagerepo = cfg.get('yum_stage_dir')
    copy_rpms_to_stage(cfg, skips)
    remote.update_yum_repo(stagerepo)
    return remote.chown(stagerepo, "root:www", recurse=True)

def update_prod_repo(cfg, skips):
    """Updates the prod repo"""
    prodrepo = cfg.get('yum_prod_dir')
    copy_rpms_to_prod(cfg, skips)
    remote.update_yum_repo(prodrepo)
    return remote.chown(prodrepo, "root:www", recurse=True)
