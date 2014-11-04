$ironic_cfg_ctrl_host = hiera('CONFIG_CONTROLLER_HOST')
#Should these be hardcoded?
class {"nova::compute::ironic":
  admin_user        => "admin",
  admin_passwd      => hiera('CONFIG_KEYSTONE_ADMIN_PW'),
  admin_url         => "http://${ironic_cfg_ctrl_host}:35357/v2.0",
  admin_tenant_name => "services",
  api_endpoint      => "http://${ironic_cfg_ctrl_host}:6385/v1",
}
