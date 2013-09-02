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

    $projeto            = 'brainiak'
    $usuario            = 'brainiak'
    $grupo              = 'brainiak'
    $projeto_home_dir   = "${supso::dir_opt::dir}/${projeto}"
    $virtualenv_dir     = "${projeto_home_dir}/virtualenv"
    $git_projeto        = 'http://ngit.globoi.com/brainiak'
    
}
