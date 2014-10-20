#$db_host = 'db'
#$db_username = 'ironic'
#$db_password = 'password'
#$rabbit_user = 'ironic'
#$rabbit_password = 'ironic'
#$rabbit_port = '5672'
#$glance_api_servers = 'glance:9292'

$deploy_kernel = 'glance://deploy_kernel_uuid'
$deploy_ramdisk = 'glance://deploy_ramdisk_uuid'
$rabbit_vhost = '/'
$rabbit_hosts = ['rabbitmq:5672']
#$db_name = 'ironic'

node db {
  class { 'mysql::server':
    config_hash => {
      'bind_address' => '0.0.0.0'
    }
  }

  class { 'mysql::ruby': }

  class { 'ironic::db::mysql':
    password => $db_password,
    dbname => $db_name,
    user => $db_username,
    host => $clientcert,
    allowed_hosts => ['controller'],
  }
}

node controller {
  class { 'ironic':
#    db_name => $db_name,
    rabbit_virtual_host => $rabbit_vhost,
    rabbit_hosts => $rabbit_hosts,

#    db_password => $db_password,
#    db_user => $db_username,
#    db_host => $db_host,
#    rabbit_password => $rabbit_password,
#    rabbit_userid => $rabbit_user,
#    glance_api_servers => $glance_api_servers,
  }
  class { 'ironic::api': }

  class { 'ironic::conductor': }

  class { 'ironic::drivers::ipmi': }

  class { 'ironic::drivers::pxe':
    deploy_kernel => $deploy_kernel,
    deploy_ramdisk => $deploy_ramdisk,
  }
}


