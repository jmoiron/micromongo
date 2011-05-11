.. micromongo documentation master file, created by sphinx-quickstart.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

micromongo
-----------

micromongo is a tiny layer around pymongo that allows you to create simple
ORM-style classes that can perform validation, allow dot access to documents,
auto-wrap queryset results, and give you pre/post save hooks.

It's designed with microframeworks in mind, but is application and framework
agnostic.  It is meant to simplify usage of pymongo and provide tools for
common idioms, not to obscure pymongo or mongodb from your data structures.

``micromongo`` makes a few design decisions in the name of simplification that
might not work for you:

* micromongo maintains a single global connection, so you cannot have models 
  that connect to multiple mongodb servers
* there are a handfull of model names and document attribute names that will
  not work with micromongo models;  these are covered in the `Models 
  Documentation <models.html>`_
* you can only have one model per collection

.. highlight:: sh

You can install micromongo with pip::

    pip install micromongo

You are welcome to open issues or send pull requests on `micromongo's github`_::

    git clone https://github.com/jmoiron/micromongo.git

.. _`micromongo's github`: https://github.com/jmoiron/micromongo

In depth documentation
~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
    :maxdepth: 2

    tutorial
    models
    backend

