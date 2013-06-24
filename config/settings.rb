load 'deploy' if respond_to?(:namespace) # cap2 differentiator

Dir['vendor/gems/*/recipes/*.rb','vendor/plugins/*/recipes/*.rb'].each { |plugin| load(plugin) }

load 'config/deploy'
load 'config/filter.rb'
load 'config/modules/puppet' # Load puppet module to execute puppet-setup every deploy, keeping the environment sync

before "deploy:update",  "deploy:setup"
before "deploy:restart", "deploy:clean_local"
before "deploy:restart", "deploy:cleanup"

#
# Sempre executo o puppet para garantir o ambiente
#
before "deploy:restart", "puppet:all"

namespace :deploy do
    task :finalize_update do
        # essa task assume que eh um projeto rails e faz
        # symlink do public pro shared, e do logs
        # coisa que nao queremos
    end

    task :docs, :roles => :docs do
        puts "Gerando documentação"
        system "tar chzf docs.tar.gz docs"
        system "cd docs; make html; cd .."
        put File.read("docs.tar.gz"), "/tmp/docs.tar.gz", :via => :scp
        run "cd /tmp && tar xzf docs.tar.gz"
        run 'cd /tmp/docs && export PATH="/opt/api_semantica/brainiak/virtualenv/bin:$PATH" && export PYTHONPATH="' + deploy_to + '/current:$PYTHONPATH" && make html'
        run "rsync -ac --delay-updates --stats /tmp/docs/build/html/ #{docs_html}/"
        run 'cd /tmp && rm -rf docs && rm docs.tar.gz'
        system "rm docs.tar.gz"
    end

    # :restart redefinido para reinciar o gunicorn da APP_v2 (brainiak) apenas
    task :restart, :roles => :restart do
        puts "Reiniciando o GUNICORN 2 do BRAINIAK..."
        run "sudo /etc/init.d/brainiak-gunicorn-be restart 2> /dev/null"
    end


    task :clean_local do
        puts "Voltando o settings atual"
        system "git checkout -- src/brainiak/settings.py"
    end
end
