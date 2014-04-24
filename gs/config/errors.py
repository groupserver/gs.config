# -*- coding: utf-8 -*-


class ConfigError(Exception):
    '''A generic error with the configuration.'''


class ConfigPathError(ValueError, ConfigError):
    '''An error with the path to the config file.'''


class ConfigFileError(OSError, ConfigError):
    'An error with reading the config file'


class ConfigSetError(ConfigError):
    '''An error with the structure of the config file.'''


class ConfigNoSchemaError(KeyError, ConfigError):
    '''An error raised when there is no schema'''


class ConfigNoSectionError(ConfigError):
    '''An error raised when there is no configuration section specified.'''


class ConfigNoOptionError(ConfigError):
    '''An error raised when an option is not defined in a schema'''


class ConfigConvertError(TypeError, ConfigError):
    '''An error raissed when the value cannot be converted.'''
