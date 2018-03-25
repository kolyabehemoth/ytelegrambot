"""  copy/paste from  https://github.com/biocommons/hgvs project. thx opensource """
import re
import os
from configparser import ConfigParser, ExtendedInterpolation
from copy import copy
from pkg_resources import resource_stream
from urllib.parse import urlparse
from urllib.parse import ParseResult


class Config(object):
    def __init__(self, extended_interpolation=True):
        if extended_interpolation:
            cp = ConfigParser(interpolation=ExtendedInterpolation())
        else:
            cp = ConfigParser()
        cp.optionxform = _name_xform
        self._cp = cp

    def read_stream(self, flo):
        self._cp.read_string(flo.read().decode('ascii'))

    def __copy__(self):
        new_config = Config.__new__(Config)
        new_config._cp = object.__getattribute__(self, '_cp')
        return new_config

    def __dir__(self):
        return list(self._cp.keys())

    def __getattr__(self, k):
        if k == "_cp":
            return
        try:
            return ConfigGroup(self._cp[k])
        except KeyError:
            raise AttributeError(k)

    __getitem__ = __getattr__


class ConfigGroup(object):
    def __init__(self, section):
        self.__dict__["_section"] = section

    def __dir__(self):
        return list(self.__dict__["_section"].keys())

    def __getattr__(self, k):
        return _val_xform(self.__dict__["_section"][k])

    __getitem__ = __getattr__

    def __setattr__(self, k, v):
        self.__dict__["_section"][k] = str(v)

    __setitem__ = __setattr__


def _name_xform(o):
    return re.sub("\W", "_", o.lower())


def _val_xform(v):
    if v == "True":
        return True
    if v == "False":
        return False
    if v == "None":
        return None
    try:
        return int(v)
    except ValueError:
        pass
    return v


class ParseResult(ParseResult):
    """Subclass of url.ParseResult that adds database and schema methods,
    and provides stringification.

    """

    def __new__(cls, pr):
        return super(ParseResult, cls).__new__(cls, *pr)

    @property
    def database(self):
        path_elems = self.path.split("/")
        return path_elems[1] if len(path_elems) > 1 else None

    @property
    def schema(self):
        path_elems = self.path.split("/")
        return path_elems[2] if len(path_elems) > 2 else None

    def __str__(self):
        return self.geturl()


def _parse_url(db_url):
    return '' if not db_url else ParseResult(urlparse(db_url))


_default_config = Config()
_default_config.read_stream(resource_stream(__name__, "config.ini"))
_default_config.web_host = os.environ.get('host')
_default_config.db_url = _parse_url(os.environ.get('DATABASE_URL') + '/public')
_default_config.telegram_token = os.environ.get('telegram_token')
_default_config.google_api_key = os.environ.get('google_api_key')


_test_config = copy(_default_config)
_test_config.__dict__ = _default_config.__dict__.copy()
_test_config.db_url = _parse_url('postgres://behemoth:root@localhost:5432/telegram_bot/public')
_test_config.web_host = 'http://localhost'

global_config = copy(_default_config)
global_config.__dict__ = _default_config.__dict__
