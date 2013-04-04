# = Class: brainiak::be
#
# TODO: Cria o ambiente API para o BRAINIAK de SEMANTICA
#       A missao dele eh receber os request HTTP e conversar com o virtuoso. Sera uma framework
#       OBS: Ele utiliza o nginx do modulo api_semantica. Com isso eu forco a importacao desse modulos
#
# Author: Jefferson Braga (jefferson@corp.globo.com) e TimeInfra
#
# == Parameters:
#
#   Nenhum parametro eh necessario para esta class.
#
# == Actions:
#
#   Criar toda a environment para o projeto
#   - Instala RPMs
#   - Criar usuarios, diretorios, links, initscripts e Alias
#   - Monta filer
#
# == Sample Usage:
#
#   include brainiak::be
#
class brainiak::be inherits api_semantica::be {

  include aliases::all

  $app_name = 'brainiak'
  $basedir  = "/opt/${projeto}/${app_name}"

  $git_projeto            = 'http://ngit.globoi.com/brainiak'
  $python_virtualenv_dir  = "${basedir}/virtualenv"

  ## Instalo 1 virtualenv separado da api_semantica pois serao outros eggs
  virtualenv { $python_virtualenv_dir:
    ensure          => present,
    projeto         => $app_name,
    usuario         => $usuario,
    grupo           => $grupo,
    use_nodeps      => false, ## A equipe prefere nao usar.
    python_prefix   => '/opt/generic/python27',
    require         => Package['python27-virtualenv_generic_globo'],
  }

  case $::zone {
    /(dev|qa1)/: {
      $gunicorn_debug = 'True'
    }
    default: {
      $gunicorn_debug = 'False'
    }
  }
  ## Instala o gunicorn para usa o tornado utilizado pelo brainiak.
  ## O nginx desse projeto eh instalado pela api_semantica::be (inherits)
  infra::gunicorn { "Gunicorn+Tornado - ${projeto}":
    projeto             => $app_name,
    instancia           => 'be',
    dir                 => "${basedir}/gunicorn-be",
    projeto_usuario     => $usuario,
    projeto_grupo       => $grupo,
    instancia_usuario   => $usuario,
    instancia_grupo     => $grupo,
    ip_bind             => '0.0.0.0',
    python_prefix       => $python_virtualenv_dir,
    app_dir             => "${brainiak_filer_app_dir}/current",
    log_dest_dir        => $mount_filer_logunix,
    log_keep            => $gunicorn_log_keepday,
    gunicorn_bin        => 'gunicorn',
    gunicorn_bind_porta => '8035',
    gunicorn_processes  => $gunicorn_processes,
    gunicorn_loglevel   => $gunicorn_loglevel,
    gunicorn_debug      => $gunicorn_debug,
    gunicorn_cmd_parameters => '-k tornado brainiak.server:application',
    settings_file       => 'settings',
    dbpasswd            => false, ## Coloquei false pq o api_semantica::be ja faz esse trabalho
    require             => Virtualenv[$python_virtualenv_dir]
  }

  ## Arquivo de senhas para autenticacao na api
  ## Foi colocado aqui pq nao acessamos banco e nao fazia parte do sprint criar um autenicacao em BANCO
  ## Isso foi conversado com Bernado e Carolo sobre a solucao
  file {
    ## Para na primeira vez q rodar nao dar erro, eu crio a pastar que deveria ser do capistrano
    ## Diretorio da APP
    $brainiak_filer_dir:
      ensure  => directory,
      owner   => $usuario,
      group   => $grupo,
      require => [
        Mount_filer_projeto["${projeto}-be"],
        Supso::Users::Create[$usuario],
      ];

    ## Diretorio da app. Onde serah jogado os deploys
    $brainiak_filer_app_dir:
      ensure  => directory,
      owner   => $usuario,
      group   => $grupo,
      require => File[$brainiak_filer_dir];
  }


  ## Essa parte é para apagar gunicorn V2 do api-semantica pois agora o V2 e do Brainiak
  service{ 'api_semantica-gunicorn-be2':
    ensure => stopped;
  }
  file {
    '/etc/init.d/api_semantica-gunicorn-be2':
      ensure  => absent,
      require => Service['api_semantica-gunicorn-be2'];
    '/opt/etc/profile.d/api_semantica-gunicorn-be2.sh':
      ensure  => absent;
    '/opt/etc/profile.d/django-manage-api_semantica-be2.sh':
      ensure  => absent;
    '/opt/api_semantica/gunicorn-be2':
      ensure  => absent,
      recurse => true, # enable recursive directory management
      purge   => true, # purge all unmanaged junk
      force   => true, # also purge subdirs and links etc.
      require => File['/etc/init.d/api_semantica-gunicorn-be2'];
    '/opt/api_semantica/app2':
      ensure  => absent;
  }
}

# EOF
