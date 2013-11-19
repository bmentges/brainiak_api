from alf.client import Client
import argparse
import sys


CREDENTIALS = {
    "dev": {
        "client_id": "U6fvLX9xb9gjJm15/h33eA==",
        "client_secret": "FcmspQN5uiWfMK2FpPzZgg==",
        "repos": "http://repos.backstage.dev.globoi.com/admin/customization_mappings/brainiak.api.backstage.dev.globoi.com",
        "accounts": "http://accounts.backstage.dev.globoi.com/token"
    },
    "qa1": {
        "client_id": "BRrZvsLcvoYrMu+5GYl6ag==",
        "client_secret": "okFR7CifaCSkwFDQDLxm8Q==",
        "repos": "http://repos.backstage.qa01.globoi.com/admin/customization_mappings/brainiak.api.backstage.qa01.globoi.com",
        "accounts": "http://accounts.backstage.qa01.globoi.com/token"
    }
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Customize all forms in accounts/repos')
    parser.add_argument("env", help="Use one of the following: dev, qa1")
    args = parser.parse_args()
    if args.env not in ('dev', 'qa1'):
        print("Invalid paramenter {0}. Use --help to see valid options.".format(args.env))
        sys.exit(0)

    config = CREDENTIALS[args.env]
    client = Client(token_endpoint=config['accounts'],
                    client_id=config['client_id'],
                    client_secret=config['client_secret'])

    payload = open("customize.json").read()
    response = client.put(config['repos'], headers={"Content-Type": "application/json"}, data=payload)

    if response.status_code not in (200, 204):
        print("Customize failed, error {0}: {1}".format(response.status_code, response.text))
    else:
        print("Success. {0}".format(response.text))

    response = client.get(config['repos'])
    if response.status_code not in (200, 201):
        print("Customize failed, error {0}: {1}".format(response.status_code, response.text))
    else:
        print(response.text)
