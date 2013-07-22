role :be,                   'cittavld507.globoi.com', 'cittavld797.globoi.com'
role :filer,                'filer.qa.globoi.com'

# Hosts
set :virtuoso_host,         'qa.virtuoso.globoi.com'
set :barramento_baas_host,  'barramento.baas.qa.globoi.com'
set :redis_host,            'redis.api.semantica.qa.globoi.com'
set :syslog_host,           'syslog.tcp.glog.qa.globoi.com'
set :filer_host,            'riofd07a'

# Ports
set :sparql_port,           8890

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{sparql_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'qa'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
