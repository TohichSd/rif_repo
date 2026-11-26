import json
import os
from http import HTTPStatus
from wsgiref.simple_server import make_server


def application(environ, start_response):
    path = environ["PATH_INFO"]
    method = environ["REQUEST_METHOD"]
    headers = [("Content-Type", "application/json; charset=utf-8")]

    if path not in {"/", "/health"}:
        status, payload = HTTPStatus.NOT_FOUND, {"error": "not found"}
    elif method not in {"GET", "HEAD"}:
        status, payload = HTTPStatus.METHOD_NOT_ALLOWED, {"error": "method not allowed"}
        headers.append(("Allow", "GET, HEAD"))
    elif path == "/health":
        status, payload = HTTPStatus.OK, {"status": "ok"}
    else:
        status, payload = HTTPStatus.OK, {"app": "rif-ci-practice"}

    body = json.dumps(payload).encode("utf-8")
    headers.append(("Content-Length", str(len(body))))
    start_response(f"{status.value} {status.phrase}", headers)
    return [] if method == "HEAD" else [body]


def main():
    port = int(os.environ.get("PORT", "8080"))
    with make_server("127.0.0.1", port, application) as server:
        print(f"http://127.0.0.1:{port}", flush=True)
        server.serve_forever()
