# Servers
role :app, "filer.staging.globoi.com" # deploys app source to filer
role :restart, "riovlb160.globoi.com", "riovlb161.globoi.com", :no_release => true # application
role :docs, "riovlb160.globoi.com", :no_release => true

set :sparql_port, 8890
set :sparql_endpoint, "http://staging.semantica.globoi.com:#{sparql_port}/sparql-auth"

set :event_bus_host, "barramento.baas.globoi.com"


# Used by puppet module in Capistrano
set :puppetmaster_env, "staging"

set :redis_endpoint, "redis.api.semantica.globoi.com"
set :redis_port, 20015
set :redis_password, "a8pdifs2e2m9afn7tcifcea99674aad2"
