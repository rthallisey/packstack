
class { 'ironic::api':
  auth_host => "%(CONFIG_CONTROLLER_HOST)s",
  admin_password => "%(CONFIG_IRONIC_KS_PW)s",
  auth_url => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
}

class { 'ironic::conductor':
  auth_url => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
}
