role :be,                         'riomp40lb14.globoi.com','riomp41lb14.globoi.com'
role :filer,                      'filer.globoi.com'

# Hosts
set :barramento_baas_host,        'barramento.baas.globoi.com'
set :filer_host,                  'riofb01a'
set :redis_host,                  'redis.api.semantica.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.globoi.com'
set :virtuoso_host,               'virtuoso.semantica.globoi.com'

# Ports
set :redis_port,                  20015
set :virtuoso_port,               80

# URLs
set :virtuoso_url,                "http://#{virtuoso_host}:#{virtuoso_port}/sparql-auth"

# Variables
set :puppetmaster_env,            'prod'
set :redis_password,              'a8pdifs2e2m9afn7tcifcea99674aad2'

# Directories
set :dbpasswd_dir,                '/mnt/projetos/dbpasswd/#{projeto}'

# Files
set :log_filepath,                '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
set :triplestore_config_filepath, "#{dbpasswd_dir}/config.ini"
