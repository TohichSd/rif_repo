import json
import unittest
from wsgiref.util import setup_testing_defaults

from app import application


class ApplicationTest(unittest.TestCase):
    def request(self, path, method="GET"):
        environ = {"PATH_INFO": path, "REQUEST_METHOD": method}
        setup_testing_defaults(environ)
        response = {}

        def start_response(status, headers):
            response.update(status=status, headers=dict(headers))

        response["body"] = b"".join(application(environ, start_response))
        return response

    def test_index_identifies_the_application(self):
        response = self.request("/")
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(json.loads(response["body"]), {"app": "rif-ci-practice"})

    def test_health_endpoint(self):
        response = self.request("/health")
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(json.loads(response["body"]), {"status": "ok"})

    def test_health_head_returns_headers_without_a_body(self):
        response = self.request("/health", "HEAD")
        self.assertEqual(response["status"], "200 OK")
        self.assertEqual(response["body"], b"")
        self.assertGreater(int(response["headers"]["Content-Length"]), 0)

    def test_missing_route_returns_404(self):
        self.assertEqual(self.request("/missing")["status"], "404 Not Found")

    def test_health_rejects_post_with_allow_header(self):
        response = self.request("/health", "POST")
        self.assertEqual(response["status"], "405 Method Not Allowed")
        self.assertEqual(response["headers"]["Allow"], "GET, HEAD")
