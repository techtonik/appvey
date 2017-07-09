#!/usr/bin/env python
"""
Kick AppVeyor builds

Automatically creates AppVeyor project if it doesn't exist for
current git repository URL (uses origin), uploads settings from
local appveyor.yml (always) and kicks build.

usage: appvey

"""

__author__ = "anatoly techtonik <techtonik@gmail.com>"
__license__ = "Public Domain"
__version__ = "1"
__url__ = "https://github.com/techtonik/appvey"

import os
import sys
from pprint import pprint as pp

import requests
from shellrun import run_capture
#import tablib

TOKENFILE = '.appveyor_token'

PY3K = sys.version_info >= (3, 0)
if PY3K:
    enter = input
else:
    enter = raw_input

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

def update(project, ymlpath='appveyor.yml'):
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


def auth():
    '''return dict with authentication header'''
    if not os.path.exists('.appveyor_token'):
        print('please enter your AppVeyor API token. you can find it at')
        print('https://ci.appveyor.com/api-token')
        print('it will be cached in .appveyor_token file in current dir')
        token = enter(': ')        
        with open(TOKENFILE, 'wb') as tf:
            tf.write(token.strip())
    token = open(TOKENFILE, 'rb').read().strip()
    return {'Authorization': 'Bearer %s' % token}

def auth_check():
    api = API('https://ci.appveyor.com', auth())
    # https://www.appveyor.com/docs/api/team/#get-roles
    roles = api.get('/api/roles')
    if 'message' in roles and roles['message'] == 'Authorization required':
        return False
    return True

def add(api, repo):
    '''add new project to AppVeyor, return its urlpath'''
    # https://www.appveyor.com/docs/api/projects-builds/#add-project
    payload = {
        "repositoryProvider":"git",
        "repositoryName":repo
    }
    resp = api.post('/api/projects', data=payload)
    if resp.status_code == 200:
        res = resp.json()
        urlpath = '%s/%s' % (res["accountName"], res["slug"])
        print('created project https://ci.appveyor.com/project/' + urlpath)
        return urlpath


def main():
    if not auth_check():
        sys.exit('Authentication Failed. Remove %s and try again.' % TOKENFILE)

    api = API('https://ci.appveyor.com', auth())
    # https://www.appveyor.com/docs/api/projects-builds/#get-projects
    projects = api.get('/api/projects')
    #projdata = tablib.Dataset()
    #projdata.json = projects
    repos = {p['repositoryName']: '%s/%s' % (p['accountName'], p['slug']) for p in projects}

    for p in projects:
        urlpath = '%s/%s' % (p['accountName'], p['slug'])
        print("%-32s %s" % (urlpath, p['repositoryName']))

    # detect repository
    repo = run_capture('git remote get-url origin').output.strip()
    print('detected: %s' % repo)
    if repo not in repos.keys():
        urlpath = add(api, repo)
    else:
        urlpath = repos[repo]

    # update config
    print('updating: %s' % urlpath)
    update(urlpath)

    # kick da build
    build(urlpath)

if __name__ == '__main__':
    main()
