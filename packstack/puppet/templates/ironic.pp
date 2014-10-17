
class { 'ironic::api':
       keystone_host     => '%(CONFIG_CONTROLLER_HOST)s',
       keystone_password => '%(CONFIG_IRONIC_KS_PW)s',
}

class { 'ironic::conductor':
}


