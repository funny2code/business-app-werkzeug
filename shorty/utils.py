from os import path
from random import randrange, sample
from urllib import response
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import MetaData
from sqlalchemy.orm import create_session, declarative_base, scoped_session
from werkzeug.local import Local, LocalManager
from werkzeug.routing import Map, Rule
from werkzeug.urls import url_parse
from werkzeug.utils import cached_property
from werkzeug.wrappers import ResponseStream, Response

from .routes import routes


TEMPLATE_PATH = path.join(path.dirname(__file__), "templates")
STATIC_PATH = path.join(path.dirname(__file__), "static")
ALLOWED_SCHEMES = frozenset(["http", "https", "ftp", "ftps"])
URL_CHARS = "abcdefghijkmpqrstuvwxyzABCDEFGHIJKLMNPQRST23456789"

local = Local()
local_manager = LocalManager([local])
application = local("application")
url_map = routes

Base = declarative_base()
metadata = Base.metadata

session = scoped_session(
    lambda: create_session(
        application.database_engine, autocommit=False, autoflush=False
    )
)
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))


def expose(rule, **kw):
    def decorate(f):
        kw["endpoint"] = f.__name__
        url_map.add(Rule(rule, **kw))
        return f

    return decorate

def url_for(endpoint, _external=False, **values):
    return local.url_adapter.build(endpoint, values, force_external=_external)


jinja_env.globals["url_for"] = url_for

def render_template(template, **context):
    response = Response(
        jinja_env.get_template(template).render(**context), mimetype="text/html"
    )
    return response


def validate_url(url):
    return url_parse(url)[0] in ALLOWED_SCHEMES


def get_random_uid():
    return "".join(sample(URL_CHARS, randrange(3, 9)))


class Pagination:
    def __init__(self, query, per_page, page, endpoint):
        self.query = query
        self.per_page = per_page
        self.page = page
        self.endpoint = endpoint

    @cached_property
    def count(self):
        return self.query.count()

    @cached_property
    def entries(self):
        return (
            self.query.offset((self.page - 1) * self.per_page)
            .limit(self.per_page)
            .all()
        )

    @property
    def has_previous(self):
        """Return True if there are pages before the current one."""
        return self.page > 1

    @property
    def has_next(self):
        """Return True if there are pages after the current one."""
        return self.page < self.pages

    @property
    def previous(self):
        """Return the URL for the previous page."""
        return url_for(self.endpoint, page=self.page - 1)

    @property
    def next(self):
        """Return the URL for the next page."""
        return url_for(self.endpoint, page=self.page + 1)

    @property
    def pages(self):
        """Return the number of pages."""
        return max(0, self.count - 1) // self.per_page + 1
