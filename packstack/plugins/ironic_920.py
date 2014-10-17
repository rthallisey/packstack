# -*- coding: utf-8 -*-

"""
Installs and configures nova
"""

import os
import uuid
import logging
import platform
import socket

from packstack.installer import basedefs, processors, utils, validators
from packstack.installer.exceptions import ScriptRuntimeError

from packstack.modules.common import filtered_hosts
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile, manifestfiles)


#------------------ Ironic installer initialization ------------------

PLUGIN_NAME = "OS-Ironic"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    if platform.linux_distribution()[0] == "Fedora":
        primary_netif = "em1"
        secondary_netif = "em2"
    else:
        primary_netif = "eth0"
        secondary_netif = "eth1"

    ironic_params = {
        "IRONIC": [
            {"CMD_OPTION": "ironic-db-passwd",
             "USAGE": "The password to use for the Ironic to access DB",
             "PROMPT": "Enter the password for the Ironic DB access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_IRONIC_DB_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},

            {"CMD_OPTION": "ironic-ks-passwd",
             "USAGE": ("The password to use for the Ironic to authenticate "
                       "with Keystone"),
             "PROMPT": "Enter the password for the Ironic Keystone access",
             "OPTION_LIST": [],
             "VALIDATORS": [validators.validate_not_empty],
             "DEFAULT_VALUE": "PW_PLACEHOLDER",
             "PROCESSORS": [processors.process_password],
             "MASK_INPUT": True,
             "LOOSE_VALIDATION": False,
             "CONF_NAME": "CONFIG_IRONIC_KS_PW",
             "USE_DEFAULT": False,
             "NEED_CONFIRM": True,
             "CONDITION": False},
        ],
    }

    ironic_groups = [
        {"GROUP_NAME": "IRONIC",
         "DESCRIPTION": "Ironic Options",
         "PRE_CONDITION": "CONFIG_IRONIC_INSTALL",
         "PRE_CONDITION_MATCH": "y",
         "POST_CONDITION": False,
         "POST_CONDITION_MATCH": True},
    ]
    for group in ironic_groups:
        params = ironic_params[group["GROUP_NAME"]]
        controller.addGroup(group, params)


def initSequences(controller):
    if controller.CONF['CONFIG_IRONIC_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Adding Ironic manifest entries',
         'functions': [create_manifest]},
        {'title': 'Adding Ironic Keystone manifest entries',
         'functions': [create_keystone_manifest]},
#        {'title': 'Adding Ironic Conductor manifest entries',
#         'functions': [create_conductor_manifest]},
#        {'title': 'Creating ssh keys for Ironic migration',
#         'functions': [create_ssh_keys]},
#        {'title': 'Gathering ssh host keys for Ironic migration',
#         'functions': [gather_host_keys]},
#        {'title': 'Adding Ironic Common manifest entries',
#         'functions': [create_common_manifest]},
    ]

    controller.addSequence("Installing OpenStack Ironic", [], [],
                           steps)


#------------------------- helper functions -------------------------

def check_ifcfg(host, device):
    """
    Raises ScriptRuntimeError if given host does not have give device.
    """
    server = utils.ScriptRunner(host)
    cmd = "ip addr show dev %s || ( echo Device %s does not exist && exit 1 )"
    server.append(cmd % (device, device))
    server.execute()


def bring_up_ifcfg(host, device):
    """
    Brings given device up if it's down. Raises ScriptRuntimeError in case
    of failure.
    """
    server = utils.ScriptRunner(host)
    server.append('ip link show up | grep "%s"' % device)
    try:
        server.execute()
    except ScriptRuntimeError:
        server.clear()
        cmd = 'ip link set dev %s up'
        server.append(cmd % device)
        try:
            server.execute()
        except ScriptRuntimeError:
            msg = ('Failed to bring up network interface %s on host %s.'
                   ' Interface should be up so Openstack can work'
                   ' properly.' % (device, host))
            raise ScriptRuntimeError(msg)


