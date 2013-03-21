# WARNING: THIS FILE REFFERS ONLY TO LOCAL SERVICES
import logging

DEBUG = False
ENVIRONMENT = "local"

SERVER_PORT = 5100

SPARQL_ENDPOINT = "http://localhost:8890/sparql-auth"
SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"

DEFAULT_LANG = "pt"

LOG_FILEPATH = '/tmp/brainiak.log'
LOG_LEVEL = logging.DEBUG
LOG_NAME = "brainiak"

URI_PREFIX = "http://semantica.globo.com/"
