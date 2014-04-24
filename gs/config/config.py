# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from os.path import isfile, join as path_join
import sys
if (sys.version_info >= (3, )):
    from configparser import SafeConfigParser
else:
    from ConfigParser import SafeConfigParser  # lint:ok
from logging import getLogger
log = getLogger('gs.config')
from .errors import (ConfigPathError, ConfigFileError, ConfigSetError,
    ConfigNoSchemaError, ConfigNoOptionError, ConfigNoSectionError,
    ConfigConvertError)
try:
    from App.config import getConfiguration
    from zope.globalrequest import getRequest
    USINGZOPE = True
except ImportError:
    USINGZOPE = False
    getConfiguration = getRequest = None  # lint:ok


def bool_(val):
    '''Turn the plain-text ways of writing Boolean values into a Boolean
    value.'''
    if val.lower() in ('true', 'yes', 'on'):
        val = True
    elif val.lower() in ('false', 'no', 'off'):
        val = False
    else:
        raise ValueError("Not a bool")
    return val


def getInstanceId():
    instance_id = ''
    if USINGZOPE:
        request = getRequest()
        if request:
            instance_id = request.get('HTTP_INSTANCEID', '')
    retval = instance_id if instance_id else 'default'
    return retval


class Config(object):
    schema = {}

    def __init__(self, configset, configpath=None):
        if USINGZOPE and not configpath:
            # again, try and figure out from our groupserver config,
            # otherwise abort.
            cfg = getConfiguration()
            configpath = path_join(cfg.instancehome, 'etc/gsconfig.ini')
        elif configpath is None:
            msg = "No configpath set, unable to read configfile"
            raise ConfigPathError(msg)

        if not isfile(configpath):
            m = 'Could not read the configuration, as the configuration file '\
                '"{0}" does not exist.'
            msg = m.format(configpath)
            raise ConfigFileError(msg)

        log.info("Reading the config file <%s>" % configpath)
        self.parser = SafeConfigParser()
        self.parser.read(configpath)

        if not self.parser.has_section('config-' + configset):
            m = 'No configuration set "{0}" defined in file "{1}".'
            msg = m.format(configset, configpath)
            raise ConfigSetError(msg)
        self.configset = configset

    def set_schema(self, configtype, schema):
        if not isinstance(schema, dict):
            m = "Schema must be a dictionary of converters, not a {0}"
            msg = m.format(type(schema))
            raise ValueError(msg)
        self.schema[configtype] = schema

    def get_schema(self, configtype):
        if configtype not in self.schema:
            m = 'No schema defined for configuration type "{0}".'
            msg = m.format(configtype)
            raise ConfigNoSchemaError(msg)
        return self.schema[configtype]

    def keys(self):
        return self.parser.options('config-' + self.configset)

    def get(self, configtype):
        if configtype not in self.keys():
            m = 'No configuration defined for "{0}" in set "{1}".'
            msg = m.format(configtype, self.configset)
            raise ConfigNoSectionError(msg)

        secval = self.parser.get('config-' + self.configset, configtype)
        if not self.parser.has_section(configtype + '-' + secval):
            m = 'No configuration section for type "{0}" with value "{1}".'
            msg = m.format(configtype, secval)
            raise ConfigNoSectionError(msg)

        schema = self.get_schema(configtype)

        retval = {}
        for option in self.parser.options(configtype + '-' + secval):
            if option not in schema:
                m = 'No option "{0}" defined in schema for "{1}".'
                msg = m.format(option, configtype)
                raise ConfigNoOptionError(m)
            val = self.parser.get(configtype + '-' + secval, option)
            try:
                val = schema[option](val)
            except:
                m = 'Unable to convert option "{0}" value "{1}" using "{2}'
                msg = m.format(option, val, schema[option])
                raise ConfigConvertError(msg)
            retval[option] = val

        return retval
