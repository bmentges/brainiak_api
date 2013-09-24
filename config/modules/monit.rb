namespace :monit do

    set :monit_initscript, "/etc/init.d/monit"

    task :start, :roles => :be do
        utils.askpass("puppet")
        run("sudo #{monit_initscript} start")
    end

    task :stop, :roles => :be do
        utils.askpass("puppet")
        run("sudo #{monit_initscript} stop")
    end

end
