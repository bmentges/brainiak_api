#!/usr/bin/env ruby

require 'capistrano'
require 'capistrano/ext/multistage'

load 'deploy' if respond_to?(:namespace) # cap2 differentiator

Dir['vendor/gems/*/recipes/*.rb','vendor/plugins/*/recipes/*.rb'].each { |plugin| load(plugin) }
Dir['config/*.rb'].each { |m| load m }
Dir['config/modules/*.rb'].each { |m| load m }

before "deploy:update",         "tdi:all"
before "deploy:update",         "deploy:setup"
before "deploy:update",         "deploy:filter"
before "deploy:restart",        "deploy:docs"
before "deploy:update_code",    "deploy:hacks"
after  "deploy:restart",        "deploy:unfilter"
