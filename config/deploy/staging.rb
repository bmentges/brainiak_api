# Servers
role :app, "riovlb13.globoi.com" # deploys app source to filer
role :restart, "riovlb160.globoi.com", "riovlb161.globoi.com", :no_release => true # application
role :docs, "riovlb160.globoi.com", :no_release => true 

set :sparql_endpoint, "http://staging.semantica.globoi.com:8890/sparql-auth"




# Used by puppet module in Capistrano
set :puppetmaster_env, "staging"
