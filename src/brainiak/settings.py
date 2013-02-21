# WARNING: THIS FILE REFFERS ONLY TO LOCAL SERVICES
import logging

DEBUG = True

SERVER_PORT = 5100

SPARQL_ENDPOINT_DATABASE = "virtuoso"
SPARQL_ENDPOINT_FULL_URL = "http://localhost:8890/sparql-auth"

SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"  # Virtuoso-related

LOG_FILEPATH = '/tmp/brainiak.log'
LOG_LEVEL = logging.DEBUG
LOG_NAME = "brainiak"

URI_PREFIX = "http://semantica.globo.com"
