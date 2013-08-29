#!/usr/bin/env ruby

require 'capistrano'
require 'capistrano/ext/multistage'

load 'deploy' if respond_to?(:namespace) # cap2 differentiator

Dir['vendor/gems/*/recipes/*.rb','vendor/plugins/*/recipes/*.rb'].each { |plugin| load(plugin) }
Dir['config/*.rb'].each { |m| load m }
Dir['config/modules/*.rb'].each { |m| load m }

before "deploy:update",         "deploy:setup"
before "deploy:update",         "utils:version_py"
before "deploy:update",         "deploy:filter"
before "deploy:update",         "deploy:copy_doc"
before "deploy:restart",        "deploy:cleanup"
#before "deploy:restart",        "deploy:docs"
before "deploy:update_code",    "deploy:hacks"
after "deploy:setup",           "tdi:all"
after  "deploy:restart",        "deploy:unfilter"
after  "deploy:update",         "deploy:clean_doc"
after  "deploy:update",         "deploy:clean_local"
