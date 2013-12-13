desc "SSH para os servidores do projeto"

def ssh_connect(target_role)

    if not ENV['usuario'].nil?
        ssh_user = "#{ENV['usuario']}"
    else
        ssh_user = "#{ENV['USER']}"
    end

    if not roles.include?(target_role)
        puts "ERRO: A role '#{target_role}' não existe neste projeto."
        exit 1
    end

    csshbin = %x[whereis cssh csshX].split("\n").shift
    if roles[target_role].servers.length == 1
      run_local "ssh -l #{ssh_user} " + roles[target_role].servers.shift.to_s
    elsif not csshbin.nil? and not csshbin.empty?
      run_local "#{csshbin} -l #{ssh_user} " + roles[target_role].servers.join(' ')
    else
      puts "Atenção: Não foi possível encontrar nenhum dos executáveis csshX ou cssh. O acesso será a apenas um dos servidores da role #{target_role}."
      run_local "ssh -l #{ssh_user} " + roles[target_role].servers.shift.to_s
    end

end

namespace :ssh do

    task :default do
        tmp_roles = roles.clone
        tmp_roles.delete(:filer) if tmp_roles.include?(:filer)

        if tmp_roles.count == 1
            target_role = tmp_roles.shift[0]
            puts "Connecting to role " + target_role.to_s.upcase + "..."
            ssh_connect(target_role)
        else
            puts <<-EOF
                Este projeto possui mais de uma role. Por favor, especifique a role desejada.
                Exemplo: cap <ambiente> ssh:<role>
           EOF
        end
    end

    task :adm do
        ssh_connect(:adm)
    end

    task :be do
        ssh_connect(:be)
    end

    task :fe do
        ssh_connect(:fe)
    end

    task :filer do
        ssh_connect(:filer)
    end
end
