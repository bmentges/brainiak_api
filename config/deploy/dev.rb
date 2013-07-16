role :be,               'cittavld44.globoi.com'
role :filer,            'filer.dev.globoi.com'

set :sparql_port,       8890
set :sparql_endpoint,   "http://dev.virtuoso.globoi.com:#{sparql_port}/sparql-auth"
set :event_bus_host,    'barramento.baas.dev.globoi.com'
set :puppetmaster_env,  'dev'
set :redis_endpoint,    'redis.dev.globoi.com'
set :redis_port,        20015
set :redis_password,    'a8pdifs2e2m9afn7tcifcea99674aad2'
