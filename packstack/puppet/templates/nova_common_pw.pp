
# Ensure Firewall changes happen before nova services start
# preventing a clash with rules being set by nova-compute and nova-network
Firewall <| |> -> Class['nova']

nova_config{
  'DEFAULT/sql_connection': value => hiera('CONFIG_NOVA_SQL_CONN_PW');
  'DEFAULT/metadata_host':  value => hiera('CONFIG_CONTROLLER_HOST');
}
