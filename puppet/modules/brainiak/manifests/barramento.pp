#
#
#

class brainiak::barramento {
  include supso::users
  Supso::Users::Create <| user == 'portal' |>
  Supso::Users::Create <| user == 'portal_' |>
  Supso::Users::Create <| user == 'suporte' |>
  Supso::Users::Create <| user == 'watcher' |>

  include infra::scripts::aliases_all
  include supso::vars

  $owner_file                 = 'portal'
  $owner_app                  = 'portal_'

  $project                    = 'brainiak'
  $java_console_port          = 8204
  $log_destdir                = 'purge'
  $use_virtual_topic          = true
  $use_redundancy             = true

  $java_console = "-Dcom.sun.management.jmxremote.port=${java_console_port} -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
  $domain = $supso::vars::dns_interno
  case $::zone {
    dev,qa1: {
      $barramento_mcaddr  = undef
    }
    qa2: {
      if $use_redundancy {
        $barramento_mcaddr  = undef # Por enquanto, sem IP reservado
        # '239.10.249.6'  # XXX
      } else {
        $barramento_mcaddr  = undef
      }
    }
    staging,prod: {
      $barramento_mcaddr  = undef
    }
    default: {
      fail( "Zona inválida: '${::zone}'" )
    }
  }
  case $::zone {
    dev,qa1,staging: {
      $java_options       = "-Xms128m -Xmx128m -XX:MaxPermSize=64m ${java_console}"
      $log_keep           = 2
      $memorylimit_mb     = 8
      $storelimit_mb      = 200
      $templimit_mb       = 100
    }
    prod,qa2: {
      $java_options       = "-Xms6g -Xmx6g -XX:MaxPermSize=128m ${java_console}"
      $log_keep           = 10
      $memorylimit_mb     = 128
      $storelimit_mb      = 10240
      $templimit_mb       = 1024
    }
    default: {
      fail( "Zona inválida: '${::zone}'" )
    }
  }

  infra::activemq { $project:
    projeto             => $project,
    usuario             => $owner_file,
    usuario_nologin     => $owner_app,
    multicast_connector => $barramento_mcaddr,
    memorylimit_mb      => $memorylimit_mb,
    storelimit_mb       => $storelimit_mb,
    templimit_mb        => $templimit_mb,
    autostart           => true,
    java_options        => $java_options,
    log_destdir         => $log_destdir,
    log_keep            => $log_keep,
    require             => Supso::Users::Create[$owner_file,$owner_app],
  }
}

# EOF
