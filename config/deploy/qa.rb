# Servers
role :app, "filer.qa.globoi.com"  # deploys app source to filer
role :restart, "cittavld507.globoi.com", "cittavld797.globoi.com", :no_release => true # application
role :docs, "cittavld507.globoi.com", :no_release => true

set :sparql_port, "8890"
set :sparql_endpoint, "http://qa.virtuoso.globoi.com:%s/sparql-auth"

set :event_bus_host, "barramento.baas.qa.globoi.com"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "qa"

# EOF
