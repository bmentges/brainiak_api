class brainiak::rpms {

    # RPMs
    include rpm::python27_generic_globo-2-7-3-2
    include rpm::python27-virtualenv_generic_globo-1-6-4
    include rpm::python27-setuptools_generic_globo-0-6c11-2
    include rpm::glb-curl       # Dependecia do pycurl
    include rpm::openldap-devel # Dependecia do pycurl
    include rpm::openssl-devel  # Dependecia do pycurl
    include rpm::libidn-devel   # Dependecia do pycurl

    package { "git_globo" :
        ensure => $::zone ? {
                    /dev|qa2/   => 'latest',
                    default     => 'purged'
                  }
    }
    
}
