Introduction
============

`GroupServer`_ stores *most* of its data using the `PostgreSQL`_ relational
database [#otherData]_. The `SQLAlchemy`_ system is used to provide the
connection between GroupServer and PostgreSQL [#transaction]_. The
``gs.database`` product provides some utilities to establish the
connection, and use the connection more easily. Most code will `perform a
query`_ in the same way, and not have to consider which `database
instance`_ is being used.

Perform a Query
===============

To perform a query carry out the following steps.

#. Call `getTable`_ to get the relational database table to query.
#. Create the statement with the table, using SQLAlchemy.
#. Call `getSession`_ to get the *session* that connects to the database.
#. Execute the statement with the session.
#. Finally, if the database is being **changed** — by an ``update``,
   ``insert``, or ``delete`` — then ``zope.sqlalchemy.mark_changed`` should
   be called, passing the session as the argument. This ensures that the
   session is committed to the database.

In `example patterns`_ below we show some common techniques for performing
these queries.

``getTable``
------------

The ``gs.database.getTable`` function is used to get a table. Queries
are performed on the table that is returned.

:Synopsis:
   ``getTable(tableName)``

:Arguments:

   ``tableName``
     The name of the table-instance to retrieve from the database.

:Returns: 
   The `SQLAlchemy`_ table-instance for ``tableName``, for the current
   `database instance`_.

``getSession``
--------------

The ``gs.database.getSession`` is used to get the `SQLAlchemy
session`_ that will manage the connection with the current `database
instance`_ and execute the query.

:Synopsis:
   ``getSession()``

:Arguments:
   None.

:Returns:
   The SQLAlchemy session instance for the current thread and the current
   `database instance`_

Example Patterns
----------------

There are four basic patterns. The first is creating `a query class`_ to
hold some related queries. Second is the very common `selecting`_
pattern. `Inserting`_ is comparatively rare. However, it is not as rare as
`updating`_, which is normally only used to carry out a *logical delete*.

A Query Class
~~~~~~~~~~~~~

Normally a query-class is created to combine some related queries. The
`getTable`_ call is made to instantiate the table as a property of the
instance.::

    class QueryClass(object):
        def __init__(self):
            self.table = getTable('tableName')

Selecting
~~~~~~~~~

Most selects follow the same pattern: 

* Create a select statement (``self.table.select``), 
* Specify the columns to select, 
* Specify the order,
* Append a where-clause, 
* Append another where-clause to ignore the logically-deleted items (see
  `updating`_ below) and 
* Then the statement is executed. 

Usually each result is marshaled into a dictionary, and all the results
placed in a list::

       def get_some_column(self, methodArgument):
           assert methodArgument, 'No method argument specified'
           cols = [self.table.c.columnName]
           s = self.table.select(cols).order_by(self.table.c.someOtherColumn)
           s.append_whereclause(self.table.c.columnName == methodArgument)
           s.append_whereclause(self.table.c.deleted == None)

           session = getSession()
           r = session.execute(s)
           retval = []
           if r:
               retval = [{'columnName': x['columnName']} for x in r]
           assert type(retval) == list
           return retval

Inserting
~~~~~~~~~

When inserting an insert statement is first created (normally by
``self.table.insert``). The data to insert is then passed as the dictionary
``params`` when executing the statement. Finally,
``zope.sqlalchemy.mark_changed`` is called to ensure the data is flushed to
the database.::

       def add_some_thing(self, thing):
           assert thing, 'No thing specified'
           i = self.table.insert()
           d = {'columnName': thing}
       
           session = getSession()
           session.execute(i, params=d)
           mark_changed(session)

Updating
~~~~~~~~

Updating is rare in GroupServer. About the only time it is ever done is to
logically delete an entry by setting the ``deleted`` column to the current
time [#deleted]_::

    def del_some_thing(self, methodArgument):
        u = self.table.update(self.table.c.columnName == methodArgument)
        d = {'deleted': datetime.utcnow()}

        session = getSession()
        session.execute(u, params=d}
        mark_changed(session)

Database Instance
=================

:Note:
  For GroupServer installations with only one site there can only be
  one database instance, so this section can be ignored.

GroupServer is highly scalable:

* One `Zope`_ instance can manage multiple GroupServer instances, 
* One GroupServer instance can manage multiple sites, and
* One site can handle multiple groups.

The PostgreSQL database is independent of this. A single *database
instance* can be shared by multiple sites. The main advantage of this is
that the **profile** information is shared [#profile]_. However, the
databases do not need to be shared.

The front-end HTTP proxy is used to set the correct database instance,
in much the same way that the proxy is used to select the correct skin
[#skin]_. The proxy should set the ``HTTP_INSTANCEID`` environment
variable in the HTTP request to the ID of the database to connect
to. The ``gs.database.core.getInstanceId`` utility, which is called by
both `getTable`_ and `getSession`_, will then examine this environment
variable to determine the correct database instance for the current
**request**.

.. _GroupServer: http://groupserver.org/
.. _PostgreSQL: http://www.postgresql.org/
.. [#otherData] Neither files, nor image caches are stored in the
                relational database. These are the the two major exceptions
                to the "data is in the database" rule.
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. [#transaction] `The zope.sqlalchemy product
                  <http://pypi.python.org/pypi/zope.sqlalchemy>`_ also
                  provides some integration between Zope transactions and
                  the SQLAlchemy transactions.
.. _SQLAlchemy session: http://docs.sqlalchemy.org/en/rel_0_7/orm/session.html
.. _Zope: http://zope.org/

.. [#deleted] Our convention is to have a ``deleted`` column, which is a
              timestamp-with-timezone. When set to ``NULL`` the entry is
              not deleted. When set the entry is deleted, with the
              timestamp showing when it was deleted.
.. [#profile] By sharing profile information between sites people can use
              the same profile to log in to multiple sites, and do not have
              to verify their email address for each site.
.. [#skin] Skins are not just colour-schemes, but entire collections of
           code. As crazy as it sounds, `selecting a skin based on URL
           <http://plone.org/documentation/kb/select-skin-by-url>`_ can
           change vast amounts of behaviour, and is normal with Zope.
