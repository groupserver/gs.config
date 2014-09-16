=============
``gs.config``
=============
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Configuration files with "sets"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Authors: `Richard Waid`_; `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-04-24
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.

Introduction
============

Sometimes configuration is complex, such as when multiple sets of
configuration is needed because multiple instances of a system
(such as GroupServer [#gs]_) are running on the same setup. In
this case each instance is made up of a set of components, and
each component is made up of configuration options:

* Instance

  + Component
  
    - Configuration options
    - More configuration options

  + Component 2

    - Different configuration options

* Another instance

Sadly the ConfigParser_ system does not allow for this hierarchy,
but ``gs.config`` does, by using the *name* *space* to provide
the relationship between an instance and the component. In
particular, this product supplies a `Config class`_ to read a
file_ of a particular structure.

``Config`` Class
================

The ``gs.config.Config`` class that represents the system
configuration. See the Sphinx documentation in this module for
more information.

File
====

The instance is marked with the name ``[config-${name}]``, where
``${name}`` is the name of the instance. For example ``[config-production]``
for the instance ``production``.

For each component the set of sections is then supplied::

  [config-production]
  database = production
  smtp = external
  cache = production
  tokenauth = production
  
The configuration for a component can be shared by multiple
instances::

  [config-staging]
  database = production
  smtp = dead
  cache = none
  tokenauth = production

Each component is a configuration section, with a name of the form
``[${component}-${name}]``. For example ``[smtp-external]`` for the 
smtp section named *external*.

Example
-------

In the example below three instances are configured: one for a
test-server, one for a staging server, and one for a production
server. Each instance has two components: a database, and an SMTP
server::

  [config-test]
  database = test
  smtp = test

  [config-staging]
  database = live
  smtp = test

  [config-production]
  database = live
  smtp = live

  # An actual configuration section for each configuration set
  [database-test]
  dsn = postgres://name:pass@server/database-test

  [database-live]
  dsn = postgres://name:pass@server/database-live

  [smtp-test]
  server = localhost
  port = 2525

  [smtp-live]
  server = external
  port = 25

When the configuration is instantiated, an ID is passed. This ID identifies
the configuration set that is currently being accessed. If an ID is not
passed, an attempt is made to get the ID from the environment
automatically. At the moment this is specific to the GroupServer_
environment, though care is taken to ensure that it will fall back
gracefully to being passed an ID.

Resources
=========

- Documentation: http://gsconfig.readthedocs.org/
- Code repository: https://source.iopen.net/groupserver/gs.config
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. [#gs] While originally written for GroupServer_, there is no
         code in this product that is specific to
         GroupServer. However, this product is used to configure
         the database_, SMTP_, cache_, and `token
         authentication`_ for GroupServer.
.. _database: https://source.iopen.net/groupserver/gs.database
.. _SMTP: https://source.iopen.net/groupserver/gs.email
.. _cache: https://source.iopen.net/groupserver/gs.cache
.. _token authentication: https://source.iopen.net/groupserver/gs.auth.token

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _ConfigParser: http://docs.python.org/library/configparser.html
..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/
.. _Richard Waid: http://groupserver.org/p/richard
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
