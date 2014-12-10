class { 'neutron::agents::lbaas':
  interface_driver => hiera('CONFIG_NEUTRON_LBAAS_INTERFACE_DRIVER'),
  device_driver    => 'neutron.services.loadbalancer.drivers.haproxy.namespace_driver.HaproxyNSDriver',
  user_group       => 'haproxy',
  debug            => hiera('CONFIG_DEBUG_MODE'),
}
