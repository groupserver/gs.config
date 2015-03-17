Example
=======

Below is an example of a file_ with configuration sets, and
parsing_ the file.

File
----

In the following example the default configuration-set contains
two items, ``smtp`` and ``pop``. The the configuration for this
set is provided by the ``smtp-local`` and ``pop-local``
sections. The ``smtp-remote`` section is currently unused by the
configuration set.

.. code-block:: ini

  [config-default]
  smtp = local
  pop = local

  [smtp-local]
  server = localhost
  port = 2525

  [pop-local]
  server = localhost
  port = 110

  [smtp-remote]
  server = smtp.example.com
  port = 25

Parsing
-------

A configuration class is initialised. The second parameter is
optional, depending on the degree to which we want the
environment to configure things automatically.

.. code-block:: pycon

    >>> from gs.config import Config
    >>> config = Config('default', '/example/file.ini')

A schema must be provided before data is retrieved. For example,
setting the server to be a string, and a port to be an integer.

.. code-block:: pycon

    >>> config.set_schema('smtp', {'server': str, 'port': int})

Then a specific configuration section, with all the options can
be retrieved as a dict.

.. code-block:: pycon

    >>> config.get('smtp')
    {'port': 2525, 'server': localhost}

If file fails to fit the schema then a ConfigError is raised:

.. code-block:: pycon

    >>> config.set_schema('smtp', {'someparam': int})
    >>> config.get('smtp')

.. code-block:: pytb

    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "config.py", line 201, in get
        raise ConfigNoOptionError(msg)
    ConfigNoOptionError: No option "server" defined in schema for "smtp".

However, it is possible to parse the configuration in a lax way,
by passing ``strict=False``. This allows for hard-coded defaults:

.. code-block:: pycon

    >>> config.get('smtp', strict=False)
    {}
