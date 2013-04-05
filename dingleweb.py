"""Dingle Web Application"""

import web
import json
from fabric.context_managers import settings
import dingle.workflows as wrk
import dingle.remote as remote
from dingle.config import DingleConfig

CFG = DingleConfig.configure("./testdingle.json")
CFG.validate_config()

URLS = (
    # '/', 'DingleUI',
    '/api/rpms/dev/new', 'NewDevRPMS',
    '/api/rpms/qa/new', 'NewQARPMS',
    '/api/rpms/stage/new', 'NewStageRPMS',
    '/api/rpms/prod/new', 'NewProdRPMS',
    '/api/rpms/dev/list', 'ListDevRPMS',
    '/api/rpms/qa/list', 'ListQARPMS',
    '/api/rpms/stage/list', 'ListStageRPMS',
    '/api/rpms/prod/list', 'ListProdRPMS',
    '/api/yum/qa/update', 'QARepoUpdater',
    '/api/yum/stage/update', 'StageRepoUpdater',
    '/api/yum/prod/update', 'ProdRepoUpdater'
)

class NewEndpoint(object):
    def __init__(self):
        self.host = CFG.get('yum_repo_host')
        self.password = CFG.get('yum_repo_password')

    def request(self, key, val_func):
        with settings(host_string=self.host, password=self.password):
            web.header('Content-Type', 'application/json')
            return json.dumps({key : val_func()})

class NewDevRPMS(NewEndpoint):
    def GET(self):
        return self.request("latest_dev_rpms", wrk.latest_dev_rpms)

class NewQARPMS(NewEndpoint):
    def GET(self):
        return self.request("new_qa_rpms", wrk.latest_new_qa_rpms)

class NewStageRPMS(NewEndpoint):
    def GET(self):
        return self.request("new_stage_rpms", wrk.latest_new_stage_rpms)

class NewProdRPMS(NewEndpoint):
    def GET(self):
        return self.request("new_prod_rpms", wrk.latest_new_prod_rpms)

class ListDevRPMS(NewEndpoint):
    def GET(self):
        lister = lambda: sorted(remote.list_dev_fs())
        return self.request("list_dev_rpms", lister)

class ListQARPMS(NewEndpoint):
    def GET(self):
        lister = lambda: sorted(remote.list_qa_fs())
        return self.request("list_qa_rpms", lister)

class ListStageRPMS(NewEndpoint):
    def GET(self):
        lister = lambda: sorted(remote.list_stage_fs())
        return self.request("list_stage_rpms", lister)

class ListProdRPMS(NewEndpoint):
    def GET(self):
        lister = lambda: sorted(remote.list_prod_fs())
        return self.request("list_prod_rpms", lister)

class QARepoUpdater(NewEndpoint):
    def GET(self):
        updater = lambda: wrk.update_qa_repo(CFG, [])
        return self.request("update_qa_repo", updater)

class StageRepoUpdater(NewEndpoint):
    def GET(self):
        updater = lambda: wrk.update_stage_repo(CFG, [])
        return self.request("update_stage_repo", updater)

class ProdRepoUpdater(NewEndpoint):
    def GET(self):
        updater = lambda: wrk.update_prod_repo(CFG, [])
        return self.request("update_prod_repo", updater)

if __name__ == "__main__":
    APP = web.application(URLS, globals())
    APP.run()