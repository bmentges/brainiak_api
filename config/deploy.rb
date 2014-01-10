set :stages,                %w(dev qa1 qa2 qa staging prod)
set :default_stage,         "dev"

set :application,           "brainiak"
set :projeto,               "#{application}"
set :user,                  "brainiak"
set :deploy_to,             "/mnt/projetos/deploy-be/#{projeto}/app"
set :docs_html,             "#{deploy_to}/current/docs"
set :use_sudo,              false
set :via,                   :scp
set :repository,            "src"
set :scm,                   :none
set :deploy_via,            :copy
set :copy_dir,              "/tmp"
set :keep_releases,         4
set :projeto_log_dir,       "/opt/logs/#{projeto}/#{projeto}.log"
set :triplestore_json_file, 'triplestore.json'
set :copy_exclude,          [
                                "*.pyc",
                                "**/*.pyc",
                                ".unfiltered",
                                "**/*.log",
                                "**/.git",
                                "**/.gitignore",
                                "nosetests.xml",
                                "**/.coverage",
                                "**/.idea",
                                "**/*.unfiltered"
                             ]

namespace :deploy do

    task :filter do
        Dir["**/*.unfiltered"].each do |file_in|
            puts "Filtrando arquivo '#{file_in}'..."
            filter_file(file_in,file_in.chomp(".unfiltered"))
        end
    end

    task :unfilter do
        Dir["**/*.unfiltered"].each do |file_in|
            puts "Removendo arquivo '" + file_in.chomp(".unfiltered") + "'..."
            run_local "rm -f " + file_in.chomp(".unfiltered")
        end
    end

    task :hacks do

        utils.askpass("brainiak")

        update_code_task = find_task('update_code')
        update_code_task.options[:roles] = :filer

        symlink_task = find_task('symlink')
        if not symlink_task.nil?
            symlink_task.options[:roles] = :filer
        end

        create_symlink_task = find_task('create_symlink')
        if not create_symlink_task.nil?
            create_symlink_task.options[:roles] = :filer
        end

        cleanup_task = find_task('cleanup')
        cleanup_task.options[:roles] = :filer
    end

    task :setup do

        puppet.all

        dirs = [deploy_to, releases_path, shared_path]
        utils.askpass("brainiak")
        run "#{try_sudo} mkdir -p #{dirs.join(' ')} && #{try_sudo} chmod g+w #{dirs.join(' ')}", :roles => :filer
    end

    task :finalize_update do
        # essa task assume que eh um projeto rails e faz
        # symlink do public pro shared, e do logs
        # coisa que nao queremos
    end

    task :copy_doc do
        run_local "cp -rf docs/build/html src/docs"
    end

    task :copy_locale do
        run_local "cp -rf locale src/"
    end

    task :clean_doc do
        run_local "rm -rf src/docs"
    end

    task :clean_locale do
        run_local "rm -rf src/locale"
    end

    task :docs, :roles => :be do
        puts 'Gerando docs'
        run_local <<-EOF
            tar chzf docs.tar.gz docs   &&
            make clean                  &&
            cd docs                     &&
            make html                   &&
            cd ..                       &&
            git checkout -- .
        EOF
        utils.askpass("brainiak")
        put File.read("docs.tar.gz"), "/tmp/docs.tar.gz", :via => :scp
        run_once <<-EOF
            cd /tmp && tar xzf docs.tar.gz                                          &&
            cd /tmp/docs                                                            &&
            export PATH="/opt/brainiak/virtualenv/bin:$PATH"          &&
            export PYTHONPATH="#{deploy_to}/current:$PYTHONPATH"                    &&
            make html                                                               &&
            rsync -ac --delay-updates --stats /tmp/docs/build/html/ #{docs_html}/   &&
            cd /tmp                                                                 &&
            rm -rf docs                                                             &&
            rm docs.tar.gz
        EOF
        run_local 'rm docs.tar.gz'
    end

    task :filer_sync do
        # Check if current_release is seen in all servers and current link has been updated.

        filer_current = capture "readlink -snf /mnt/projetos/deploy-be/brainiak/app/current", :roles => :filer
        elaspsed_time = 0

        servers = find_servers(:roles => :be)
        servers.each do |s|
            server_current = capture "readlink -snf /mnt/projetos/deploy-be/brainiak/app/current", :hosts => s
            puts "[#{s}]:"
            puts "  Server current link: #{server_current}"
            puts "  Filer current link:  #{filer_current}"
            while not server_current.eql?(filer_current)
                sleep 1
                elaspsed_time += 1
                server_current = capture "readlink -snf /mnt/projetos/deploy-be/brainiak/app/current", :hosts => s
            end
        end
        puts "Total elapsed sync time: #{elaspsed_time.to_s}"
    end

    task :restart, :roles => :be do
        monit.stop if not stage.to_s.eql?('prod')
        utils.askpass("brainiak")
        run "sudo /etc/init.d/brainiak-gunicorn-be restart"
        run "sudo /etc/init.d/brainiak-nginx-be restart"
        monit.start if not stage.to_s.eql?('prod')
    end

    task :clean_local do
        run_local "git checkout -- src/brainiak/version.py"
    end
end
