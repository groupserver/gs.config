Example
=======

A configuration class is initialised. The second parameter is optional,
depending on the degree to which we want the environment to configure things
automatically::

 >>> from gs.config import Config
 >>> config = Config('default', '/example/config/file.ini')

A schema must be provided before data is retrieved. For example,
setting the server to be a string, and a port to be an integer::

 >>> config.set_schema('smtp', {'server': str, 'port': int})

Then a specific configuration section, with all the options can
be retrieved as a dict::

 >>> config.get('smtp')
 {'port': 2525, 'server': localhost}

If file fails to fit the schema then a ConfigError is raised::

 >>> c.set_schema('wibble', {'someparam': int})
 >>> c.get('wibble')
 Traceback (most recent call last):
   File "<console>", line 1, in <module>
   File "/home/deploy/groupserver-12.05/src/gs.config/gs/config/config.py", line 70, in get
     (option, val, schema[option]))
 ConfigError: Unable to convert option "someparam" value "one" using "<type 'int'>"

