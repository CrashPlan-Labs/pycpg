import sys
from importlib.metadata import version

proxies = None

# Controls whether we verify the server's certificate.
# True, False, or a path to a CA bundle to use.
verify_ssl_certs = True

items_per_page = 500

_custom_user_prefix = ""
_custom_user_suffix = ""
_python_version = f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"


def get_user_agent_string():
    return "{}pycpg/{} python/{}{}".format(
        _custom_user_prefix, version("pycpg"), _python_version, _custom_user_suffix
    )


def set_user_agent_suffix(suffix):
    global _custom_user_suffix
    _custom_user_suffix = f" {suffix}" if suffix else ""


def set_user_agent_prefix(prefix):
    global _custom_user_prefix
    _custom_user_prefix = f"{prefix} " if prefix else ""
