namespace :tdi do

    task :default do
        all
    end

    task :all do
        be
    end

    task :be, :roles => :be do
        utils.askpass("puppet")
        tdi_permission = capture("sudo -l | grep /opt/local/bin/tdi -q && echo true || echo false").chomp
        if tdi_permission == "true"
            deploy.filter
            upload "tdi.json", "/tmp/tdi-#{projeto}.json"
            run "sudo /opt/local/bin/tdi /tmp/tdi-#{projeto}.json"
            deploy.unfilter
        end
    end
end
