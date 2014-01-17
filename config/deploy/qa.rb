role :be,                         'cittavld895.globoi.com', 'cittavld896.globoi.com'
role :filer,                      'filer.qa.globoi.com'

# Hosts
set :barramento_backstage_host,   'barramento.backstage.qa.globoi.com'
set :redis_host,                  'redis.qa01.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.qa01.globoi.com'
set :filer_host,                  'riofd07a'
set :elasticsearch_host,          'esearch.qa.globoi.com'

# Ports
set :redis_port,                  20019
set :virtuoso_port,               8890

# Variables
set :puppetmaster_env,            'qa'
set :redis_password,              '4fdfa56255f21ccf01b3d78f999caea3'

# Directories
set :dbpasswd_dir,                "/mnt/projetos/dbpasswd/#{projeto}"

# Files
set :log_filepath,                '/opt/logs/brainiak/gunicorn-be/gunicorn-be.log'
set :triplestore_config_filepath, "#{dbpasswd_dir}/triplestore.ini"
