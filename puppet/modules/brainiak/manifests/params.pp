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

    $projeto                = 'brainiak'
    $usuario                = 'brainiak'
    $grupo                  = 'brainiak'
    $projeto_home_dir       = "${supso::dir_opt::dir}/${projeto}"
    $virtualenv_dir         = "${projeto_home_dir}/virtualenv"
    $projeto_deploybe_dir   = "/mnt/projetos/deploy-be/${projeto}"
    $projeto_logsunix_dir   = $::zone ? { prod => "/mnt/logsunix/${projeto}", default => 'purge' }

    $gunicorn_num_processes = $::zone ? { /(prod|qa2)/    => 5, default => 2 }
    $gunicorn_loglevel      = $::zone ? { /(prod|qa2)/ => 'INFO', default => 'DEBUG' }
    $gunicorn_log_keep      = $::zone ? { prod => 7, default => 1 }
    
}
