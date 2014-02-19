# coding: utf-8

"""
How to use
==========

    (1) Make sure your have no local changes and pull files from Accounts API:
    $ python accounts.py pull dev

    Don't forget to commit to git intentional changes before pushing to Accounts API.

    (2) make local changes, commit to git and then push to Accounts, using:
    $ python accounts.py push dev

Accounts overview
=================

/apps/ [GET]
    all applications which use Accounts to manage their access to APIs

/apps/<id> [GET]
    application info (name, client_id, client_secret, redirect_uris)

/apps/<id>/roles [GET] [PUT]
    all access permissions of an application (target APIs URL regex and allowed operations)

/roles/ [GET]
    all access permissions of all applications

/roles/<id> [GET]
    access permission role of containing a target API URL regex and one allowed operation

"""
import glob
import json
import os
import sys

import requests
from slugify import slugify


HOSTS = {
    "dev": "http://accounts.interno.backstage.dev.globoi.com/",
    "qa": "http://accounts.interno.backstage.qa.globoi.com/",
    "qa01": "http://accounts.interno.backstage.qa01.globoi.com/",
    "qa02": "http://accounts.interno.backstage.qa01.globoi.com/",
    "prod": "http://accounts.interno.backstage.globoi.com/",
    "stg": "http://accounts.interno.backstage.globoi.com/",
}


BRAINIAK_CLIENTS = [
    u"Educação CDA",
    u"Educação CMA",
    u"G1 Dados",
    u"G1 CDA",
    u"G1 CMA",
    u"GloboEsporte CDA",
    u"GloboEsporte CMA",
    u"Home Globo.com",
]


PROXIES = {
    "stg": {"http": "http://proxy.staging.globoi.com:3128"},
    "qa": {"http": "http://proxy.qa.globoi.com:3128"}
}


def save_app_roles(environ, app_name, app_id, roles_text):
    filename = "data/{0}/{1}_{2}.json".format(environ, slugify(app_name), app_id)
    try:
        outfile = open(filename, "w")
    except IOError:
        os.makedirs("data/{0}/".format(environ))
        outfile = open(filename, "w")
    obj = json.loads(roles_text)
    json.dump(obj, outfile, sort_keys=True, indent=4)
    outfile.write('\n')
    outfile.close()


def pull(environ, clients):
    host = HOSTS[environ]
    proxies = PROXIES.get(environ, {})
    url = "{0}apps/".format(host)
    response = requests.get(url, proxies=proxies)
    response_json = response.json()

    try:
        apps_list = response_json["items"]  # new version of Accounts (available in DEV, QA1)
    except TypeError:
        apps_list = response_json  # old version of Accounts (available in PROD)

    if clients == "*":
        brainiak_clients = [app for app in apps_list if app["name"] in BRAINIAK_CLIENTS]
    else:
        brainiak_clients = [app for app in apps_list if app["name"] in clients]

    for app in brainiak_clients:
        app_id = app["id"]

        url = "{0}/apps/{1}/roles".format(host, app_id)
        response = requests.get(url, proxies=proxies)
        app_roles = response.json()

        save_app_roles(environ, app["name"], app_id, response.text)

    return True


def parse_options():
    commands = ["pull", "push"]
    msg = "Run:\n   python accounts.py <command> <environ>\nWhere command in {0} and environ in {1}".format(commands, HOSTS.keys())
    if len(sys.argv) == 3:
        environ = sys.argv[-1]
        command = sys.argv[-2]
        if not environ in HOSTS.keys():
            print(msg)
            exit()
        if not command in commands:
            print(msg)
            exit()
    else:
        print(msg)
        exit()
    return command, environ


def push(environ, clients):
    host = HOSTS[environ]
    proxies = PROXIES.get(environ, {})
    roles_filenames = glob.glob("data/{0}/*.json".format(environ))

    for filename in roles_filenames:
        with open(filename) as infile:
            app_roles = json.load(infile)
            app_id = filename.split("_")[-1].split(".json")[-2]

            for role in app_roles:

                role_id = role["id"]

                for permission in role["permissions"]:
                    permission_id = permission.pop("_id")

                url = "{0}roles/{2}".format(host, app_id, role_id)
                headers = {"Content-Type": "application/json"}
                response = requests.put(url, data=json.dumps(role), headers=headers, proxies=proxies)


if __name__ == "__main__":
    command, environ = parse_options()

    if command == "pull":
        #try_and_pull(environ)
        pull(environ, "*")
    else:  # "push"
        #try_and_push(environ)
        push(environ, "*")
