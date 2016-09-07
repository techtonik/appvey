"""
appvey add <url> [appveyor.yml]

start: 10:30
end: 13:15
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
        return requests.post(self.apiurl + path, headers=self.headers, data=data).json()

    def put(self, path, data=None):
        return requests.put(self.apiurl + path, headers=self.headers, data=data)

api = API('https://ci.appveyor.com/', headers=auth)
#roles = api.get('/api/roles')

projects = api.get('/api/projects')
#projdata = tablib.Dataset()
#projdata.json = projects
reponames = [p['repositoryName'] for p in projects]
buildurls = ["%s/%s" % (p['accountName'], p['repositoryName']) for p in projects]

for p in projects:
    print("%-20s %-20s %s" % (p['slug'], p['name'], p['repositoryName']))

if sys.argv[1:]:
    if sys.argv[1] == 'add':
        repo = sys.argv[2]
        if repo in reponames:
            sys.exit('error: already added %s' % repo)
       
        # https://www.appveyor.com/docs/api/projects-builds/#add-project
        payload = {
            "repositoryProvider":"git",
            "repositoryName":repo
        }
        resp = api.post('/api/projects', data=payload)
        # [ ] if resp.status == 200:
        if resp.status_code == 200:
            res = resp.json()
            path = '%s/%s' % (res["accountName"], res["slug"])
            print('created https://ci.appveyor.com/project/' + path)

            # def config
            if sys.argv[2:]:
                resp = api.put('/api/projects/%s/settings/yaml' % (path), data=open('appveyor.yml', 'rb').read())
            
            if resp.status_code == 200:
                res = resp.json()

                # def start build
                payload = {
                    'accountName': res["accountName"],
                    'projectSlug': res["slug"],
                }
                resp = api.post('/api/builds', data=payload)
                pp(resp.json())
    

def build(project, name):
    payload = {
        'accountName': 'techtonik',
        'projectSlug': 'ruruki',
        # master
        #'branch': 'master',
    }
    res = api.post('/api/builds', data=payload)
    pp(res.json())
