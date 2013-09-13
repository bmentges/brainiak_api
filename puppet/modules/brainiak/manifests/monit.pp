# = Class: brainiak::monit
#
#   Esta classe contém as monitorações dos serviços do projeto.
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
#   - Criação das monitorações necessárias aos serviços do projeto.
#
# == Sample Usage
#
#   include brainiak::monit
#
class brainiak::monit {

    if $::zone != 'prod' {
    
        monit_globo::http_server { "${brainiak::params::projeto}-gunicorn-be":
          pidfile   => "/opt/logs/${brainiak::params::projeto}/gunicorn-be/gunicorn-be.pid",
          uri       => '/healthcheck',
          port      => $brainiak::params::gunicorn_bind_port,
          alert     => $brainiak::params::monit_notification_mail,
          require   => Infra::Gunicorn['GUnicorn - Brainiak']
        }

        monit_globo::http_server { "${brainiak::params::projeto}-nginx-be":
          pidfile   => "/opt/logs/${brainiak::params::projeto}/nginx-be/nginx-be.pid",
          uri       => '/healthcheck',
          port      => $brainiak::params::nginx_bind_port,
          hostname  => $brainiak::params::projeto_host,
          alert     => $brainiak::params::monit_notification_mail,
          require   => Infra::Nginx['Nginx - Brainiak']
        }
        
    }

}
