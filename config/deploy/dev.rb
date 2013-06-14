# Servers
role :app, "filer.dev.globoi.com"  # deploys app source to filer
role :restart, "cittavld44.globoi.com", :no_release => true # application
role :docs, "cittavld44.globoi.com", :no_release => true

set :sparql_port, 8890
set :sparql_endpoint, "http://dev.virtuoso.globoi.com:#{sparql_port}/sparql-auth"

set :event_bus_host, "barramento.baas.dev.globoi.com"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "dev"

set :redis_endpoint, "redis.dev.globoi.com"
set :redis_port, 20015
set :redis_password, "a8pdifs2e2m9afn7tcifcea99674aad2"
