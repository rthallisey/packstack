class {"ironic::db::mysql":
  password      => "%(CONFIG_IRONIC_DB_PW)s",
  host          => "%%",
  allowed_hosts => "%%",
  charset       => "utf8",
  mysql_module  => '2.2',
}
