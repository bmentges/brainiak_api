role :be,                         'cittavld507.globoi.com', 'cittavld797.globoi.com'
role :filer,                      'filer.qa.globoi.com'

# Hosts
set :virtuoso_host,               'qa.virtuoso.globoi.com'
set :barramento_backstage_host,   'barramento.backstage.qa.globoi.com'
set :redis_host,                  'redis.api.semantica.qa.globoi.com'
set :syslog_host,                 'syslog.tcp.glog.qa.globoi.com'
set :filer_host,                  'riofd07a'
set :elasticsearch_host,          'esearch.qa.globoi.com'

# Ports
set :virtuoso_port,              8890

# URLs
set :virtuoso_url,                "http://#{virtuoso_host}:#{virtuoso_port}/sparql-auth"

# Variables
set :puppetmaster_env,            'qa'
set :redis_password,              'a8pdifs2e2m9afn7tcifcea99674aad2'

# Directories
set :dbpasswd_dir,                "/mnt/projetos/dbpasswd/#{projeto}"

# Files
set :triplestore_config_filepath, "#{dbpasswd_dir}/triplestore.ini"
