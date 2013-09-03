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
    realize Supso::Users::Create[$usuario]

    include supso::ldap
    realize Supso::Ldap::Projeto[$projeto]

    include supso::filer
    Supso::Filer::Mount <| projeto == 'brainiak' and tipo == 'dbpasswd' |>

    virtualenv { $virtualenv_dir:
        ensure              => present,
        projeto             => $projeto,
        usuario             => $usuario,
        grupo               => $grupo,
        python_prefix       => '/opt/generic/python27',
        requirements_file   => 'requirements.txt',
        file_search_dir     => $projeto,
        require             => Package['python27-virtualenv_generic_globo'],
    }

    # TODO: GUnicorn  
    infra::gunicorn { "GUnicorn - Brainiak":
        projeto             => $projeto,
        instancia           => 'be',
        dir                 => "${projeto_home_dir}/gunicorn-be",
        projeto_usuario     => $usuario,
        projeto_grupo       => $grupo,
        instancia_usuario   => $usuario,
        instancia_grupo     => $grupo,
        app_dir             => "${projeto_deploybe_dir}/app/current",
        python_prefix       => $virtualenv_dir,
        log_dest_dir        => $projeto_logsunix_dir,
        log_keep            => $gunicorn_log_keep,
        gunicorn_bin        => 'gunicorn',
        gunicorn_processes  => $gunicorn_num_processes,
        gunicorn_loglevel   => $gunicorn_loglevel,
        gunicorn_debug      => $gunicorn_debug,
        gunicorn_cmd_parameters => '-k tornado brainiak.server:application',
        settings_file       => 'settings',
        dbpasswd            => true,
        use_mount_virtual   => $projeto,
        gunicorn_dbpasswd_conf => $dbpasswd_conf_file,
        sudoers             => $api_semantica::defs::sudoers,
        autostart           => true,
        require             => Virtualenv[$python_virtualenv_dir]
    }
    
    # TODO: Nginx
    # TODO: Checar expurgo e rotacionamento de logs

}

# EOF
