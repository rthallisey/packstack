
class { 'ironic::api':
       keystone_host     => '%(CONFIG_CONTROLLER_HOST)s',
       keystone_password => '%(CONFIG_IRONIC_KS_PW)s',
}

class { 'ironic::conductor':
}

class { 'ironic::keystone::domain':
      auth_url          => 'http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0',
      keystone_admin    => 'admin',
      keystone_password => '%(CONFIG_KEYSTONE_ADMIN_PW)s',
      keystone_tenant   => 'admin',
      domain_name       => '%(CONFIG_IRONIC_DOMAIN)s',
      domain_admin      => '%(CONFIG_IRONIC_DOMAIN_ADMIN)s',
      domain_password   => '%(CONFIG_IRONIC_DOMAIN_PASSWORD)s',
}

