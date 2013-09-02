# = Class: brainiak::be
#
# Cria o ambiente API para o Brainiak de Semântica.
# É uma API REST que serve como camada de abstração para acesso ao Virtuoso.
#
# Author: Jefferson Braga <jefferson@corp.globo.com>, Diogo Kiss <diogokiss@corp.globo.com> e Marcelo Monteiro <m.monteiro@corp.globo.com>.
#
# == Parameters:
#
#   Nenhum parametro é necessário para esta classe.
#
# == Actions:
#
#   Implementa toda a configuração de ambiente necessária ao projeto.
#   - Instalar RPMs.
#   - Criar usuarios, diretorios, links, initscripts e aliases.
#   - Montar filer.
#
# == Sample Usage:
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

    # TODO: GUnicor
    # TODO: Nginx
    # TODO: Checar expurgo e rotacionamento de logs

}

# EOF
