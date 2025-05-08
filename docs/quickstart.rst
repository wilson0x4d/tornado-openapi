Quick Start
============
.. _quickstart:

.. contents::

Installation
------------

You can install **tornado_openapi** from `PyPI <https://pypi.org/project/tornado_openapi/>`_ through usual means, such as ``pip``:

.. code:: bash

   pip install tornado-openapi

Usage
-----

The simplest approach is to use :py:class:`~tornado_openapi.OpenApiConfigurator` to construct a configuration object, and also update a ``tornado.web.application`` instance with necessary settings. A simple example might look like:

.. code:: python

    import tornado
    import tornado_openapi as openapi
    from .api.FakeApi import FakeApi

    # you create a tornado app
    app = tornado.web.Application()
    # you add some handlers for your app
    app.add_handlers('.*', [
        (r'/api/v2/fakes', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)', FakeApi),
        (r'/api/v2/fakes/(?P<name>[\dA-Za-z]+)', FakeApi),
        (r'/api/v2/fakes/(?P<id>\d+)?name=(?P<name>[^/][\dA-Za-z]+)', FakeApi)
    ])
    # you configure openapi
    openapi.OpenApiConfigurator(self.__tornado)\
        .pattern(r'/api/v2/(swagger.*)')\
        .info(openapi.objects.Info(
            title='My API',
            summary='APIs exposed by My Application',
            description='This is an optional long description of My Application APIs.',
            termsOfService='https://my-application/terms-of-service0',
            contact=openapi.objects.Contact(
                name='My Application on Github',
                url='https://github.com/whoami/my-application'
            ),
            license=openapi.objects.License(
                name='MIT License',
                identifier='MIT'
            ),
            version='v2'
        ))\
        .staticFilesPath('./swagger-ui')\
        .commit()

In the above example, ``FakeApi`` is a subclass of ``tornado.web.RequestHandler``. The path matches you configure for ``FakeApi`` are requried for OAS construction. There are more configuration options than are shown here, and there are decorators you can apply to your request handler classes and methods to augment OAS generation.

