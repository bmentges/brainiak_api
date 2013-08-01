set :stages,                %w(dev qa1 qa2 qa staging prod)
set :default_stage,         "dev"

set :application,           "brainiak"
set :project,               "#{application}"
set :projeto,               "#{application}"

set :deploy_to,             "/mnt/projetos/deploy-be/api_semantica/#{projeto}/app"
set :docs_html,             "#{deploy_to}/current/docs"

set :user,                  "busca"
set :use_sudo,              false
set :via,                   :scp

set :repository,            "src"
set :scm, :none
set :deploy_via,            :copy
set :copy_dir,              "/tmp"

set :keep_releases,         4

set :copy_exclude,          [
                            "*.pyc", "**/*.pyc",
                            ".unfiltered",
                            "**/*.log",
                            "**/.git", "**/.gitignore",
                            "nosetests.xml", "**/.coverage", "**/.idea" ]
