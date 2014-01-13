# coding: utf-8

"""
Accounts overview:

/apps/ [GET]
    all applications which use Accounts to manage their access to APIs

/apps/<id> [GET]
    application info (name, client_id, client_secret, redirect_uris)

/apps/<id>/roles [GET]
    all access permissions of an application (target APIs URL regex and allowed operations)

/roles/ [GET]
    all access permissions of all applications

/roles/<id> [GET] [PUT]
    access permission role of containing a target API URL regex and one allowed operation

"""

import json
import subprocess
import sys

import requests
from slugify import slugify


HOSTS = {
    "dev": "http://accounts.interno.backstage.dev.globoi.com/",
    "qa01": "http://accounts.interno.backstage.qa01.globoi.com/",
    "prod": "http://accounts.interno.backstage.globoi.com/"
}


BRAINIAK_USERS = [
    u"Educação CDA",
    u"Educação CMA",
    u"G1 Dados",
    u"G1 CDA",
    u"G1 CMA",
    u"GloboEsporte CDA",
    u"GloboEsporte CMA"
]


def run(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.stdout.readline().split('\n')[0]


def save_app_roles(environ, app_name, roles_text):
    filename = "data/{0}/{1}.json".format(environ, slugify(app_name))

    with open(filename, "w") as outfile:
        obj = json.loads(roles_text)
        json.dump(obj, outfile, sort_keys=True, indent=4)
        outfile.write('\n')


def pull(environ, brainik_users=["G1 CDA"]):
    host = HOSTS[environ]
    url = "{0}/apps/".format(host)
    response = requests.get(url)
    response_json = response.json()

    try:
        apps_list = response_json["items"]  # new version of Accounts (available in DEV, QA1)
    except TypeError:
        apps_list = response_json  # old version of Accounts (available in PROD)

    if brainik_users == "*":
        brainiak_apps = [app for app in apps_list if app["name"] in BRAINIAK_USERS]
    else:
        brainiak_apps = [app for app in apps_list if app["name"] in brainik_users]

    for app in brainiak_apps:
        app_id = app["id"]
        
        url = "{0}/apps/{1}/roles".format(host, app_id)
        response = requests.get(url)
        app_roles = response.json()

        save_app_roles(environ, app["name"], response.text)

        for role in app_roles:

            for permission in role["permissions"]:
                permission_id = permission["_id"]
                permission_url = permission["target"]


def get_environ():
    msg = "Run:\n   python accounts.py <environ>\nWhere environ in {0}".format(HOSTS.keys())
    if len(sys.argv) == 2:
        environ = sys.argv[-1]
        if not environ in HOSTS.keys():
            print(msg)
            exit()
    else:
        print(msg)
        exit()
    return environ


def did_permissions_change():
    response = run("git st data")
    if "modified" in response:
        print(u"Your local files are different from the server's. Check if this is on purpose and commit them before any change")
        return True
    return False


if __name__ == "__main__":
    environ = get_environ()
    files_differ = did_permissions_change()
    if not files_differ:
        pull(environ, "*")
