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
            run_local "rm " + file_in.chomp(".unfiltered")
        end
    end

    task :hacks do
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
        utils.askpass("busca")
        run "#{try_sudo} mkdir -p #{dirs.join(' ')} && #{try_sudo} chmod g+w #{dirs.join(' ')}", :roles => :filer
    end

    task :finalize_update do
        # essa task assume que eh um projeto rails e faz
        # symlink do public pro shared, e do logs
        # coisa que nao queremos
    end

    task :docs, :roles => :be do
        puts 'Gerando documentação'
        run_local <<-EOF
            tar chzf docs.tar.gz docs   &&
            make clean                  &&
            cd docs                     &&
            make html                   &&
            cd ..
        EOF
        utils.askpass("busca")
        put File.read("docs.tar.gz"), "/tmp/docs.tar.gz", :via => :scp
        run_once <<-EOF
            cd /tmp && tar xzf docs.tar.gz                                          &&
            cd /tmp/docs                                                            &&
            export PATH="/opt/api_semantica/brainiak/virtualenv/bin:$PATH"          &&
            export PYTHONPATH="#{deploy_to}/current:$PYTHONPATH"                    &&
            make html                                                               &&
            rsync -ac --delay-updates --stats /tmp/docs/build/html/ #{docs_html}/   &&
            cd /tmp                                                                 &&
            rm -rf docs                                                             &&
            rm docs.tar.gz
        EOF
        run_local 'rm docs.tar.gz'
    end

    task :restart, :roles => :be do
        run "sudo /etc/init.d/brainiak-gunicorn-be restart"
    end

    task :clean_local do
        run_local "git checkout -- src/brainiak/settings.py"
    end
end
