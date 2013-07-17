role :filer,            'filer.globoi.com'
role :be,               'riomp40lb14.globoi.com','riomp41lb14.globoi.com'


set :sparql_port,       80
set :sparql_endpoint,   "http://virtuoso.semantica.globoi.com:#{sparql_port}/api-semantica/sparql-auth"
set :event_bus_host,    'barramento.baas.globoi.com'
set :puppetmaster_env,  'prod'
set :redis_endpoint,    'redis.api.semantica.globoi.com'
set :redis_port,        20015
set :redis_password,    'a8pdifs2e2m9afn7tcifcea99674aad2'

set :log_filepath,      '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
