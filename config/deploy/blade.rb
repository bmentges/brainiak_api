role :be,                       "api-semantica-dev.plataformas.glb.com"
role :filer,                    "api-semantica-dev.plataformas.glb.com"

set :virtuoso_port,             8890
set :sparql_endpoint,           "http://qa1.virtuoso.globoi.com:#{virtuoso_port}/sparql"
set :solr_endpoint,             "http://master.solr.semantica.qa01.globoi.com"
set :redis_endpoint,            "redis.qa1.globoi.com"
set :redis_port,                20015
set :redis_password,            "4fdfa56255f21ccf01b3d78f999caea3"
set :log_file,                  "/opt/logs/api-semantica/api-semantica.log"
set :log_level,                 "logging.INFO"
set :deploy_to,                 "/mnt/projetos/deploy-be/#{application}/app"
set :docs_html,                 "/mnt/projetos/deploy-be/api_semantica/app/current/docs"
set :usuarios_api_semantica,    "/var/local/usuarios_api_semantica.txt"
