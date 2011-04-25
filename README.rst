micromongo
-----------

micromongo is a tiny layer around pymongo that allows you to create simple
ORM-style classes that can perform validation, allow dot access to documents,
auto-wrap queryset results, and give you pre/post save hooks.

It's designed with microframeworks in mind, but is application and framework
agnostic.  It is meant to simplify usage of pymongo and provide tools for
common idioms, not to obscure pymongo or mongodb from your data structures.

