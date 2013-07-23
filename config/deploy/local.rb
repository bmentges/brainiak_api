role :be,               'cittavld44.globoi.com'
role :filer,            'filer.dev.globoi.com'

# TODO:
# DEBUG = True
# NOTIFY_BUS = True
# ENABLE_CACHE = True

set :sparql_port,       8890
set :virtuoso_host,         'localhost'
set :virtuoso_url,          "http://#{virtuoso_host}:#{sparql_port}/sparql-auth"
set :barramento_baas_host,    'localhost'
set :puppetmaster_env,  'local'
set :redis_host,    'localhost'
set :redis_port,        6379
set :syslog_host,           'syslog.tcp.glog.dev.globoi.com'
set :filer_host,            'riofd06'

set :log_filepath,      '/tmp/brainiak.log'
