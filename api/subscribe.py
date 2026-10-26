from _lib import send
from _wsgi import make_wsgi, read_json


def route(environ):
    body = read_json(environ)
    email = str(body.get("email") or "").strip()
    if "@" not in email:
        return send({"ok": False}, 400)
    return send({"ok": True})


app = make_wsgi(route)
