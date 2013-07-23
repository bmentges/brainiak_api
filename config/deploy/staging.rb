role :be,                   'riovlb160.globoi.com', 'riovlb161.globoi.com'
role :filer,                'filer.staging.globoi.com'

# Hosts
set :virtuoso_host,         'staging.semantica.globoi.com'
set :barramento_baas_host,  'barramento.baas.globoi.com'
set :redis_host,            'redis.api.semantica.globoi.com'
set :syslog_host,           'syslog.tcp.glog.globoi.com'
set :filer_host,            'riofb01a'

# Ports
set :virtuoso_port,         8890

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{virtuoso_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'staging'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
