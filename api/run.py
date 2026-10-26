import secrets

from _lib import send
from _wsgi import make_wsgi


def route(environ):
    return send({"t": secrets.token_urlsafe(16), "ok": True})


app = make_wsgi(route)
