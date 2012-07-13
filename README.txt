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

 >>> config = gs.config.getConfig('test')

You can ask for a specific configuration to be returned:

>>> config.keys()
{'database', 'smtp', 'wibble'}
>>> config.get('database')
{'dsn': 'postgres://name:pass@server/database-test'}

And as a convenience, you can pass in a (very) simple schema to handle
validation and conversion:

>>> config.get_validated('test', {'server': str, 'port': int})
{'server': 'localhost', 'port': 2525}

.. _GroupServer: http://groupserver.org/
