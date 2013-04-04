"""Dingle Web Application"""

import web
import json
from fabric.context_managers import settings
from dingle.workflows import latest_dev_rpms, latest_new_qa_rpms
from dingle.config import DingleConfig

CFG = DingleConfig.configure("./dingle.json")
CFG.validate_config()

URLS = (
    # '/', 'DingleUI',
    '/api/latest-qa-rpms', 'LatestQARPMS',
    '/api/latest-dev-rpms', 'LatestDevRPMS'
)

class LatestDevRPMS(object):
    def GET(self):
        with settings(host_string=CFG.get('yum_repo_host')):
            web.header('Content-Type', 'application/json')
            return json.dumps({"latest_dev_rpms" : latest_dev_rpms()})

class LatestQARPMS(object):
    def GET(self):
        with settings(host_string=CFG.get('yum_repo_host')):
            web.header('Content-Type', 'application/json')
            return json.dumps({"latest_qa_rpms" : latest_new_qa_rpms()})

if __name__ == "__main__":
    APP = web.application(URLS, globals())
    APP.run()