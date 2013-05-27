role :app, "api-semantica-dev.plataformas.glb.com"
role :restart, "api-semantica-dev.plataformas.glb.com", :no_release => true

set : sparql_port, "8890"
set :sparql_endpoint, "http://qa1.virtuoso.globoi.com:%d/sparql"
set :solr_endpoint, "http://master.solr.semantica.qa01.globoi.com"

set :redis_endpoint, "redis.qa1.globoi.com"
set :redis_port, 20015
set :redis_password, "a8pdifs2e2m9afn7tcifcea99674aad2"

set :log_file, "/opt/logs/api-semantica/api-semantica.log"
set :log_level, "logging.INFO"

set :deploy_to, "/mnt/projetos/deploy-be/#{application}/app"

set :docs_html, "/mnt/projetos/deploy-be/api_semantica/app/current/docs"

set :usuarios_api_semantica, "/var/local/usuarios_api_semantica.txt"
