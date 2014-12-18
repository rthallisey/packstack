$glance_ks_pw        = hiera('CONFIG_GLANCE_DB_PW')
$glance_mariadb_host = hiera('CONFIG_MARIADB_HOST')
$ironic_enabled      = hiera('CONFIG_IRONIC_INSTALL')
$keystone_password   = hiera('CONFIG_GLANCE_KS_PW')
$auth_host           = hiera('CONFIG_CONTROLLER_HOST')
$known_stores        = ['glance.store.filesystem.Store','glance.store.http.Store','glance.store.swift.Store']

if $ironic_enabled {
  $show_image_direct_url = true
} else {
  $show_image_direct_url = false
}

class { 'glance::api':
  auth_host             => $auth_host,
  keystone_tenant       => 'services',
  keystone_user         => 'glance',
  keystone_password     => $keystone_password,
  pipeline              => 'keystone',
  database_connection   => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  known_stores          => $known_stores,
  show_image_direct_url => $show_image_direct_url,
  verbose               => true,
  debug                 => hiera('CONFIG_DEBUG_MODE'),
}

class { 'glance::registry':
  auth_host           => $auth_host,
  keystone_tenant     => 'services',
  keystone_user       => 'glance',
  keystone_password   => $keystone_password,
  database_connection => "mysql://glance:${glance_ks_pw}@${glance_mariadb_host}/glance",
  verbose             => true,
  debug               => hiera('CONFIG_DEBUG_MODE'),
}


if $ironic_enabled {
  class { 'glance::backend::swift':
    swift_store_create_container_on_put => true,
    swift_store_key                     => $keystone_password,
    swift_store_user                    => 'services:glance',
    swift_store_auth_address            => "http://${auth_host}:5000/v2.0/",
 }
}
