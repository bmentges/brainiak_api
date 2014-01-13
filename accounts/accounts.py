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
import subprocess
import sys

import requests
from slugify import slugify


HOSTS = {
    "dev": "http://accounts.interno.backstage.dev.globoi.com/",
    "qa01": "http://accounts.interno.backstage.qa01.globoi.com/",
    "prod": "http://accounts.interno.backstage.globoi.com/",
    # TODO
    # "qa"
    # "qa02"
    # "stg"
}


BRAINIAK_CLIENTS = [
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
    return process.stdout.read()


def save_app_roles(environ, app_name, app_id, roles_text):
    filename = "data/{0}/{1}_{2}.json".format(environ, slugify(app_name), app_id)

    with open(filename, "w") as outfile:
        obj = json.loads(roles_text)
        json.dump(obj, outfile, sort_keys=True, indent=4)
        outfile.write('\n')


def try_and_pull(environ):
    msg = u"Your local file(s) changed.\nCheck if this is on purpose and commit them to GIT and to Accounts API before any further steps."
    files_differ = were_local_files_modified(msg)
    if not files_differ:
        response = pull(environ, "*")
        msg = u"Files at Accounts API are different from the local ones.\nMake sure you:\n" \
        "(1) commit the just pulled files to git before making any further changes, or\n" \
        "(2) git reset (checkout --) local files and overwrite permissions at Accounts API pushing them."
        files_differ = were_local_files_modified(msg)
    print(u"Files successfuly pulled from <{0}>.".format(environ))


def pull(environ, clients=["G1 CDA"]):
    host = HOSTS[environ]
    url = "{0}/apps/".format(host)
    response = requests.get(url)
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
        response = requests.get(url)
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


def were_local_files_modified(msg):
    response = run("git status data")
    if "modified" in response:
        print(msg)
        return True
    return False


def push(environ, clients=["G1 CDA"]):
    host = HOSTS[environ]
    roles_filenames = glob.glob("data/{0}/*.json".format(environ))

    for filename in roles_filenames:
        with open(filename) as infile:
            app_roles = json.load(infile)
            app_id = filename.split("_")[-1].split(".json")[-2]

            for role in app_roles:
                role_id = role["id"]
                new_permissions = []

                for permission in role["permissions"]:
                    permission_id = permission.pop("_id")
                    permission_url = permission["target"]

                url = "{0}roles/{2}".format(host, app_id, role_id)
                headers = {"Content-Type": "application/json"}
                role["permissions"] = new_permissions
                response = requests.put(url, data=json.dumps(role), headers=headers)


def try_and_push(environ):
    msg = u"Your permission file(s) changed locally.\nCommit them to GIT before pushing to Accounts API."
    files_differ = were_local_files_modified(msg)
    if files_differ:
        exit()
    else:
        response = pull(environ, "*")
        files_differ = were_local_files_modified("")
        if not files_differ:
            msg = u"Permissions at Accounts API are equal to your local ones."
            print(msg)
        push(environ, "*")

if __name__ == "__main__":
    command, environ = parse_options()

    if command == "pull":
        try_and_pull(environ)
    else:  # "push"
        try_and_push(environ)
