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
        puts "Filtrando arquivos .unfiltered"
        system "cp src/api_semantica/settings.py src/api_semantica/settings.py.atual"
        Dir["**/*.unfiltered"].each do |file_in|
            puts "Filtrando ", file_in
            filter_file(file_in,file_in.chomp(".unfiltered"))
        end
    end
end
