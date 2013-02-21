# WARNING: THIS FILE REFFERS ONLY TO LOCAL SERVICES
import logging

DEBUG = True

SERVER_PORT = 5100

<<<<<<< HEAD
SPARQL_ENDPOINT = "http://localhost:8890/sparql"
SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"

LOG_FILEPATH = '/tmp/brainiak.log'
LOG_LEVEL = logging.DEBUG
LOG_NAME = "brainiak"
=======
SPARQL_ENDPOINT_DATABASE = "virtuoso"
SPARQL_ENDPOINT_FULL_URL = "http://localhost:8890/sparql-auth"

SPARQL_ENDPOINT_USER = "api-semantica"
SPARQL_ENDPOINT_PASSWORD = "api-semantica"
SPARQL_ENDPOINT_AUTH_MODE = "digest"
SPARQL_ENDPOINT_REALM = "SPARQL"  # Virtuoso-related
>>>>>>> a2a6e6a27aadab4b71110eca189ab98c01b4b989

URI_PREFIX = "http://semantica.globo.com"
