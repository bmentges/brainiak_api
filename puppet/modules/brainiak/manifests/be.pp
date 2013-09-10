# = Class: brainiak::be
#
# Cria o ambiente API para o Brainiak de Semântica.
# É uma API REST que serve como camada de abstração para acesso ao Virtuoso.
#
# == Authors
#
#   Jefferson Braga <jefferson@corp.globo.com>
#   Diogo Kiss <diogokiss@corp.globo.com>
#   Marcelo Monteiro <m.monteiro@corp.globo.com>.
#
# == Parameters
#
#   Nenhum parametro é necessário para esta classe.
#
# == Actions
#
#   Implementa toda a configuração de ambiente necessária ao projeto.
#   - Instalar RPMs.
#   - Criar usuarios, diretorios, links, initscripts e aliases.
#   - Montar filer.
#
# == Sample Usage
#
#   include brainiak::be
#

class brainiak::be inherits brainiak::params {

    include supso::dir_opt

    include supso::users
    realize Supso::Users::Create['suporte']
    realize Supso::Users::Create['watcher']
    realize Supso::Users::Create[$brainiak::params::usuario]

    include supso::ldap
    realize Supso::Ldap::Projeto[$brainiak::params::projeto]

    include supso::filer
    Supso::Filer::Mount <| projeto == 'brainiak' and tipo == 'dbpasswd' |>
    Supso::Filer::Mount <| projeto == 'brainiak' and tipo == 'be' |>

    include brainiak::dirs
    include brainiak::rpms
    include brainiak::monit
    include tdi

    virtualenv { $brainiak::params::virtualenv_dir:
        ensure              => present,
        projeto             => $brainiak::params::projeto,
        usuario             => $brainiak::params::usuario,
        grupo               => $brainiak::params::grupo,
        python_prefix       => '/opt/generic/python27',
        requirements_file   => 'requirements.txt',
        use_nodeps          => false, # With great power comes great responsibility.
        file_search_dir     => $brainiak::params::projeto,
        require             => Package['python27-virtualenv_generic_globo'],
    }

    infra::gunicorn { 'GUnicorn - Brainiak':
        projeto                 => $brainiak::params::projeto,
        instancia               => 'be',
        dir                     => "${brainiak::params::projeto_home_dir}/gunicorn-be",
        projeto_usuario         => $brainiak::params::usuario,
        projeto_grupo           => $brainiak::params::grupo,
        instancia_usuario       => $brainiak::params::usuario,
        instancia_grupo         => $brainiak::params::grupo,
        app_dir                 => "${brainiak::params::projeto_deploybe_dir}/app/current",
        python_prefix           => $brainiak::params::virtualenv_dir,
        log_dest_dir            => $brainiak::params::projeto_logsunix_dir,
        log_keep                => $brainiak::params::log_keep,
        gunicorn_bin            => 'gunicorn',
        gunicorn_processes      => $brainiak::params::gunicorn_num_processes,
        gunicorn_loglevel       => $brainiak::params::gunicorn_loglevel,
        gunicorn_debug          => $brainiak::params::gunicorn_debug,
        gunicorn_bind_porta     => $brainiak::params::gunicorn_bind_port,
        settings_file           => "${brainiak::params::projeto}/settings",
        gunicorn_cmd_parameters => '-k tornado brainiak.server:application',
        require                 => Virtualenv[$brainiak::params::virtualenv_dir]
    }

    include infra::nginx::vars
    infra::nginx { 'Nginx - Brainiak':
        projeto                 => $brainiak::params::projeto,
        instancia               => 'be',
        rpm                     => 'nginx_generic_globo',
        rpm_dir                 => '/opt/generic/nginx',
        rpm_versao              => '1.2.8-0.el5',
        instancia_usuario       => 'nobody',
        instancia_grupo         => 'nobody',
        projeto_usuario         => $brainiak::params::usuario,
        projeto_grupo           => $brainiak::params::grupo,
        log_dest_dir            => $brainiak::params::projeto_logsunix_dir,
        log_filer               => "riofb18a:/vol/vol3/glb_${projeto}",
        log_keep                => $brainiak::params::log_keep
    }

}

# EOF
