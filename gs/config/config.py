# coding=utf-8
import os
from os.path import isfile
import ConfigParser
import logging
import time

try:
    from App.config import getConfiguration
    from zope.globalrequest import getRequest
    USINGZOPE = True
except ImportError:
    USINGZOPE = False
    getConfiguration = getRequest = None

log = logging.getLogger('gs.config')

def bool_(val):
    if val.lower() in ('true', 'yes', 'on'):
        val = True
    elif val.lower() in ('false', 'no', 'off'):
        val = False
    else:
        raise ValueError, "Not a bool"
    return val

class ConfigError(Exception):
    pass

def getInstanceId():
    instance_id = 'default'
    if USINGZOPE:
        request = getRequest()
        instance_id = 'default'
        if request:
            instance_id = request.get('HTTP_INSTANCEID', 'default')

    return instance_id

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

        if not self.parser.has_section('config-'+configset):
            raise ConfigError('No configuration set "%s" defined in file.' % configset)
        self.configset = configset

    def set_schema(self, configtype, schema):
        assert isinstance(schema, dict), "Schema must be a dictionary of converters"
        self.schema[configtype] = schema

    def get_schema(self, configtype):
        if not self.schema.has_key(configtype):
            raise ConfigError('No schema defined for configuration type "%s".' % configtype)

        return self.schema[configtype]
    
    def keys(self):
        return self.parser.options('config-'+self.configset)

    def get(self, configtype):
        if configtype not in self.keys():
            raise ConfigError('No configuration defined for "%s" in set "%s".' %
                      (configtype, self.configset))

        secval = self.parser.get('config-'+self.configset, configtype)
        if not self.parser.has_section(configtype+'-'+secval):
            raise ConfigError('No configuration for type "%s" with value "%s".' % 
                               (configtype, secval))
       
        schema = self.get_schema(configtype)

        retval = {}
        for option in self.parser.options(configtype+'-'+secval):
            if option not in schema:
                raise ConfigError('No option "%s" defined in schema for "%s"' %
                          (option, configtype))
            val = self.parser.get(configtype+'-'+secval, option)
            try:
                val = schema[option](val)
            except:
                raise ConfigError('Unable to convert option "%s" value "%s" using "%s"' % 
                                  (option, val, schema[option]))
            retval[option] = val

        return retval
