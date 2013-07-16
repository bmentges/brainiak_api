namespace :tdi do

    task :default do
        all
    end

    task :all do
        be
    end

    task :be, :roles => :be do

        utils.askpass("busca")

        permission = capture "sudo -l | grep /opt/local/bin/tdi -q ; echo $?"
        if permission.to_i == 1
            puppet.be
            set :puppet_already_run, 1
        end

        deploy.filter
        upload "tdi.json", "/tmp/tdi.json"
        run "sudo /opt/local/bin/tdi /tmp/tdi.json"
        deploy.unfilter
    end
end
