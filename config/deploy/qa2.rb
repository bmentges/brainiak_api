role :be,                   'api-semantica-be01.vb.qa02.globoi.com', 'api-semantica-be02.vb.qa02.globoi.com'
role :filer,                'filer.qa02.globoi.com'

# Hosts
set :virtuoso_host,         'qa2.virtuoso.globoi.com'
set :barramento_baas_host,  'barramento.baas.qa02.globoi.com'
set :redis_host,            'redis.qa02.globoi.com'
set :syslog_host,           'syslog.tcp.glog.qa02.globoi.com'
set :filer_host,            'ho.riofd02'

# Ports
set :sparql_port,           8890

# URLs
set :virtuoso_url,          "http://#{virtuoso_host}:#{sparql_port}/sparql-auth"

# Variables
set :puppetmaster_env,      'qa2'
set :redis_password,        'a8pdifs2e2m9afn7tcifcea99674aad2'
