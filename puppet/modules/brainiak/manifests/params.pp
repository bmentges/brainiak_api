# = Class: brainiak::params
#
# Esta classe contém as variáveis globais do projeto.
# 
# == Author: Diogo Kiss <diogokiss@corp.globo.com> e Marcelo Monteiro <m.monteiro@corp.globo.com>.
#
# == Parameters:
#
#   Nenhum parametro é necessário para esta classe.
#
# == Actions:
#
#    Nenhuma ação é executada por esta classe.
#
# == Sample Usage:
#
#  myclass::be inherits brainiak::params
#

class brainiak::params {

    include supso::vars

    $projeto                    = 'brainiak'
    $usuario                    = $projeto
    $grupo                      = $projeto
    $projeto_host               = "${projeto}.semantica.${supso::vars::dns_interno}"
    $projeto_home_dir           = "${supso::dir_opt::dir}/${projeto}"
    $projeto_log_dir            = "${supso::dir_opt::dir}/logs/${projeto}"
    $projeto_deploybe_dir       = "/mnt/projetos/deploy-be/${projeto}"
    $virtualenv_dir             = "${projeto_home_dir}/virtualenv"
    $projeto_logsunix_dir       = $::zone ? { prod => "/mnt/logsunix/${projeto}", default => 'purge' }
    $log_keep                   = $::zone ? { prod => 7, default => 1 }

    $nginx_home_dir             = "${projeto_home_dir}/nginx-be"
    $nginx_proxycache_dir       = "${projeto_home_dir}/nginx-be/proxy_cache"
    $nginx_proxytemp_dir        = "${projeto_home_dir}/nginx-be/proxy_temp"
    $nginx_clientbodytemp_dir   = "${projeto_home_dir}/nginx-be/client_body_temp"

    $gunicorn_num_processes     = $::zone ? { /(prod|qa2)/ => 5, default => 2 }
    $gunicorn_debug             = $::zone ? { /(dev|qa1)/ => 'True', default => 'False' }
    $gunicorn_loglevel          = $::zone ? { /(prod|qa2)/ => 'INFO', default => 'DEBUG' }

}
