""" ==========================================================
File:        YouTrack.py
Description: Plugin for working with You Track 5, works in Subime Text 3.
Maintainer:  Eldar Amantay <amantay.eldar@gmail.com>
Website:     https://www.steppefox.kz/
==========================================================="""

__version__ = '0.1'

import sublime, sublime_plugin, json

import glob
import os
# import platform
# import sys
import urllib.request
# import os.system
# import http.cookiejar

# import time
from os.path import expanduser, dirname, realpath, isfile, join, exists


# globals
ACTION_FREQUENCY = 2
ST_VERSION = int(sublime.version())
PLUGIN_DIR = dirname(realpath(__file__))
if(os.path.isfile(PLUGIN_DIR+'/YouTrack.local.sublime-settings')):
    SETTINGS = sublime.load_settings("YouTrack.local.sublime-settings")
else:
    SETTINGS = sublime.load_settings("YouTrack.sublime-settings")
HOST = SETTINGS.get('host')

COOKIES = []
PROJECTS_LIST = []
ISSUE_LIST = []
CURRENT_PROJECT = None

def sendRequest(url,data=[]):
    # print(data)
    data = urllib.parse.urlencode(data)
    # data = data.encode('utf-8') # data should be byte
    cookies = ';'.join(COOKIES);
    opener = urllib.request.build_opener()
    opener.addheaders.append(('Cookie',cookies))
    opener.addheaders.append(('Accept', 'application/json'))
    urllib.request.install_opener(opener)
    get_params = ''
    if(len(data)):
        get_params = '?'+data
    url_to_open = HOST+url+get_params

    response = urllib.request.urlopen(url_to_open)
    return json.loads(response.read().decode())

class YoutrackConnectCommand(sublime_plugin.TextCommand):
    global CURRENT_PROJECT

    def run(self, edit):

        if(os.path.isfile(PLUGIN_DIR+'/YouTrack.local.sublime-settings')):
            SETTINGS = sublime.load_settings("YouTrack.local.sublime-settings")
        else:
            SETTINGS = sublime.load_settings("YouTrack.sublime-settings")

        # Login in YouTrack
        values = {'login':SETTINGS.get('login'),'password':SETTINGS.get('pass')}
        data = urllib.parse.urlencode(values)
        data = data.encode('utf-8') # data should be byte
        response = urllib.request.urlopen(SETTINGS.get('host')+'/rest/user/login',data)
        html = response.read()
        headers = response.info()
        # Remember auth cookies
        for i in response.getheaders():
            if i[0]=="Set-Cookie":
                COOKIES.append(i[1])

        res = sendRequest('/rest/project/all',{'verbose':'false'});
        # Clear projects list array to fill it again
        del PROJECTS_LIST[:]
        for row in res:
            PROJECTS_LIST.append(row['shortName'])

        self.view.window().show_quick_panel(PROJECTS_LIST, self.onProjectSelected, sublime.MONOSPACE_FONT)

    def onProjectSelected(self,item):
        CURRENT_PROJECT = PROJECTS_LIST[item]
        res = sendRequest('/rest/issue',{'filter':'for #'+SETTINGS.get('login')+' #'+CURRENT_PROJECT+' State: Open'})
        res_issue_list = res.get('issue')
        print(res_issue_list)
        issues_list = []
        for issue in res_issue_list:
            summary = ''
            estimation = ''
            issue['jsonFields'] = {}
            for field in issue['field']:
                issue['jsonFields'][field['name']] = field['value']
            estimation = issue['jsonFields']['Estimation'][0]+'m.'
            issues_list.append(issue.get('id')+' '+issue['jsonFields']['summary']+' | '+estimation)
        project_data = self.view.window().project_data()
        project_folder = project_data['folders'][0]['path']
        print(os.system('cd '+project_folder+'; ls -lah; touch lol.test'))
        # Show issues list
        sublime.set_timeout(lambda: self.view.window().show_quick_panel(issues_list, self.onIssueSelected, sublime.MONOSPACE_FONT),200)

    def onIssueSelected(self,item):
        sublime.set_timeout(lambda: self.view.window().show_input_panel('Write commit message', 'initial_text', None, None, None),200)

