
class {'ironic':
    rpc_backend => 'ironic.openstack.common.rpc.impl_kombu',
    rabbit_host => "%(CONFIG_AMQP_HOST)s",
    rabbit_port => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    rabbit_user => '%(CONFIG_AMQP_AUTH_USER)s',
    rabbit_password => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    database_connection => 'mysql://ironic:%(CONFIG_IRONIC_DB_PW)s@%(CONFIG_MARIADB_HOST)s/ironic',
    debug  => True,
    verbose  => True,
}
