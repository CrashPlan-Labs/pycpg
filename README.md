# Official CrashPlan Python SDK



![Build status](https://github.com/CrashPlan-Labs/pycpg/workflows/build/badge.svg)
[![codecov.io](https://codecov.io/github/CrashPlan-Labs/pycpg/coverage.svg?branch=main)](https://codecov.io/github/CrashPlan-Labs/pycpg?branch=main)
[![versions](https://img.shields.io/pypi/pyversions/pycpg.svg)](https://pypi.org/project/pycpg/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/pycpg/badge/?version=latest)](https://pycpgdocs.crashplan.com/en/latest/?badge=latest)


`pycpg` is a Python wrapper around the CrashPlan REST APIs that also provides several other useful utility methods.
It is designed to be used for developing your own tools for working with CrashPlan data while avoiding the overhead
of session / authentication management.

## Requirements

- Python 3.11+
- CrashPlan Cloud environment (e.g. console.us1.crashplan.com or console.us2.crashplan.com)

## Installation

```bash
$ pip install pycpg
```

## Hello, pycpg

Here's a simple example to verify the installation and your server/account.

Launch the Python interpreter

```bash
$ python
```

Import a couple essentials

```python
>>> import pycpg.sdk
>>> import pycpg.util as util
```

Initialize the client.

```python
>>> sdk = pycpg.sdk.from_local_account("https://console.us1.crashplan.com", "john.doe", "password")
```
or alternatively
```
>>> sdk = pycpg.sdk.from_jwt_provider("https://console.us1.crashplan.com", jwt_provider_function)
```

Get and print your user information.

```python
>>> response = sdk.users.get_current()
>>> util.print_response(response)
```

You should see something like the following:

```json
{
    "username": "john.doe",
    "orgName": "ACME Organization",
    "userId": 123456,
    "emailPromo": true,
    "licenses": [],
    "modificationDate": "2018-08-29T15:32:56.995-05:00",
    "blocked": false,
    "usernameIsAnEmail": true,
    "userUid": "1234567890abcdef",
    "userExtRef": null,
    "email": "john.doe@acme.com",
    "status": "Active",
    "localAuthenticationOnly": false,
    "orgUid": "123456789123456789",
    "passwordReset": true,
    "active": true,
    "creationDate": "2012-01-16T11:25:43.545-06:00",
    "orgType": "BUSINESS",
    "firstName": "John",
    "lastName": "Doe",
    "notes": null,
    "orgId": 123456,
    "quotaInBytes": -1,
    "invited": false
}
```

## Configuration

There are a few default settings that affect the behavior of the client.

| Name | Description | Default |
| ---- | ----------- | ------- |
| verify_ssl_certs | Controls whether the SDK verifies the server's certificate.<br>Possible values: `True`, `False`, or a path to a CA bundle to use.| `True`
| proxies | Dictionary mapping protocol or protocol and hostname to the URL of the proxy.<br>See [the Requests library's documentation on proxies](https://requests.readthedocs.io/en/latest/user/advanced/?highlight=proxy#proxies) for more info.| `None`
| debug.level | Controls log level | `logging.NOTSET`
| debug.logger | Controls logger used | `logging.Logger` with `StreamHandler` sending to `sys.stderr`
| items_per_page | Controls how many items are retrieved per request for methods that loops over several "pages" of items in order to collect them all. | 500

To override these settings, import `pycpg.settings` and override values as necessary before creating the client.
 For example, to disable certificate validation in a dev environment:

```python
import pycpg.sdk
import pycpg.settings as settings
import logging

settings.verify_ssl_certs = False

# customize logging
custom_logger = logging.getLogger("my_app")
handler = logging.FileHandler("my_app.log")
custom_logger.addHandler(handler)
settings.debug.logger = custom_logger
settings.debug.level = logging.DEBUG

sdk = pycpg.sdk.from_local_account("https://console.us1.crashplan.com", "my_username", "my_password")
```

## Usage

The SDK object opens availability to APIs across the CrashPlan environment, including storage nodes.

```python
import pycpg.sdk

sdk = pycpg.sdk.from_local_account("https://console.us1.crashplan.com", "my_username", "my_password")

# clients are organized by feature groups and accessible under the sdk object

# get information about the current user.
current_user = sdk.users.get_current()

# page through all devices available to this user.
for device_page in sdk.devices.get_all():
    for device in device_page["computers"]:
        print(device)

# page through all orgs available to this user.
for org_page in sdk.orgs.get_all():
    for org in org_page["orgs"]:
        print(org)

# save a copy of a file from an archive this user has access to into the current working directory.
stream_response = sdk.archive.stream_from_backup("/full/path/to/file.txt", "1234567890")
with open("/path/to/my/file", 'wb') as f:
    for chunk in stream_response.iter_content(chunk_size=128):
        if chunk:
            f.write(chunk)

## Additional Resources

For complete documentation on the CrashPlan web API that backs this SDK, here are some helpful resources:

- [Introduction to the CrashPlan API](https://support.crashplan.com/hc/en-us/articles/9057001723917--CrashPlan-API-syntax-and-usage)
- [CrashPlan API documentation viewers](https://support.crashplan.com/hc/en-us/articles/9057096803469--CrashPlan-API-documentation-viewer-reference)
