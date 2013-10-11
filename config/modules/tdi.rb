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

            generate_triplestore_json
            if File.exist?(triplestore_json_file)
                utils.askpass("puppet")
                upload triplestore_json_file, "/tmp/tdi-triplestore.json"
                run "sudo /opt/local/bin/tdi /tmp/tdi-triplestore.json"
                File.delete(triplestore_json_file)
            end
        end
    end

    task :generate_triplestore_json, :roles => :be do

        utils.askpass("brainiak")
        host_port_list = capture("fgrep url /mnt/projetos/dbpasswd/brainiak/triplestore.ini | cut -f3 -d/ | sort -u", :once => true).split("\n")

        triplestore_hash = Hash.new
        triplestore_hash['triplestore'] = {}
        triplestore_hash['triplestore']['desc'] = 'TDI de ACL para os hosts do triplestore.ini.'
        triplestore_hash['triplestore']['acl'] = {}
        
        host_port_list.each do |host_port|
            host,port = host_port.split(':')
            port = 80 if port.nil?
            triplestore_hash['triplestore']['acl'][host] = { 'port' => port.to_i }
        end

        require 'json'
        
        begin
            File.open(triplestore_json_file, "w") { |file| file.write(triplestore_hash.to_json) }
        rescue IOError => e
            puts "Could not write file '#{triplestore_json_file}'!"
            puts e.message
        end
    end
end
