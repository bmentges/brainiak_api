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

#
# Aqui eu crio apenas o virtualenv com seus requirements específicos
#
# O gunicorn e nginx estão definidos no módulo api_semantica
#

class brainiak::be {

  include supso::dir_opt
  include api_semantica::defs

  #$projeto = 'brainiak'
  $projeto = 'api_semantica'
  $usuario = $api_semantica::defs::usuario
  #$basedir = "${supso::dir_opt::dir}/${projeto}"
  $basedir = "${supso::dir_opt::dir}/${projeto}/brainiak"
  $python_virtualenv_dir  = "${basedir}/virtualenv"
  $git_projeto            = 'http://ngit.globoi.com/brainiak'

  include supso::ldap
  realize Supso::Ldap::Projeto[$projeto]

  # Filer
  include supso::filer
  Supso::Filer::Mount <| projeto == 'brainiak' and tipo == 'dbpasswd' |>

  virtualenv { $python_virtualenv_dir:
    ensure              => present,
    projeto             => $projeto,
    usuario             => $usuario,
    grupo               => $usuario,
    use_nodeps          => false, ## A equipe prefere nao usar.
    python_prefix       => '/opt/generic/python27',
    requirements_file   => "requirements.txt",
    file_search_dir     => "brainiak",
    require             => Package['python27-virtualenv_generic_globo'],
  }
}

# EOF
