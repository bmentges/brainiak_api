namespace :puppet do

    task :default do
        all
    end

    task :all do
        be
    end

    task :be, :roles => :be do
        puppet_prepare

        # Setup
        sudo "/opt/local/bin/puppet-setup"

        # Voltando usuário anterior
        set :user, current_user
        utils.askpass(user)
     end

    task :puppet_prepare do

        # Salvando usuário atual
        set :current_user, user

        # Password
        utils.askpass("puppet")

        # Submódulos
        run_local "git submodule update --init"

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        # Deploy puppetmaster
        run_local <<-EOF
            cd puppet/deploy &&
            fab #{puppetmaster_env} deploy_puppet #{puppet_params}
        EOF

        # Voltando para o loglevel anterior
        logger.level = current_loglevel

    end

end
