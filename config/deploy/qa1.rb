# Servers
role :app, "filer.qa01.globoi.com"  # deploys app source to filer
role :restart, "cittavld45.globoi.com", :no_release => true # application
role :docs, "cittavld45.globoi.com", :no_release => true

set :sparql_port, 8890
set :sparql_endpoint, "http://qa1.virtuoso.globoi.com:#{sparql_port}/sparql-auth"

set :event_bus_host, "barramento.baas.qa01.globoi.com"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "qa1"

set :redis_endpoint, "redis.qa01.globoi.com"
set :redis_port, 20015
set :redis_password, "a8pdifs2e2m9afn7tcifcea99674aad2"
