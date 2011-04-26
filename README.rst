micromongo
==========

micromongo is a tiny layer around pymongo that allows you to create simple
ORM-style classes that can perform validation, allow dot access to documents,
auto-wrap queryset results, and give you pre/post save hooks.

It's designed with microframeworks in mind, but is application and framework
agnostic.  It is meant to simplify usage of pymongo and provide tools for
common idioms, not to obscure pymongo or mongodb from your data structures.

You are welcome to open issues or send pull requests on `micromongo's github`_

.. _`micromongo's github`: https://github.com/jmoiron/micromongo

``micromongo`` makes a few design decisions in the name of simplification that
might not work for you:

* micromongo maintains a single global connection, so you cannot have models 
  that connect to multiple mongodb servers
* there are a handfull of model names and document attribute names that will
  not work with micromongo models;  these will be covered in the `full docs`_
* you can only have one model per collection

.. _`full docs`: http://packages.python.org/micromongo/

getting started
---------------

To start off with micromongo, just import it::

    >>> from micromongo import connect, Model
    >>> c = connect()

``connect`` takes the same arguments as `pymongo's Connection`_ object, and
behaves almost identically, except that it attempts to automatically return
query results wrapped in the appropriate Model classes.  The connection object
that you create via this call will be cached and used by the various ORM-style
facilities, like ``Model.save()``, ``Model.proxy``, etc.  If you want a clean,
standard ``Connection`` object, you can get one easily::

    >>> from micromongo import clean_connection
    >>> clean = clean_connection()

Note that clean_connection does not take arguments and will always return a
clean ``Connection`` class with the same settings as the current micromongo 
connection.

With these connection objects, you can create databases or do whatever you
would with normal ``pymongo`` objects::

    >>> db = c.test_db
    >>> collection = db.test_collection
    >>> collection.save({"docid": 1, "fail": False})
    >>> collection.find_one()
    {u'_id': ObjectId('...'), u'fail': False, u'docid': 1}

You can also declare your own Model for a particular collection in
declarative style::

    >>> class TestModel(Model):
            collection = 'test_db.test_collection'

    >>> collection.find_one()
    <TestModel: {u'_id': ObjectId('...'), u'fail': False, u'docid': 1}>

These classes have a number of additional features over a dictionary that can
make them much more convenient to use.  The document keys are all accessible
as attributes::

    >>> t = collection.find_one()
    >>> t.fail
    False
    >>> t.docid
    1

The documents are also easily persisted to the database::

    >>> t.docid = 17
    >>> t.save()
    >>> clean.test_db.test_collection.find_one()
    {u'_id': ObjectId('...'), u'fail': False, u'docid': 17}

defining models
---------------

Above, the ``collection`` attribute was assigned to our ``Foo`` model.  This
was a shortcut, though;  if ``database`` and ``collection`` are assigned
separately, the Model can figure out the full collection name.  If the
collection and database are not present, micromongo attempts to figure it out
based on the class and module name of your Model.  For instance, ``blog.Post``
will become ``blog.post``, or ``stream.StreamEntry`` will become
``stream.stream_entry``.  Explicit is better than implicit, and it's encouraged
that you set the collection manually.

Besides packing and unpacking results from the database, models can also define
a ``spec`` document which can define defaults and perform validation before
saving the model.  Take a trivial blog post model::

    >>> from micromongo.spec import *
    >>> class Post(Model):
            collection = 'test_db.blog_posts'
            spec = dict(
                author=Field(default='jmoiron', required=True, type=unicode),
                title=Field(required=True, default='', type=unicode),
                published=Field(required=True, default=False, type=[True, False]),
                body=Field(type=unicode),
                timestamp=Field(),
            )

    >>> p = Post.new()
    >>> p


.. _`pymongo's Connection`: http://api.mongodb.org/python/current/api/pymongo/connection.html

