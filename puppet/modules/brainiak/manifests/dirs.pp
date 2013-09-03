# = Class: brainiak::dirs
#
#   Esta classe contém as definições de diretórios e suas respectivas permissões.
# 
# == Authors
#
#   Diogo Kiss <diogokiss@corp.globo.com>
#   Marcelo Monteiro <m.monteiro@corp.globo.com>.
#
# == Parameters
#
#   Nenhum parametro é necessário para esta classe.
#
# == Actions
#
#   - Criação dos diretórios necessários ao projeto.
#
# == Sample Usage
#
#   include brainiak::dirs
#

class brainiak::dirs {

    file { $brainiak::params::projeto_home_dir:
        ensure  => directory,
        owner   => $brainiak::params::usuario,
        group   => $brainiak::params::grupo,
        mode    => 0755
    }

    file { $brainiak::params::nginx_home_dir:
        ensure  => directory,
        owner   => root,
        group   => root,
        mode    => 0755,
        require => File[$brainiak::params::projeto_home_dir]
    }

    file { $brainiak::params::nginx_proxycache_dir:
        ensure  => directory,
        owner   => nobody,
        group   => nobody,
        mode    => 0755,
        require => File[$brainiak::params::nginx_home_dir]
    }

    file { $brainiak::params::nginx_proxytemp_dir:
        ensure  => directory,
        owner   => nobody,
        group   => nobody,
        mode    => 0755,
        require => File[$brainiak::params::nginx_home_dir]
    }

    file { $brainiak::params::nginx_clientbodytemp_dir:
        ensure  => directory,
        owner   => nobody,
        group   => nobody,
        mode    => 0755,
        require => File[$brainiak::params::nginx_home_dir]
    }
    
}
