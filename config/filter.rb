require 'erb'

# Helpers
def read_file(filename)
    data = ""
    File.open(filename, "r") do |f|
        f.each_line do |line|
            data += line
        end
    end
    return data
end

def write_file(filename, content)
    File.open(filename, "w"){|f| f << content}
end

def filter_file(file_in, file_out)
    write_file(file_out,
               ERB.new(read_file(file_in)).result(binding()))
end

namespace :python do

    desc "Filtragem dos arquivos de configuração por ambiente"
    task :filter do
        puts "Sobrescrevendo version.py"
        system 'cd src; python -c "from brainiak.utils.git import build_release_string; print build_release_string()" > brainiak/version.py'

        puts "Filtrando arquivos .unfiltered"
        #system "cp src/#{application}/settings.py src/#{application}/settings.py.atual"
        Dir["**/*.unfiltered"].each do |file_in|
            puts "Filtrando ", file_in
            filter_file(file_in,file_in.chomp(".unfiltered"))
        end
    end
end

namespace :deploy do
  task :restart, :roles => :web do
    run "touch #{ current_path }/tmp/restart.txt"
  end

  task :restart_daemons, :roles => :app do
    sudo "monit restart all -g daemons"
  end
end