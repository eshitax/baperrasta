from _lib import send
from _wsgi import make_wsgi, read_json


def route(environ):
    body = read_json(environ)
    name = str(body.get("name") or "").strip()[:24]
    if not name:
        return send({"ok": False, "error": "empty"}, 400)
    return send({"ok": True, "name": name})


app = make_wsgi(route)
