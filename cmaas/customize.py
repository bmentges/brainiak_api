import requests
import argparse
import base64
import sys


CREDENTIALS = {
    "dev": {
        "client_id": "U6fvLX9xb9gjJm15/h33eA==",
        "client_secret": "FcmspQN5uiWfMK2FpPzZgg==",
        "repos": "http://repos.backstage.dev.globoi.com/admin/customization_mappings/brainiak.semantica.dev.globoi.com",
        "accounts": "http://accounts.backstage.dev.globoi.com/token"
    },
    "qa1": {
        "client_id": "BRrZvsLcvoYrMu+5GYl6ag==",
        "client_secret": "okFR7CifaCSkwFDQDLxm8Q==",
        "repos": "http://repos.backstage.qa01.globoi.com/admin/customization_mappings/brainiak.semantica.qa01.globoi.com",
        "accounts": "http://accounts.backstage.qa01.globoi.com/token"
    }
}


def renew_token(env, credentials):
    config = credentials[env]
    token = base64.encodestring("{0}:{1}".format(config['client_id'], config['client_secret'])).strip()
    headers = {"Authorization": "Basic {0}".format(token)}
    response = requests.post(config['accounts'], headers=headers, data={'grant_type': 'client_credentials'})
    return response


def customize(env, credentials, token):
    config = credentials[env]
    headers = {"Authorization": "Bearer {0}".format(token), "Content-Type": "application/json"}
    payload = open("customize.json").read()
    response = requests.put(config['repos'], headers=headers,data=payload)
    return response


def get_customization(env, credentials, token):
    config = credentials[env]
    headers = {"Authorization": "Bearer {0}".format(token)}
    response = requests.get(config['repos'], headers=headers)
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Customize all forms in accounts/repos')
    parser.add_argument("env", help="Use one of the following: dev, qa1")
    args = parser.parse_args()
    if args.env not in ('dev', 'qa1'):
        print("Invalid paramenter {0}. Use --help to see valid options.".format(args.env))
        sys.exit(0)

    response_token = renew_token(args.env, CREDENTIALS)
    if response_token.status_code != 200:
        print("Token renewal failed: {0}".format(response_token.text))
        sys.exit(0)

    access_token = response_token.json()['access_token']
    response_customize = customize(args.env, CREDENTIALS, access_token)
    if response_token.status_code != 200:
        print("Customize failed: {0}".format(response_customize.text))
    else:
        print("Success. {0}".format(response_customize.text))

    response_customization = get_customization(args.env, CREDENTIALS, access_token)
    if response_token.status_code != 200:
        print("Retrieval of customization failed: {0}".format(response_customization.text))
    else:
        print(response_customization.text)
