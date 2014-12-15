$endpoint_url = hiera('CONFIG_CONTROLLER_HOST')

ironic_config {
  'glance/glance_host':        value => hiera('CONFIG_STORAGE_HOST');
  'glance/swift_endpoint_url': value => "http://${endpoint_url}:8080";
  'glance/swift_api_version':  value => "v1";
}

class { 'ironic::api':
  auth_host          => hiera('CONFIG_CONTROLLER_HOST'),
  admin_password     => hiera('CONFIG_IRONIC_KS_PW'),
  enabled_drivers    => hiera('CONFIG_IRONIC_BACKEND_DRIVERS'),
  swift_temp_url_key => hiera('CONFIG_IRONIC_SWIFT_TEMP_URL_KEY'),
}

class { 'ironic::client': }

class { 'ironic::conductor': }
