# Servers
role :app, "filer.qa02.globoi.com"   # deploys app source to filer
#role :restart, "api-semantica-be01.vb.qa02.globoi.com", "api-semantica-be02.vb.qa02.globoi.com", :no_release => true # application
# So temos uma maquina normalmente
role :restart, "api-semantica-be01.vb.qa02.globoi.com", :no_release => true # application
role :docs, "api-semantica-be01.vb.qa02.globoi.com", :no_release => true

set :sparql_port, 8890
set :sparql_endpoint, "http://qa2.virtuoso.globoi.com:#{sparql_port}/sparql-auth"

set :event_bus_host, "barramento.baas.qa02.globoi.com"

# Lazy...
set :password, 'busca'

# Used by puppet module in Capistrano
set :puppetmaster_env, "qa2"

set :redis_endpoint, "redis.qa02.globoi.com"
set :redis_port, 20015
set :redis_password, "a8pdifs2e2m9afn7tcifcea99674aad2"
