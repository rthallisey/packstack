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


#-------------------------- step functions --------------------------

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

#def create_conductor_manifest(config, messages):
#    manifestfile = "%s_ironic.pp" % config['CONFIG_CONTROLLER_HOST']
#    manifestdata = getManifestTemplate("ironic_conductor.pp")
#    appendManifestFile(manifestfile, manifestdata)


