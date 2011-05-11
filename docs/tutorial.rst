.. micromongo tutorial, should cover the fundamentals but leave out in depth
   information on models and hooks that are covered elsewhere

.. highlight:: python

Tutorial
--------

This tutorial will get you started with micromongo.

Connecting
~~~~~~~~~~

To start off with micromongo, we need to connect to a database::

    >>> from micromongo import connect, Model
    >>> c = connect()

``connect`` takes the same arguments as `pymongo's Connection`_ object, and
behaves almost identically, except that it attempts to automatically return
query results wrapped in the appropriate Model classes.  The connection object
that you create via this call will be cached and used by the various ORM-style
facilities, like ``Model.save()``, ``Model.find``, etc.  If you want a clean,
standard ``Connection`` object, you can get one easily::

    >>> from micromongo import clean_connection
    >>> clean = clean_connection()

``clean_connection`` will always return a ``Connection`` class with the same 
settings as the current micromongo connection.  If you call ``connect`` with
different arguments, these areguments are used for the connection returned by
subsequent calls to ``clean_connection``.

.. autofunction:: micromongo.connect

.. autofunction:: micromongo.clean_connection

With these connection objects, you can create databases or do whatever you
would with normal ``pymongo`` objects::

    >>> db = c.test_db
    >>> collection = db.test_collection
    >>> collection.save({"docid": 1, "fail": False})
    >>> collection.find_one()
    {u'_id': ObjectId('...'), u'fail': False, u'docid': 1}


Using Models
~~~~~~~~~~~~

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

Besides packing and unpacking results from the database, models can also define
a ``spec`` document which can define defaults and perform validation before
saving the model.  Take a trivial blog post model::

    >>> from micromongo.spec import *
    >>> class Post(Model):
            collection = 'test_db.blog_posts'
            spec = dict(
                author=Field(required=True, default='jmoiron', type=basestring),
                title=Field(required=False, default='', type=basestring),
                published=Field(required=True, default=False, type=[True, False]),
                body=Field(type=unicode),
                timestamp=Field(),
            )

    >>> p = Post.new()
    >>> p
    <Post: {'title': u'', 'author': u'jmoiron', 'published': False}>

A few things are going on here.  Fields that have a default are initialized to
that default whether they are required or not.  If a required field does not
have a default, it's initialized to ``None``.

Fields can take a ``type`` argument, which can either be a callable that takes
a value and returns True or False, one or more base types, or one or more
values.  If one or more types are provided, ``isinstance`` is used to test that
values are the right type.  If one or more values are provided, the Field acts
as an enum type, checking that values are in its set of values.  If no type is
given, validation always passes on a field *unless* it is required and absent.

If a field in p is given an invalid type, then a ``ValueError`` is raised::

    >>> p.title = 10
    >>> p.save()
    Traceback (most recent call last):
      ...
    ValueError: Keys did not match spec: ['title']
    >>> del p.author
    >>> p.save()
    Traceback (most recent call last):
      ...
    ValueError: Missing fields: ['author'], Invalid fields: ['title']
    >>> p.title = 'My first blogpost'
    >>> p.author = 'jmoiron'
    >>> p.published = True
    >>> p.body = u"This is my first blog post..  I'm so excited!"
    >>> p.save()

Learn more about defining models, pre/post save hooks, model validation, and
some of the limitations of micromongo models in the `Models Documentation
<models.html>`_.

.. _`pymongo's Connection`: http://api.mongodb.org/python/current/api/pymongo/connection.html
.. _`pymongo's Collection.find`: http://api.mongodb.org/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find
