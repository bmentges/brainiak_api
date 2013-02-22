load 'deploy' if respond_to?(:namespace) # cap2 differentiator

# Uncomment if you are using Rails' asset pipeline
# load 'deploy/assets'

Dir['vendor/gems/*/recipes/*.rb','vendor/plugins/*/recipes/*.rb'].each { |plugin| load(plugin) }

load 'config/deploy'
load 'config/filter.rb'
#load 'config/modules/puppet' # Load puppet module to execute puppet-setup every deploy, keeping the environment sync

before "deploy:restart", "deploy:clean_local"
before "deploy:restart", "deploy:cleanup"

#
# Sempre executo o puppet para garantir o ambiente
#
#before "deploy:restart", "puppet:all"

namespace :deploy do
    task :finalize_update do
        # essa task assume que eh um projeto rails e faz
        # symlink do public pro shared, e do logs
        # coisa que nao queremos
    end

    # :restart redefinido para reinciar o gunicorn da APP_v1 apenas
    task :restart, :roles => :restart do
        puts "Reiniciando o GUNICORN 2..."
        run "sudo /etc/init.d/api_semantica-gunicorn-be2.brainiak restart 2> /dev/null"
    end


    task :clean_local do
        puts "Voltando o settings atual"
        system "git checkout -- src/brainiak/settings.py"
    end
end
