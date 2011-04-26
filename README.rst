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

Model.find
~~~~~~~~~~

For convenience and DRY, ``Model.find`` is a classmethod that will use
micromongo's cursor to issue a find against the right collection.  This method
behaves exactly the same as `pymongo's Collection.find`_.

micromongo's slightly modified ``Cursor`` class also makes a django-inspired
``order_by`` method available to all cursors (``find`` and anything you chain
off if it returns a cursor).  You can pass one or more field names, with an
optional leading '-', to sort things by ascending or descending order.

These changes allow you to use most of the power of pymongo without having to
import it, and lets you avoid needless repetition of the location of your data.

field subclassing
~~~~~~~~~~~~~~~~~

You are encouraged to create your own Fields that do what you want.  Field 
subclasses have a hook function ``pre_validate`` which take an incoming value
and can transform it however they want.  Note that this will only work if the
fields are actually present; so to get something like an ``auto_now_add`` on a
``DateTimeField``, you will want to make it required and have its
``pre_validate`` turn ``None`` into ``datetime.datetime.now()``.


.. _`pymongo's Connection`: http://api.mongodb.org/python/current/api/pymongo/connection.html
.. _`pymongo's Collection.find`: http://api.mongodb.org/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find

