# Servers
role :app, "filer.qa01.globoi.com"  # deploys app source to filer
role :restart, "cittavld45.globoi.com", :no_release => true # application
role :docs, "cittavld45.globoi.com", :no_release => true

set :sparql_port, "80"
set :sparql_endpoint, "http://qa1.virtuoso.globoi.com:%s/sparql-auth"

set :event_bus_host, "barramento.baas.qa01.globoi.com"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "qa1"
