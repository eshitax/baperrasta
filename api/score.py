from _lib import score_response, send
from _wsgi import make_wsgi, read_json


def route(environ):
    return send(score_response(read_json(environ)))


app = make_wsgi(route)
