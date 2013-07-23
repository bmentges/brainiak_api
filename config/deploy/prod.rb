role :be,                   'riomp40lb14.globoi.com','riomp41lb14.globoi.com'
role :filer,                'filer.globoi.com'

# Hosts
set :virtuoso_host,         'virtuoso.semantica.globoi.com'
set :barramento_baas_host,  'barramento.baas.globoi.com'
set :redis_host,            'redis.api.semantica.globoi.com'
set :syslog_host,           'syslog.tcp.glog.globoi.com'
set :filer_host,            'riofb01a'

# Ports
set :virtuoso_port,         80

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{virtuoso_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'prod'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
