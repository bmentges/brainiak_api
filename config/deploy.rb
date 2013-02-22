require 'capistrano'
require 'capistrano/ext/multistage'

set :stages, %w(dev qa1 qa2 staging prod)
set :default_stage, "dev"

set :application, "api_semantica"
set :project, "#{application}"

set :deploy_to, "/mnt/projetos/deploy-be/#{application}/app2"

before "deploy:update", "python:filter"

set :user, "busca"
set :use_sudo, false
set :via, :scp

set :repository, "src"
set :scm, :none
set :deploy_via, :copy
set :copy_dir, "/tmp"

set :keep_releases, 4

set :copy_exclude, [
    "*.pyc", "**/*.pyc",
    ".unfiltered",
    "**/*.log",
    "**/.git", "**/.gitignore",
    "nosetests.xml", "**/.coverage", "**/.idea" ]


## Variaveis para o module puppet do capistrano
set :puppet_host, "puppet.globoi.com:8140" unless exists?(:puppet_host)

