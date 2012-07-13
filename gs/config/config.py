# coding=utf-8
import os
from os.path import isfile
from App.config import getConfiguration
from App.FindHomes import CLIENT_HOME, INSTANCE_HOME
import ConfigParser
import logging
import time

log = logging.getLogger('gs.config')

class ConfigError(Exception):
    pass

class Config(object):
    schema = {}
    def __init__(self, configset=None, configpath=None):
        if not configset:
            # get the configset from our groupserver config, otherwise abandon ship.
            pass

        if not configpath:
            # again, try and figure out from our groupserver config, otherwise abort.
            pass

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
            raise ConfigError('No configuration defined for "%s" in set "%".' %
                      (configtype, configset))

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

def init():
    cfg = getConfiguration()
    parser = ConfigParser.SafeConfigParser()
    configName = os.path.join(cfg.instancehome, 'etc/database.ini')
    log.info('Reading the config file <%s>' % configName)
    if not isfile(configName):
        m = 'Could not read the configuration, as the configuration '\
            'file "%s" does not exist.' % configName
        raise ConfigError(m)
    parser.read(configName)
    for section in parser.sections():
        top = time.time()
        if section.find('database-') == 0:
            configdict = {}
            configid = None
            # check we have everything
            for option in ('id','dsn'):
                if not parser.has_option(section, option):
                    raise ConfigError(
                   "No option %s specified in database section %s"
                          % (option, section))
                if option == 'id':
                    configid = parser.get(section, 'id')
                else:
                    configdict[option] = parser.get(section, option)
            
            databaseConfig[configid] = configdict

