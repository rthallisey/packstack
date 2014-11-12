
class {"nova::compute::ironic":
  admin_user        => "admin",
  admin_passwd      => "%(CONFIG_KEYSTONE_ADMIN_PW)s",
  admin_url         => "http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0",
  admin_tenant_name => "services",
  api_endpoint      => "http://%(CONFIG_CONTROLLER_HOST)s:6385/v1",
}
