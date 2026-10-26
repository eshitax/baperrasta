import json


def make_wsgi(route_fn):
    def app(environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        if method == "OPTIONS":
            start_response(
                "204 No Content",
                [
                    ("Access-Control-Allow-Origin", "*"),
                    ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                    ("Access-Control-Allow-Headers", "Content-Type"),
                ],
            )
            return [b""]
        result = route_fn(environ)
        status_code = result["statusCode"]
        headers = [
            (k, v) for k, v in result["headers"].items()
        ]
        body = result["body"].encode("utf-8")
        start_response(f"{status_code} {'OK' if status_code < 400 else 'Error'}", headers + [("Content-Length", str(len(body)))])
        return [body]

    return app


def read_json(environ):
    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length) if length else b"{}"
    try:
        return json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        return {}
