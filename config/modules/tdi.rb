namespace :tdi do

    task :default do
        all
    end

    task :all do
        be
    end

    task :be, :roles => :be do
        utils.askpass("puppet")
        tdi_installed = capture("[[ -e /opt/local/bin/tdi ]] && echo true || echo false")
        if tdi_installed == "true"
            deploy.filter
            upload "tdi.json", "/tmp/tdi.json"
            run "sudo /opt/local/bin/tdi /tmp/tdi.json"
            deploy.unfilter
        end
    end
end
