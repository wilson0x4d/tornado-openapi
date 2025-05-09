
[![tornado-openapi on PyPI](https://img.shields.io/pypi/v/tornado-openapi.svg)](https://pypi.org/project/tornado-openapi/) [![tornado-openapi on readthedocs](https://readthedocs.org/projects/tornado-openapi/badge/?version=latest)](https://tornado-openapi.readthedocs.io)


`tornado-openapi` is an OAS-generation library for [Tornado](https://www.tornadoweb.org).

This README is only a high-level introduction to **tornado-openapi**. For more detailed documentation, please view the official docs at [https://tornado-openapi.readthedocs.io](https://tornado-openapi.readthedocs.io).

## Installation

You can install `tornado-openapi` from [PyPI](https://pypi.org/project/tornado-openapi) through usual means, such as `pip`:

```bash
pip install tornado-openapi
```

## Quick Start

The simplest approach is to use `OpenApiConfigurator` to construct a configuration object, and also update a `tornado.web.application` instance with necessary settings. A simple example might look like:

```python

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
    openapi.OpenApiConfigurator(app)\
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
```

In the above example, `FakeApi` is a subclass of `tornado.web.RequestHandler`. The path matches you configure for `FakeApi` are required for OAS construction. There are more configuration options than are shown here, and there are decorators you can apply to your request handler classes and methods to augment OAS generation.

## Wait, where is `swagger-ui` ?!

Alas, `swagger-ui` is NOT included as part of the `tornado-openapi` package. The reasons, in order of importance:

* We do not want to thrust a specific version of `swagger-ui` upon anyone. You may already have a version rolled into your front-end project, for example. You may want a version that is newer than what was current at the time the library was last published.
* We do not wish to encounter licensing issues, as `swagger-ui` currently falls under a different license than the licenses we typically publish under.
* We want to keep our packages small. Storage costs money, networks get congested, and small packages are great for keeping CI/CD times low.
* Indeed, we could rely on a CDN, but some enterprise security audits will identify a third-party CDN as a potential threat -- and again, we don't want to thrust upon anyone a specific version of `swagger-ui`.

Worry not, by default `tornado-openapi` will serve `swagger-ui` out of the relative path `./swagger-ui/` if it is present. It will assume the contents are a "swagger-ui-dist" bundle, and it will assume the default document is "index.html". You can, of course, customize this by passing the relevant path information into `OpenApiHandler`.

Whether or not `swagger-ui` is installed the `OpenApiHandler` will still generate a schema whenever `swagger.json` is requested. This ensures that integrations (too many to list here, from "cloud gateways" to "dev/test tools") can still be pointed at your server to acquire the necessary schema details of your APIs.

If you are a developer, build engineer, or operator and you wish to slip `swagger-ui` into the build artifacts of your product you can acquire "swagger-ui-dist" which is a self-contained `swagger-ui` distribution. The simplest approach would be to pull [the git repo](https://github.com/swagger-api/swagger-ui/) using `git`, then move/copy the `dist` directory or its contents into the `./swagger-ui` directory of your build output. This avoids a dependency on `npm` tooling, ensures you can have a fresh version of `swagger-ui`. Example:

```bash

# NOTE: remove `--branch v5.21.0` to pull latest from `master`, or, change the version to any valid tag to pull that version.
rm -rf ./swagger-ui && \
rm -rf /tmp/swagger-ui-repo && \
git clone --depth 1 --branch v5.21.0 https://github.com/swagger-api/swagger-ui.git /tmp/swagger-ui-repo && \
cp -r /tmp/swagger-ui-repo/dist ./swagger-ui && \
cp -r /tmp/swagger-ui-repo/LICENSE ./swagger-ui/LICENSE && \
cp -r /tmp/swagger-ui-repo/NOTICE ./swagger-ui/NOTICE && \
rm -rf /tmp/swagger-ui-repo
# if you want to slim down the dist to only what you need:
rm -f ./swagger-ui/*-bundle-*
rm -f ./swagger-ui/*-es-*
rm -f ./swagger-ui/*.map

```

The relative pathing and decision to use `/tmp` are highly dependent on your build environment and security practices, I leave the obvious decisions up to you and your peers.

If you have an existing front-end with `swagger-ui` installed as a package (via `npm`) simply configure the relevant `swagger.json` url you've defined in tornado and everything should work as intended. I defer to [the official documentation](https://swagger.io/tools/swagger-ui/) for configuring and using `swagger-ui`.

Lastly, you can customize the static files path of `swagger-ui` and the url of `swagger.json` by passing in additional intializer params:

```python
(r'/(swagger.*)', openapi.OpenApiHandler, { swaggerStaticFiles='/path/to/swagger-ui' })
```

Or if you are using `OpenApiConfigurator`, you can specify the location using the `staticFilesPath(...)` method (as seen in the section above.)

Enjoy!


## Contact

You can reach me on [Discord](https://discordapp.com/users/307684202080501761) or [open an Issue on Github](https://github.com/wilson0x4d/tornado-openapi/issues/new/choose).