#-------------------------- step functions --------------------------

def create_ssh_keys(config, messages):
    migration_key = os.path.join(basedefs.VAR_DIR, 'ironic_migration_key')
    # Generate key
    local = utils.ScriptRunner()
    local.append('ssh-keygen -t rsa -b 2048 -f "%s" -N ""' % migration_key)
    local.execute()

    with open(migration_key) as fp:
        secret = fp.read().strip()
    with open('%s.pub' % migration_key) as fp:
        public = fp.read().strip()

    config['IRONIC_MIGRATION_KEY_TYPE'] = 'ssh-rsa'
    config['IRONIC_MIGRATION_KEY_PUBLIC'] = public.split()[1]
    config['IRONIC_MIGRATION_KEY_SECRET'] = secret


def gather_host_keys(config, messages):
    global compute_hosts

    for host in compute_hosts:
        local = utils.ScriptRunner()
        local.append('ssh-keyscan %s' % host)
        retcode, hostkey = local.execute()
        config['HOST_KEYS_%s' % host] = hostkey


def create_manifest(config, messages):
    manifestfile = "%s_ironic.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "ironic"))
    manifestdata = getManifestTemplate("ironic.pp")
    config['FIREWALL_SERVICE_NAME'] = "ironic"
    config['FIREWALL_PORTS'] = "['8773', '8774', '8775']"
    config['FIREWALL_CHAIN'] = "INPUT"
    config['FIREWALL_PROTOCOL'] = 'tcp'
    config['FIREWALL_ALLOWED'] = "'ALL'"
    config['FIREWALL_SERVICE_ID'] = "ironic"
    manifestdata += getManifestTemplate("firewall.pp")
    appendManifestFile(manifestfile, manifestdata)


def create_keystone_manifest(config, messages):
    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_ironic.pp")
    appendManifestFile(manifestfile, manifestdata)

def create_conductor_manifest(config, messages):
    manifestfile = "%s_ironic.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("ironic_conductor.pp")
    appendManifestFile(manifestfile, manifestdata)

def create_common_manifest(config, messages):
    global compute_hosts, network_hosts
    network_type = (config['CONFIG_NEUTRON_INSTALL'] == "y" and
                    'neutron' or 'nova')
    network_multi = len(network_hosts) > 1
    dbacces_hosts = set([config.get('CONFIG_CONTROLLER_HOST')])
    dbacces_hosts |= network_hosts

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_nova.pp"):
            host, manifest = manifestfile.split('_', 1)
            host = host.strip()

            if host in compute_hosts and host not in dbacces_hosts:
                # we should omit password in case we are installing only
                # nova-compute to the host
                perms = "nova"
            else:
                perms = "nova:%(CONFIG_NOVA_DB_PW)s"
            sqlconn = "mysql://%s@%%(CONFIG_MARIADB_HOST)s/nova" % perms
            config['CONFIG_NOVA_SQL_CONN'] = sqlconn % config

            # for nova-network in multihost mode each compute host is metadata
            # host otherwise we use api host
            if (network_type == 'nova' and network_multi and
                    host in compute_hosts):
                metadata = host
            else:
                metadata = config['CONFIG_CONTROLLER_HOST']
            config['CONFIG_NOVA_METADATA_HOST'] = metadata

            data = getManifestTemplate(get_mq(config, "nova_common"))
            data += getManifestTemplate("nova_common.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)

def create_neutron_manifest(config, messages):
    if config['CONFIG_NEUTRON_INSTALL'] != "y":
        return

    virt_driver = 'ironic.virt.libvirt.vif.LibvirtGenericVIFDriver'
    config['CONFIG_IRONIC_LIBVIRT_VIF_DRIVER'] = virt_driver

    for manifestfile, marker in manifestfiles.getFiles():
        if manifestfile.endswith("_ironic.pp"):
            data = getManifestTemplate("ironic_neutron.pp")
            appendManifestFile(os.path.split(manifestfile)[1], data)
