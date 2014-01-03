from alf.client import Client
import argparse
import sys


CREDENTIALS = {
    "dev": {
        "client_id": "U6fvLX9xb9gjJm15/h33eA==",
        "client_secret": "FcmspQN5uiWfMK2FpPzZgg==",
        "repos": "http://repos.backstage.dev.globoi.com/admin/customization_mappings/brainiak.backstage.dev.globoi.com",
        "accounts": "http://accounts.backstage.dev.globoi.com/token"
    },
    "qa1": {
        "client_id": "BRrZvsLcvoYrMu+5GYl6ag==",
        "client_secret": "okFR7CifaCSkwFDQDLxm8Q==",
        "repos": "http://repos.backstage.qa01.globoi.com/admin/customization_mappings/brainiak.backstage.qa01.globoi.com",
        "accounts": "http://accounts.backstage.qa01.globoi.com/token"
    },
    "stg": {
        "client_id": "g0SfWM9PJFzbKPV8kYiufA==",
        "client_secret": "abKIB/YENYqvVvij3r7G/Q==",
        "repos": "http://repos.backstage.globoi.com/admin/customization_mappings/brainiak.backstage.globoi.com",
        "accounts": "http://accounts.backstage.globoi.com/token"
    },
    "prod": {
        "client_id": "g0SfWM9PJFzbKPV8kYiufA==",
        "client_secret": "abKIB/YENYqvVvij3r7G/Q==",
        "repos": "http://repos.backstage.globoi.com/admin/customization_mappings/brainiak.backstage.globoi.com",
        "accounts": "http://accounts.backstage.globoi.com/token"
    }
}

proxies = {
    "stg": {"http": "http://gateway.backstage.globoi.com"}  #"http://proxy.staging.globoi.com:3128"}
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Customize all forms in accounts/repos')
    parser.add_argument("env", help="Use one of the following: dev, qa1, stg, prod")
    args = parser.parse_args()
    environment = args.env
    if not environment in CREDENTIALS:
        print("Invalid paramenter {0}. Use --help to see valid options.".format(args.env))
        sys.exit(0)

    config = CREDENTIALS[args.env]
    client = Client(token_endpoint=config['accounts'],
                    client_id=config['client_id'],
                    client_secret=config['client_secret'])

    if environment in proxies:
        client.proxies = proxies[environment]

    print("Valid client, authorization OK")

    payload = open("customize.json").read()
    response = client.put(config['repos'], headers={"Content-Type": "application/json"}, data=payload)

    if response.status_code not in (200, 201, 204):
        print("Customize failed, error {0}: {1}".format(response.status_code, response.text))
    else:
        print("Success. {0}".format(response.text))

    response = client.get(config['repos'])
    if response.status_code not in (200, 201):
        print("Customize failed, error {0}: {1}".format(response.status_code, response.text))
    else:
        print(response.text)
