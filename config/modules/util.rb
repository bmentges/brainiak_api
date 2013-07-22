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

    # Fecha todas as sessões SSH para troca de usuário.
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
                set(:password) { Capistrano::CLI.password_prompt("Senha para o usuário #{username}: ") }
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
        run_local "./scripts/pdb_hunter.sh ."
    end

    task :submodules do
        run_local "git submodule update --init"
    end

    task :clean_df do
        run_local "git clean -df"
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

    task :do_not_deploy_local do
        if stage.to_s.start_with? "local"
            puts "Erro: Nao faz sentido fazer deploy para o ambiente local!"
            exit 1
        end
    end

    def check_acl(service_name, hosts, port="80")
      hosts = "#{hosts}".split(",")

      if exists?(:testnofail)
        fail_command = "true"
      else
        fail_command = "false"
      end

      hosts.to_a.each do |host|
        host = host.strip

        if host.include?(":")
          host, port = host.split(":")
        end

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run <<-EOF
          success='ACL: #{service_name} #{host}:#{port} [\e[00;32m  OK  \e[00m]'      ;
          warning='ACL: #{service_name} #{host}:#{port} [\e[00;33m  WARNING  \e[00m]' ;
          failure='ACL: #{service_name} #{host}:#{port} [\e[00;31m  FAILED  \e[00m]'  ;
          ret="failure" ;
          timeout=3 ;

          ini=$(date +"%s") ;

          ( nc -w $timeout #{host} #{port} >/dev/null 2>&1 )
          &&
          ret="success" ;

          end=$(date +"%s") ;
          let tot=end-ini ;

          if [[ "$ret" == "success" ]] ; then
            echo -e "$success" ;
            true ;
          else
            if [[ $tot -lt $timeout ]] ; then
              echo -e "$warning" ;
              true ;
            else
              echo -e "$failure" ;
              #{fail_command} ;
            fi
          fi
        EOF

        # Voltando para o loglevel anterior
        logger.level = current_loglevel

      end
    end

    def check_rw(dir, use_sudo=false)
        if exists?(:testnofail)
            fail_command = "true"
        else
            fail_command = "false"
        end

        if use_sudo
            sudo_command = "sudo "
        else
            sudo_command = ""
        end

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run <<-EOF
            success='RW #{dir} [\e[00;32m  OK  \e[00m]'     ;
            failure='RW #{dir} [\e[00;31m  FAILED  \e[00m]' ;
            ret="failure" ;

            (#{sudo_command}touch #{dir}/${HOSTNAME}.rw >/dev/null 2>&1 && #{sudo_command}rm -f #{dir}/${HOSTNAME}.rw >/dev/null 2>&1)
            &&
            ret="success" ;

            if [[ "$ret" == "success" ]] ; then
                echo -e "$success" ;
                true ;
            else
                echo -e "$failure" ;
                #{fail_command} ;
            fi
        EOF

        logger.level = current_loglevel

    end

    def check_ro(dir, use_sudo=false)
        if exists?(:testnofail)
            fail_command = "true"
        else
            fail_command = "false"
        end

        if use_sudo
            sudo_command = "sudo "
        else
            sudo_command = ""
        end

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run <<-EOF
            success='RO #{dir} [\e[00;32m  OK  \e[00m]'     ;
            failure='RO #{dir} [\e[00;31m  FAILED  \e[00m]' ;
            ret="failure" ;

            ( [[ ! -d #{dir} ]] || { #{sudo_command}touch #{dir}/${HOSTNAME}.rw >/dev/null 2>&1 && #{sudo_command}rm -f #{dir}/${HOSTNAME}.rw >/dev/null 2>&1 ; })
            ||
            ret="success" ;

            if [[ "$ret" == "success" ]] ; then
                echo -e "$success" ;
                true ;
            else
                echo -e "$failure" ;
                #{fail_command} ;
            fi
        EOF

        logger.level = current_loglevel

    end

    def check_proxy(proxy, url, expect_string='')
        if exists?(:testnofail)
            fail_command = "true"
        else
            fail_command = "false"
        end

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        if expect_string == ''
            run <<-EOF
                success='PROXY #{url}
PROXY via #{proxy} (expect: != Access Denied) [\e[00;32m  OK  \e[00m]'      ;
                failure='PROXY #{url}
PROXY via #{proxy} (expect: != Access Denied) [\e[00;31m  FAILED  \e[00m]'  ;
                ret="failure" ;

                (curl --connect-timeout 1 -s -v -L -x "#{proxy}" "#{url}" 2>&1 | egrep 'Access Denied\.' >/dev/null 2>&1)
                ||
                ret="success" ;

                if [[ "$ret" == "success" ]] ; then
                    echo -e "$success" ;
                    true ;
                else
                    echo -e "$failure" ;
                    #{fail_command} ;
                fi
            EOF
        else
            run <<-EOF
                success='PROXY #{url}
PROXY via #{proxy} (expect: == #{expect_string}) [\e[00;32m  OK  \e[00m]'      ;
                failure='PROXY #{url}
PROXY via #{proxy} (expect: == #{expect_string}) [\e[00;31m  FAILED  \e[00m]'  ;
                ret="failure" ;

                (curl --connect-timeout 1 -s -v -L -x "#{proxy}" "#{url}" 2>&1 | egrep '#{expect_string}' >/dev/null 2>&1)
                &&
                ret="success" ;

                if [[ "$ret" == "success" ]] ; then
                    echo -e "$success" ;
                    true ;
                else
                    echo -e "$failure" ;
                    #{fail_command} ;
                fi
            EOF
        end

        logger.level = current_loglevel

    end

    def check_ssh(usuario, host)
        if exists?(:testnofail)
            fail_command = "true"
        else
            fail_command = "false"
        end

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run <<-EOF
            success='SSH Deploy #{usuario}@#{host} [\e[00;32m  OK  \e[00m]'       ;
            failure='SSH Deploy #{usuario}@#{host} [\e[00;31m  FAILED  \e[00m]'   ;
            ret="failure" ;

            (/tmp/#{user}-ssh.expect #{usuario} #{host} true >/dev/null 2>&1)
            &&
            ret="success" ;

            if [[ "$ret" == "success" ]] ; then
                echo -e "$success" ;
                true ;
            else
                echo -e "$failure" ;
                #{fail_command} ;
            fi
        EOF

        logger.level = current_loglevel

    end

    def check_http_status(hostname, uri, code, port=8080, ssl=false, host_header=false)

        utils.askpass("busca")

        if exists?(:testnofail)
            fail_command = "true"
        else
            fail_command = "false"
        end

        cmd = "curl -o /dev/null -s -w '%{http_code}'"

        if host_header == true
            cmd = cmd + " -H 'Host: #{hostname}'"
        elsif host_header != false
            cmd = cmd + " -H 'Host: #{host_header}'"
        end

        if ssl
            cmd = cmd + " -k "
            url = " https://#{hostname}:#{port}#{uri}"
        else
            url = " http://#{hostname}:#{port}#{uri}"
        end

        cmd = cmd + "#{url} 2>/dev/null"

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run <<-EOF
            success='Request #{url} expecting HTTP #{code} [\e[00;32m  OK  \e[00m]'       ;
            failure='Request #{url} expecting HTTP #{code} [\e[00;31m  FAILED  \e[00m]'   ;
            ret="failure" ;
            if [[ $(#{cmd}) == #{code} ]];
             then
                echo $success;
                true;
            else
                echo $failure;
                #{fail_command};
            fi
        EOF

        logger.level = current_loglevel

    end

    def check_http_local_status(hostname, uri, code, port=8080, ssl=false, host_header=false)

        cmd = "curl -o /dev/null -s -w '%{http_code}'"

        if host_header == true
            cmd = cmd + " -H 'Host: #{hostname}'"
        elsif host_header != false
            cmd = cmd + " -H 'Host: #{host_header}'"
        end

        if ssl
            cmd = cmd + " -k "
            url = " https://#{hostname}:#{port}#{uri}"
        else
            url = " http://#{hostname}:#{port}#{uri}"
        end

        cmd = cmd + "#{url} 2>/dev/null"

        # Salvando loglevel atual
        current_loglevel = logger.level
        logger.level = Capistrano::Logger::INFO

        run_local <<-EOF
            success='Request #{url} expecting HTTP #{code} [\e[00;32m  OK  \e[00m]'       ;
            failure='Request #{url} expecting HTTP #{code} [\e[00;31m  FAILED  \e[00m]'   ;
            ret="failure" ;
            if [[ $(#{cmd}) == #{code} ]];
             then
                echo $success;
            else
                echo $failure;
            fi
        EOF

        logger.level = current_loglevel

    end
end
#############
# END UTILS #
#############
