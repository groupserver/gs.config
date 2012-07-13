Introduction
============

gs.config allows for generic configuration set based configuration. It is
possibly easier to demonstrate than to explain.

Configuration File
==================

The configuration file is structured like this::

  # One or more configuration groups
  [config-test]
  database = test
  smtp = test
  wibble = foo

  [config-staging]
  database = live
  smtp = test
  wibble = blarg

  # An actual configuration section for each configuration set
  [database-test]
  dsn = postgres://name:pass@server/database-test

  [database-live]
  dsn = postgres://name:pass@server/database-live

  [smtp-test]
  server = localhost
  port = 2525

  [wibble-foo]
  someparam = one

  [wibble-blarg]
  someparam = two

When the configuration is instantiated, an ID is passed. This ID identifies
the configuration set that is currently being accessed. If an ID is not
passed, an attempt is made to get the ID from the environment
automatically. At the moment this is specific to the GroupServer_
environment, though care is taken to ensure that it will fall back
gracefully to being passed an ID.

Interface
=========

Example
=======

A configuration class is initialised. The two parameters are optional,
depending on the degree to which we want the environment to configure things
automatically::

 >>> from gs.config import Config
 >>> config = Config('test', 'config.ini')

A schema must be provided before data is retrieved::

 >>> config.set_schema('smtp', {'server': str, 'port': int})

Then a specific configuration type can be retrieved::

 >>> config.get('smtp')
 {'port': 2525, 'server': localhost}

If a schema doesn't fit the actual data, a ConfigError is raised::

 >>> c.set_schema('wibble', {'someparam': int})
 >>> c.get('wibble')
 Traceback (most recent call last):
   File "<console>", line 1, in <module>
   File "/home/deploy/groupserver-12.05/src/gs.config/gs/config/config.py", line 70, in get
     (option, val, schema[option]))
 ConfigError: Unable to convert option "someparam" value "one" using "<type 'int'>"

.. _GroupServer: http://groupserver.org/
