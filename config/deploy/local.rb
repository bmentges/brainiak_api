role :be,               'cittavld44.globoi.com'
role :filer,            'filer.dev.globoi.com'

# TODO: 
# DEBUG = True
# NOTIFY_BUS = True
# ENABLE_CACHE = True

set :sparql_port,       8890
set :sparql_endpoint,   "http://localhost:#{sparql_port}/sparql-auth"
set :event_bus_host,    'localhost'
set :puppetmaster_env,  'local'
set :redis_endpoint,    'localhost'
set :redis_port,        6379

set :log_filepath,      '/tmp/brainiak.log'
