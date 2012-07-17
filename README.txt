Introduction
============

This product provides the basic configuration system for GroupServer_.
Each GroupServer instance is made up of a component, and each 
component is made up of configuration options:

* Instance
  
  + Component
  
     - Configuration
     
Sadly the ConfigParser_ system does not allow for this hierarchy. To 
overcome this the *name* *space* is used to provide the relationship 
between an instance and the component.

The instance is marked with the name ``[config-${name}]``, where
``${name}`` is the name of the instance. For example ``[config-main]``
for the instance ``main``.

Within each instance the components are listed. There are four components
that are recognised:

#. ``database`` (see ``gs.database``)
#. ``smtp`` (see ``gs.email``)
#. ``cache`` (see ``gs.cache``)
#. ``tokenauth`` (see ``gs.auth.token``)

For each component the name of the section is given. (The configuration 
for a component can be shared by multiple GroupServer instances.)::

  [config-production]
  database = production
  smtp = external
  cache = production
  tokenauth = production
  
Each component is a configuration section, with a name of the form
``[${component}-${name}]``. For example ``[database-production]`` for the 
database section named *production*.

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
.. _ConfigParser: http://docs.python.org/library/configparser.html
