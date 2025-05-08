api
===

Indicates the ``tag`` of a request method or RequestHandler class.

A ``tag`` is an OpenAPI mechanism to group endpoints logically.

Can be applied to classes or methods. For example, if you apply it to your `RequestHandler` subclasses then your RequestHandler subclass will appear in `swagger-ui` as a group of endpoints.

If no value for ``tag`` is provided and the target is a class, the class name is used. Otherwise the decorator will raise an error.

If a request method or api is, categorically, part of more than one group this decorator may be applied multiple times to associate with all groups.
