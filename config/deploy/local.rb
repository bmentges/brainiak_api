#role :be,                         ''
#role :filer,                      ''

# Hosts
set :barramento_baas_host,        'localhost'
set :filer_host,                  ''
set :redis_host,                  'localhost'
set :syslog_host,                 ''
set :elasticsearch_host,          'localhost:9200'

# Ports
set :redis_port,                  6379

# Variables
set :puppetmaster_env,            'local'
set :redis_password,              'ignored'

# Directories
set :dbpasswd_dir,                ''

# Files
set :log_filepath,                '/tmp/brainiak.log'
set :triplestore_config_filepath, "config/local/triplestore.ini"



# TODO:
# DEBUG = True
# NOTIFY_BUS = True
# ENABLE_CACHE = True
