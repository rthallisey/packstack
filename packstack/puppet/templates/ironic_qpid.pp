
class {'ironic':
    rpc_backend    => 'ironic.openstack.common.rpc.impl_qpid',
    qpid_hostname  => "%(CONFIG_AMQP_HOST)s",
    qpid_port      => '%(CONFIG_AMQP_CLIENTS_PORT)s',
    qpid_protocol  => '%(CONFIG_AMQP_PROTOCOL)s',
    qpid_username  => '%(CONFIG_AMQP_AUTH_USER)s',
    qpid_password  => '%(CONFIG_AMQP_AUTH_PASSWORD)s',
    sql_connection => "mysql://ironic:%(CONFIG_IRONIC_DB_PW)s@%(CONFIG_MARIADB_HOST)s/ironic",
    verbose        => true,
    debug          => %(CONFIG_DEBUG_MODE)s,
    mysql_module   => '2.2',
}
