# Servers
role :app, "riolb176.globoi.com" # deploys app source to filer
role :restart, "riomp40lb14.globoi.com","riomp41lb14.globoi.com", :no_release => true # application
role :docs, "riomp40lb14.globoi.com", :no_release => true 

set :sparql_endpoint, "http://virtuoso.semantica.globoi.com:80/api-semantica/sparql-auth"




# Used by puppet module in Capistrano
set :puppetmaster_env, "prod"
