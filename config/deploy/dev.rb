# Servers
role :app, "cittavld44.globoi.com"  # deploys app source to filer
role :restart, "cittavld44.globoi.com", :no_release => true # application
role :docs, "cittavld44.globoi.com", :no_release => true  

set :sparql_endpoint, "http://dev.virtuoso.globoi.com:8890/sparql-auth"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "dev"
