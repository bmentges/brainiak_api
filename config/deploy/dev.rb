# Servers
role :app, "filer.dev.globoi.com"  # deploys app source to filer
role :restart, "cittavld44.globoi.com", :no_release => true # application
role :docs, "cittavld44.globoi.com", :no_release => true  

set :sparql_endpoint, "http://dev.virtuoso.globoi.com:8890/sparql-auth"

set :event_bus_host, "barramento.baas.dev.globoi.com"
set :event_bus_port, "61613"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "dev"
