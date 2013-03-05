# Servers
role :app, "filer.qa02.globoi.com"   # deploys app source to filer
role :restart, "api-semantica-be01.vb.qa02.globoi.com", "api-semantica-be02.vb.qa02.globoi.com", :no_release => true # application
role :docs, "api-semantica-be01.vb.qa02.globoi.com", :no_release => true  

set :sparql_endpoint, "http://qa2.virtuoso.globoi.com:8890/sparql-auth"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "qa2"
