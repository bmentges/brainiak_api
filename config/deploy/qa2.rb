role :filer,            'filer.qa02.globoi.com'
role :be,               'api-semantica-be01.vb.qa02.globoi.com', 'api-semantica-be02.vb.qa02.globoi.com'

set :sparql_port,       8890
set :sparql_endpoint,   "http://qa2.virtuoso.globoi.com:#{sparql_port}/sparql-auth"
set :event_bus_host,    'barramento.baas.qa02.globoi.com'
set :puppetmaster_env,  'qa2'
set :redis_endpoint,    'redis.qa02.globoi.com'
set :redis_port,        20015
set :redis_password,    'a8pdifs2e2m9afn7tcifcea99674aad2'
