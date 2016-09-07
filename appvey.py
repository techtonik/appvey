"""
appvey add <url>
"""
import sys
from pprint import pprint as pp

import requests
import tablib

token = open('.bearer', 'rb').read().strip()
auth ={'Authorization': 'Bearer %s' % token}

class API(object):
    '''helper for REST server on top of requests'''
    def __init__(self, apiurl, headers):
	self.apiurl = apiurl
        self.headers = headers

    def get(self, path):
        return requests.get(self.apiurl + path, headers=self.headers).json()

    def post(self, path, data=None):
        return requests.post(self.apiurl + path, headers=self.headers, data=data)

api = API('https://ci.appveyor.com/', headers=auth)
#roles = api.get('/api/roles')

projects = api.get('/api/projects')
reponames = tablib.Dataset(projects)

for p in projects:
    print("%-20s %-20s %s" % (p['slug'], p['name'], p['repositoryName']))

if sys.argv[1:]:
    if sys.argv[1] == 'add':
        repo = sys.argv[2]

        # https://www.appveyor.com/docs/api/projects-builds/#add-project
        payload = {
            "repositoryProvider":"git",
            "repositoryName":repo
        }
        res = api.post('/api/projects', data=payload)

        # [ ] if res.status == 200:
        if res.status_code == 200:
            pp(res.json())
    