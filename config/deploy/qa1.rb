role :be,               'cittavld45.globoi.com'
role :filer,            'filer.qa01.globoi.com'

set :sparql_port,       8890
set :sparql_endpoint,   "http://qa1.virtuoso.globoi.com:#{sparql_port}/sparql-auth"
set :event_bus_host,    'barramento.baas.qa01.globoi.com'
set :puppetmaster_env,  'qa1'
set :redis_endpoint,    'redis.qa01.globoi.com'
set :redis_port,        20015
set :redis_password,    'a8pdifs2e2m9afn7tcifcea99674aad2'

set :log_filepath,      '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
