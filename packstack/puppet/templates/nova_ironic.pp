nova_config {

}

class {"nova::ironic":
  "ironic/admin_username": value => "%(CONFIG_NEUTRON_KS_PW)s",
  "ironic/admin_password": value => "%(CONFIG_NEUTRON_KS_PW)s",
  "ironic/admin_url": value => "http://%(CONFIG_CONTROLLER_HOST)s:35357/v2.0",
  "ironic/admin_tenant_name": value => "services",
  "ironic/api_endpoint": value => "http://IRONIC_NODE:6385/v1",  
}
