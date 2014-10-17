# ironic::keystone::auth
class {"ironic::keystone::auth":
    region => "%(CONFIG_KEYSTONE_REGION)s",
    password => "%(CONFIG_IRONIC_KS_PW)s",
    public_address => "%(CONFIG_CONTROLLER_HOST)s",
    admin_address => "%(CONFIG_CONTROLLER_HOST)s",
    internal_address => "%(CONFIG_CONTROLLER_HOST)s",
}

