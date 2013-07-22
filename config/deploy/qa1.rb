role :be,                   'cittavld45.globoi.com'
role :filer,                'filer.qa01.globoi.com'

# Hosts
set :virtuoso_host,         'qa1.virtuoso.globoi.com'
set :barramento_baas_host,  'barramento.baas.qa01.globoi.com'
set :redis_host,            'redis.qa01.globoi.com'
set :syslog_host,           'syslog.tcp.glog.qa01.globoi.com'
set :filer_host,            'riofd06'

# Ports
set :sparql_port,           8890

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{sparql_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'qa1'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
