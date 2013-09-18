role :be,                         'cittavld891.globoi.com'
role :filer,                      'filer.dev.globoi.com'

# Hosts
set :barramento_backstage_host,   'barramento.backstage.dev.globoi.com'
set :filer_host,                  'riofd06'
set :redis_host,                  'redis.dev.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.dev.globoi.com'
set :elasticsearch_host,          'esearch.dev.globoi.com'

# Ports
set :redis_port,                  20019

# Variables
set :puppetmaster_env,            'dev'
set :redis_password,              'a8pdifs2e2m9afn7tcifcea99674aad2'

# Directories
set :dbpasswd_dir,                "/mnt/projetos/dbpasswd/#{projeto}"

# Files
set :log_filepath,                '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
set :triplestore_config_filepath, "#{dbpasswd_dir}/triplestore.ini"
