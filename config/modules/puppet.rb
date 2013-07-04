namespace :puppet  do

def onetime
  
  set :hostname, `hostname`
  set :user, "puppet"
  set :pp_params, ""
  default_run_options[:pty] = true

  # Atualiza o submodulo puppet/deploy-module
  system "git submodule update --init"

  # Máquinas de deploy tem chave SSL no puppet master
  if not hostname.strip.eql?("riolb315") and not hostname.strip.eql?("riolb316")
      if puppetmaster_env.to_s =~ /(dev|qa1|qa2|qa)/
        set :password, 'puppet'
      else
        set(:password){ Capistrano::CLI.password_prompt("Senha para o usuário #{user}: ") }
      end
      set :pp_params, "-p #{password}"
  end

  # Deploy para o puppetmaster
  system <<-EOF
      cd puppet/deploy-module/deploy/ &&
      fab #{puppetmaster_env} deploy #{pp_params}
  EOF

  # Disconnect
  sessions.values.each {|session| session.close}
  sessions.clear
  
  puts "Sleeping 3s..."
  sleep 3
  
  # Run puppet-setup
  sudo "/opt/local/bin/puppet-setup"
  
end

  desc "Executa  puppet_onetime no APP"
  task :be, :roles => :role_be do
    onetime
  end

  desc "Executa  puppet_onetime no FE"
  task :fe, :roles => :role_fe do
    onetime
  end

  desc "Executa  puppet_onetime em todos servidores"
  task :all, :roles => [ :restart ] do
    onetime
  end

end
