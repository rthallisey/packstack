# -*- coding: utf-8 -*-

"""
Installs and configures ironic
"""

#import os
import uuid
#import logging
#import platform
#import socket

from packstack.installer import utils, validators #basedefs, processors, utils, validators
#from packstack.installer.exceptions import ScriptRuntimeError

#from packstack.modules.common import filtered_hosts
from packstack.modules.shortcuts import get_mq
from packstack.modules.ospluginutils import (getManifestTemplate,
                                             appendManifestFile, #manifestfiles,
                                             createFirewallResources)

#------------------ Ironic installer initialization ------------------

PLUGIN_NAME = "OS-Ironic"
PLUGIN_NAME_COLORED = utils.color_text(PLUGIN_NAME, 'blue')


def initConfig(controller):
    ironic_params = [
        {"CONF_NAME": "CONFIG_IRONIC_DB_PW",
         "CMD_OPTION": "os-ironic-db-passwd",
         "PROMPT": "Enter the password for the Ironic MySQL user",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_KS_PW",
         "CMD_OPTION": "os-ironic-ks-passwd",
         "USAGE": ("The password to use for Ironic to authenticate "
                   "with Keystone"),
         "PROMPT": "Enter the password for Ironic Keystone access",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_NOVA_USER",
         "CMD_OPTION": "os-ironic-nova-user",
         "USAGE": "The user to use when Ironic connects to Nova",
         "PROMPT": "Enter the user for Ironic to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "admin",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_NOVA_TENANT",
         "CMD_OPTION": "os-ironic-nova-tenant",
         "USAGE": "The tenant to use when Ironic connects to Nova",
         "PROMPT": "The tenant for Ironic to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [validators.validate_not_empty],
         "DEFAULT_VALUE": "service",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_NOVA_PW",
         "CMD_OPTION": "os-ironic-nova-passwd",
         "USAGE": "The password to use when Ironic connects to Nova",
         "PROMPT": "The password for Ironic to use to connect to Nova",
         "OPTION_LIST": [],
         "VALIDATORS": [],
         "DEFAULT_VALUE": "PW_PLACEHOLDER",
         "PROCESSORS": [processors.process_password],
         "MASK_INPUT": True,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": False,
         "NEED_CONFIRM": True,
         "CONDITION": False},

        {"CONF_NAME": "CONFIG_IRONIC_DATASTORES",
         "CMD_OPTION": "os-ironic-datastores",
         "USAGE": "A comma-separated list of Ironic datastores",
         "PROMPT": "Enter a comma-separated list of Ironic datastores",
         "OPTION_LIST": ['cassandra', 'couchbase', 'mongodb', 'mysql',
                         'postgresql', 'redis'],
         "VALIDATORS": [validators.validate_multi_options],
         "DEFAULT_VALUE": "redis",
         "MASK_INPUT": False,
         "LOOSE_VALIDATION": False,
         "USE_DEFAULT": True,
         "NEED_CONFIRM": False,
         "CONDITION": False},
    ]

    ironic_group = {"GROUP_NAME": "IRONIC",
                    "DESCRIPTION": "Ironic Options",
                    "PRE_CONDITION": "CONFIG_IRONIC_INSTALL",
                    "PRE_CONDITION_MATCH": "y",
                    "POST_CONDITION": False,
                    "POST_CONDITION_MATCH": True}

    controller.addGroup(ironic_group, ironic_params)


def initSequences(controller):
    if controller.CONF['CONFIG_IRONIC_INSTALL'] != 'y':
        return

    steps = [
        {'title': 'Adding Ironic Keystone manifest entries',
         'functions': [create_keystone_manifest]},
        {'title': 'Adding Ironic manifest entries',
         'functions': [create_manifest]},
    ]

    controller.addSequence("Installing OpenStack Ironic", [], [],
                           steps)


#-------------------------- step functions --------------------------

def create_manifest(config, messages):
    if (config['CONFIG_IRONIC_NOVA_USER'] == 'admin' and
            config['CONFIG_IRONIC_NOVA_PW'] == ''):
        config['CONFIG_IRONIC_NOVA_PW'] = config['CONFIG_KEYSTONE_ADMIN_PW']

    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_STORAGE_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_ironic.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate(get_mq(config, "ironic"))
    manifestdata += getManifestTemplate("ironic.pp")

    fw_details = dict()
    key = "ironic-api"
    fw_details.setdefault(key, {})
    fw_details[key]['host'] = "ALL"
    fw_details[key]['service_name'] = "ironic-api"
    fw_details[key]['chain'] = "INPUT"
    fw_details[key]['ports'] = ['6386']
    fw_details[key]['proto'] = "tcp"
    config['FIREWALL_IRONIC_API_RULES'] = fw_details

    manifestdata += createFirewallResources('FIREWALL_IRONIC_API_RULES')
    appendManifestFile(manifestfile, manifestdata, 'pre')


def create_keystone_manifest(config, messages):
    if config['CONFIG_UNSUPPORTED'] != 'y':
        config['CONFIG_IRONIC_HOST'] = config['CONFIG_CONTROLLER_HOST']

    manifestfile = "%s_keystone.pp" % config['CONFIG_CONTROLLER_HOST']
    manifestdata = getManifestTemplate("keystone_ironic.pp")
    appendManifestFile(manifestfile, manifestdata)
