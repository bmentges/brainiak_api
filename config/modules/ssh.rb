desc "SSH para os servidores do projeto"

def ssh_connect(target_role)

    if not roles.include?(target_role)
        puts "ERRO: A role '#{target_role}' não existe neste projeto."
        exit 1
    end

    csshbin = %x[which cssh csshX].split("\n").shift
    if roles[target_role].servers.length == 1
      run_local "ssh -l #{user} " + roles[target_role].servers.shift.to_s
    elsif not csshbin.empty?
      run_local "#{csshbin} -l #{user} " + roles[target_role].servers.join(' ')
    else
      puts "Atenção: Não foi possível encontrar nenhum dos executáveis csshX ou cssh. O acesso será a apenas um dos servidores da role #{target_role}."
      run_local "ssh -l #{user} " + roles[target_role].servers.shift.to_s
    end

end

namespace :ssh do
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
