# coding=utf-8
import os
from os.path import isfile
from App.config import getConfiguration
from App.FindHomes import CLIENT_HOME, INSTANCE_HOME
import ConfigParser
import core
import logging
import time

log = logging.getLogger('gs.config')

path = core.__file__
dirpath = os.path.dirname(path)

class ConfigError(Exception):
    pass

configGroups = {}
databaseConfig = {}
smtpConfig = {}

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

        #    instance_id = parser.get(section, 'instance_id')
        #    dsn = parser.get(section, 'dsn')
        #    
        #    databases[instance_id] = init_db(dsn)
        #    
        #    bottom = time.time()
        #    
        #    log.info("Initialised database for instance %s in %.2fs" % 
        #              (instance_id, (bottom-top)))
