"""
appvey add <url> [appveyor.yml]

10:30-13:15
13:30-14:50
"""
import sys
from pprint import pprint as pp

import requests
import tablib

token = open('.bearer', 'rb').read().strip()
auth ={'Authorization': 'Bearer %s' % token}


"""
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

import logging
logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
"""


class API(object):
    '''helper for REST server on top of requests'''
    def __init__(self, apiurl, headers):
	self.apiurl = apiurl
        self.headers = headers

    def get(self, path):
        return requests.get(self.apiurl + path, headers=self.headers).json()

    def post(self, path, data=None, files=None):
        return requests.post(self.apiurl + path, headers=self.headers, data=data, files=files)

    def put(self, path, data=None):
        h = self.headers.copy()
        h['Content-Type'] = 'plain/text'
        return requests.put(self.apiurl + path, headers=h, data=data)

api = API('https://ci.appveyor.com', headers=auth)
#roles = api.get('/api/roles')

projects = api.get('/api/projects')
#projdata = tablib.Dataset()
#projdata.json = projects
reponames = [p['repositoryName'] for p in projects]
slugs = ["%s/%s" % (p['accountName'], p['slug']) for p in projects]

for p in projects:
    print("%s/%-16s %s" % (p['accountName'], p['slug'], p['repositoryName']))


def build(project):
    '''project is string "account/slug"'''
    name, slug = project.split('/')
    payload = {
        'accountName': name,
        'projectSlug': slug,
    }
    resp = api.post('/api/builds', data=payload)
    """pp(resp)
    pp(resp.content)
    pp(resp.raw.read())"""
    print('build started for %s' % (project))
    return resp

def config(project, ymlpath='appveyor.yml'):
    resp = api.put('/api/projects/%s/settings/yaml' % (project), data=open(ymlpath, 'rb').read())
    #resp = api.put('/api/projects/%s/settings/yaml' % (project), data='version: 1.0.{build}\n')
    if resp.status_code == 500:
        # [ ] validate
        print('error 500: most likely appveyor.yml is invalid' % resp.content)
    if resp.status_code != 204:
        print('error: config update returned %s' % resp.status_code)
        return resp
    print('configured %s from %s' % (project, ymlpath))
    return resp
    

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
            if sys.argv[3:]:
                config(path, ymlpath=sys.argv[3])
            
            # def start build
            build(path)

"""
resp = build('techtonik/ruruki')
pp(resp)
pp(resp.json())
"""

# https://ci.appveyor.com/api/buildjobs/l7ltlhj21kkrm7df/log

files = {'file': open('nosetests.xml', 'rb')}
resp = api.post('/api/testresults/xunit/l7ltlhj21kkrm7df', files=files)
print resp
