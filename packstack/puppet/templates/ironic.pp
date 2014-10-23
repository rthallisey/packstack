ironic_config {
  "glance/glance_host": value => "%(CONFIG_STORAGE_HOST)s";
}

class { 'ironic::api':
  auth_host => "%(CONFIG_CONTROLLER_HOST)s",
  admin_password => "%(CONFIG_IRONIC_KS_PW)s",
}

class { 'ironic::conductor':
}

