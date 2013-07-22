role :be,                   'cittavld44.globoi.com'
role :filer,                'filer.dev.globoi.com'

# Hosts
set :virtuoso_host,         'dev.virtuoso.globoi.com'
set :barramento_baas_host,  'barramento.baas.dev.globoi.com'
set :redis_host,            'redis.dev.globoi.com'
set :syslog_host,           'syslog.tcp.glog.dev.globoi.com'
set :filer_host,            'riofd06'

# Ports
set :sparql_port,           8890

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{sparql_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'dev'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
