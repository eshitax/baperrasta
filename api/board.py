from _lib import fetch_live_board, send
from _wsgi import make_wsgi


def route(environ):
    return send(fetch_live_board())


app = make_wsgi(route)
