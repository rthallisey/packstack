
$deploy_kernel = 'glance://deploy_kernel_uuid'
$deploy_ramdisk = 'glance://deploy_ramdisk_uuid'
#$rabbit_vhost = '/'
#$rabbit_hosts = ['rabbitmq:5672']
#$db_name = 'ironic'


class { 'ironic':
  #    db_name => $db_name,
  auth_host => "%(CONFIG_CONTROLLER_HOST)s",
  admin_password => "%(CONFIG_IRONIC_KS_PW)s",
#  rabbit_virtual_host => $rabbit_vhost,
#  rabbit_hosts => $rabbit_hosts,

}
class { 'ironic::api': }

class { 'ironic::conductor': }

class { 'ironic::drivers::ipmi': }

class { 'ironic::drivers::pxe':
  deploy_kernel => $deploy_kernel,
  deploy_ramdisk => $deploy_ramdisk,
}
