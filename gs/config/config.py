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
import os
from os.path import isfile
import ConfigParser
import logging

try:
    from App.config import getConfiguration
    from zope.globalrequest import getRequest
    USINGZOPE = True
except ImportError:
    USINGZOPE = False
    getConfiguration = getRequest = None  # lint:ok

log = logging.getLogger('gs.config')


def bool_(val):
    if val.lower() in ('true', 'yes', 'on'):
        val = True
    elif val.lower() in ('false', 'no', 'off'):
        val = False
    else:
        raise ValueError("Not a bool")
    return val


class ConfigError(Exception):
    pass


def getInstanceId():
    instance_id = ''
    if USINGZOPE:
        request = getRequest()
        if request:
            instance_id = request.get('HTTP_INSTANCEID', '')
    retval = ((instance_id and instance_id) or 'default')
    return retval


class Config(object):
    schema = {}

    def __init__(self, configset, configpath=None):
        if USINGZOPE and not configpath:
            # again, try and figure out from our groupserver config,
            # otherwise abort.
            cfg = getConfiguration()
            configpath = os.path.join(cfg.instancehome, 'etc/gsconfig.ini')
        elif not configpath:
            raise ConfigError("No configpath set, unable to read configfile")

        if not isfile(configpath):
            raise ConfigError('Could not read the configuration, as the '
                'configuration file "%s" does not exist.' % configpath)

        log.info("Reading the config file <%s>" % configpath)
        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(configpath)

        if not self.parser.has_section('config-' + configset):
            m = 'No configuration set "%s" defined in file.' % configset
            raise ConfigError(m)
        self.configset = configset

    def set_schema(self, configtype, schema):
        assert isinstance(schema, dict),\
            "Schema must be a dictionary of converters"
        self.schema[configtype] = schema

    def get_schema(self, configtype):
        if not (configtype in self.schema):
            m = 'No schema defined for configuration type "%s".' % configtype
            raise ConfigError(m)

        return self.schema[configtype]

    def keys(self):
        return self.parser.options('config-' + self.configset)

    def get(self, configtype):
        if configtype not in self.keys():
            m = 'No configuration defined for "%s" in set "%s".' %\
                  (configtype, self.configset)
            raise ConfigError(m)

        secval = self.parser.get('config-' + self.configset, configtype)
        if not self.parser.has_section(configtype + '-' + secval):
            m = 'No configuration for type "%s" with value "%s".' %\
                   (configtype, secval)
            raise ConfigError(m)

        schema = self.get_schema(configtype)

        retval = {}
        for option in self.parser.options(configtype + '-' + secval):
            if option not in schema:
                m = 'No option "%s" defined in schema for "%s"' %\
                          (option, configtype)
                raise ConfigError(m)
            val = self.parser.get(configtype + '-' + secval, option)
            try:
                val = schema[option](val)
            except:
                m = 'Unable to convert option "%s" value "%s" using "%s"' %\
                      (option, val, schema[option])
                raise ConfigError(m)
            retval[option] = val

        return retval
