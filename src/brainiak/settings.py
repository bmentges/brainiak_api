import logging


DEBUG = False

REDIS_ENDPOINT = 'localhost'
REDIS_PORT = 6379

TRIPLESTORE_CONFIG_FILEPATH = 'src/brainiak/triplestore.ini'

ELASTICSEARCH_ENDPOINT = 'localhost:9200'

DEFAULT_LANG = "pt"

DEFAULT_URI_EXPANSION = "0"

DEFAULT_PER_PAGE = "10"
DEFAULT_PAGE = "0"

LOG_FILEPATH = '/tmp/brainiak.log'
LOG_NAME = "brainiak"

URI_PREFIX = "http://semantica.globo.com/"

EVENT_BUS_HOST = 'localhost'
EVENT_BUS_PORT = 61613
NOTIFY_BUS = True

DEFAULT_RULESET_URI = "http://semantica.globo.com/ruleset"

CORS_HEADERS = 'Content-Type, Authorization'

GRAPHS_WITHOUT_INSTANCES = ["http://semantica.globo.com/upper/"]

SERVER_PORT = 5100
DEBUG = True
ENABLE_CACHE = False
REDIS_PASSWORD = None
LOG_LEVEL = logging.DEBUG
ES_ANALYZER = "default"

ANNOTATION_PROPERTY_HAS_UNIQUE_VALUE = "base:tem_valor_unico"
