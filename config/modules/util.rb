require 'erb'

##########
# FILTER #
##########
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
    File.open(filename, "w") {|f| f << content}
end

def filter_file(file_in, file_out)
    write_file(file_out, ERB.new(read_file(file_in)).result(binding()))
end
##############
# END FILTER #
##############

###########
# PATCHES #
###########
# Monkey patch Namespace
class Capistrano::Configuration::Namespaces::Namespace
    # Allow roles inside namespace
    def role(*args)
        method_missing(:role, *args)
    end
end

# Monkey patch Inspect
module Capistrano::Configuration::Actions::Inspect
    # Run capture on all servers in a given role
    def capture_all(command, options={})
        output = ""
        invoke_command(command, options) do |ch, stream, data|
            case stream
                when :out then output << data
                when :err then warn "[ERR :: #{ch[:server]}] #{data}"
            end
        end
        output
    end
end

# Monkey patch Invocation
module Capistrano::Configuration::Actions::Invocation
    # Run local command and respect exit code
    def run_local(command)
        command = command.strip
        logger.debug "executing locally #{command.strip.inspect}"
        raise "ERR: Error executing local command: #{command}" unless system(command)
    end

    # Run remote command only on the first server for a given role
    def run_once(command)
        run command, :once => true
    end

    # Run remote stream command only on the first server for a given role
    def stream_once(command)
        stream command, :once => true
    end
end
###############
# END PATCHES #
###############

#########
# UTILS #
#########
namespace :utils do
    def is_deploy_host?
      puts "Deployment via OCD: " + ( ENV.has_key?('OCD') and ENV['OCD'] == "1" ).to_s
      return ( ENV.has_key?('OCD') and ENV['OCD'] == "1" )
    end

    # Fecha todas as sessões SSH para troca de usuario.
    def disconnect
      sessions.values.each { |session| session.close }
      sessions.clear
    end

    # Senha no shell (cap ... <username>_pass=<senha> ...).
    def askpass(username)
        no_autologin_users_list = %w(deploy root)

        disconnect

        set :user, username
        set :"#{username}_params", ''

        unless is_deploy_host?
            if stage.to_s =~ /^(dev|qa1|qa2)/
                unless no_autologin_users_list.include?(username)
                    set :"#{username}_pass", username
                    puts "Setting password automatically for user '#{username}'..."
                end
            end

            unless ENV["#{username}_pass"].nil?
                set :"#{username}_pass", ENV["#{username}_pass"]
            end

            if exists?(:"#{username}_pass")
                set :password, fetch("#{username}_pass")
            else
                set(:password) { Capistrano::CLI.password_prompt("Senha para o usuario #{username}: ") }
                set :"#{username}_pass", password
            end

            case username
                when 'puppet'
                    set :"#{username}_params", "-p #{password}"
                else
                    # Nothing (reservado para outras configurações especiais).
            end
        end
    end

    # Cria dir temporário local
    task :make_temp do
        clean_temp
        run_local "mkdir -p #{temp_dir}/#{projeto}"
    end

    # Remove dir temporário local
    task :clean_temp do
        if projeto != "" and projeto != "/"
            run_local "rm -rf /tmp/#{projeto}"
        end
    end

    task :pdb_hunter do
        run_local "./tools/pdb_hunter.sh ."
    end

    task :submodules do
        run_local "git submodule update --init"
    end

    task :clean_df do
        run_local "git clean -df"
    end

    task :version_py do
        puts 'Atualizando arquivo version.py...'
        run_local <<-EOF
            cd src      &&
            python -c "from brainiak.utils.git import build_release_string; print build_release_string()" > brainiak/version.py
        EOF
    end

    # git version.txt local
    task :version_git do
        run_local <<-EOF
            cd #{repository}
            date > version.txt                                                  &&
            git describe --all | awk -F / '{print $NF}' >> version.txt          &&
            git log -1 --pretty=format:\'%H | %an | %ai | %s%n\' >> version.txt &&
            echo $USER@$HOSTNAME >> version.txt                                 &&
            touch version.txt
            cd -
        EOF
    end

    # svn version.txt local
    task :version_svn do
        run_local <<-EOF
            cd #{repository}
            date > version.txt                                              &&
            svn info | grep URL: | awk -F / '{print $NF}' >> version.txt    &&
            svn log -l 1 >> version.txt                                     &&
            echo $USER@$HOSTNAME >> version.txt                             &&
            touch version.txt
            cd -
        EOF
    end

    # TODO: Usar git submodule foreach --recursive pwd
    # git submodules version.txt local
    task :version_git_submodules do

        submodules = `git submodule status | awk '{print $2}'`
        raiz = `pwd`
        raiz = raiz.chomp

        submodules = submodules.split "\n"

        submodules.each do |submodulo|
            submodulo = submodulo.chomp
            submodulo_dir = "#{raiz}/#{submodulo}"
            puts "Adicionando version.txt do submodulo: \"#{submodulo}\""
            run_local <<-EOF
                cd #{submodulo_dir}                                                 &&
                date > version.txt                                                  &&
                git describe --all | awk -F / '{print $NF}' >> version.txt          &&
                git log -1 --pretty=format:\'%H | %an | %ai | %s%n\' >> version.txt &&
                echo $USER@$HOSTNAME >> version.txt                                 &&
                touch version.txt
            EOF
        end
    end

    # Remove todos os version.txt locais
    task :clean_version do
        puts "Limpando todos os version.txt locais:"
        version_files = `find . -type f -name version.txt | cut -c3-`
        version_files = version_files.split "\n"

        version_files.each do |version_file|
            version_file = version_file.chomp
            puts "Limpando: \"#{version_file}\""
            run_local "rm -f #{version_file}"
        end
    end

    # Depois do ln -s para current o restart estava lendo ainda o código do
    # release anterior por conta do cache de NFS, que é de aprox. 30s
    task :sleep_link do
        puts "Sleeping 45 seconds..." unless stage.to_s.start_with? "dev" or stage.to_s.start_with? "qa"
        sleep 45 unless stage.to_s.start_with? "dev" or stage.to_s.start_with? "qa"
    end


end
#############
# END UTILS #
#############
