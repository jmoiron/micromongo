.. describe micromongo's backend implementation in case people want to
   and also cover some advance pieces of behavior/functionality not
   present in the other documents

Backend
-------

The micromongo backend is primarily concerned with making sure that we the
documents coming out of the database have the same class as the ``Model``
classes we've defined for those particular collections.

.. automodule:: micromongo.backend

The class router works via an accounting metaclass that every Model shares.
This class maintains a map of collections to model classes to do the proper
routing.

.. autoclass:: micromongo.models.AccountingMeta

Subclasses
~~~~~~~~~~

The following subclasses are made by the backend:

.. autoclass:: micromongo.backend.Connection

The ``Connection`` object is where the class router is set.  If you would prefer,
you can create one directly and set your own class router via the 
``class_router`` keyword argument.  This is the actual type returned by
``micromongo.connect()``.

.. autoclass:: micromongo.backend.Database

The ``Database`` object is unmodified from the pymongo class.

.. autoclass:: micromongo.backend.Collection

The ``Collection`` object is unmodified from the pymongo class.

Micromongo's Cursor
~~~~~~~~~~~~~~~~~~~

.. autoclass:: micromongo.backend.Cursor

The ``Cursor`` class is what is returned when you perform a ``find``, and
cloned (or modified) cursors are also returned on subsequent operations like
sorts, limits, slices, etc.  Micromongo's Cursor does behave slightly 
differently from the default in a few key ways.

The first is that these cursors behave more like lazy ORM/ODM querysets than
database cursors.  Once iterated over, these cursors cache the returned results
and can be iterated over again.  If you are counting on the default cursor
behavior, you should use ``micromongo.clean_connection()`` to get a connection
that will not exhibit this behavior.  This might be required if, for example,
your application is using tailable cursors.

.. automethod:: micromongo.backend.Cursor.next

The cursors are also where the ``as_class`` setting for our class router is
applied.  If you want to avoid this behavior, a clean connection will be
required.

Finally, the cursor defines a function, ``order_by``, which is a convenient
way to do simple one or two field sorts, inspired by the Django ORM:

.. automethod:: micromongo.backend.Cursor.order_by

For many simple apps that require only object persistence and simple sorting, 
it's generally possible to avoid importing pymongo in code using micromongo,
as the only thing you generally need it for if you have a collection object is
``pymongo.{ASCENDING,DESCENDING}``.

Running Tests
~~~~~~~~~~~~~

To run the tests, you'll have to clone the repository to get the test suite,
and then either use ``./setup.py test`` or a third party test runner such as
``nose``.

In addition to that, you can set the testing environment mongodb settings with
the following keys:

* ``MICROMONGO_URI``: a `mongo connection URI`_
* ``MICROMONGO_HOST``: a hostname or IP address
* ``MICROMONGO_PORT``: a port number

If the URI is present, it is used rather than the HOST or PORT parameters.

.. _`mongo connection URI`: http://www.mongodb.org/display/DOCS/Connections

