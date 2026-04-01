from __future__ import annotations

import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pokemon_service.handler import handler


class PokemonRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query_params = {
            key: values[-1]
            for key, values in parse_qs(parsed.query, keep_blank_values=True).items()
        }
        event = {
            "rawPath": parsed.path,
            "queryStringParameters": query_params or None,
            "requestContext": {"http": {"method": "GET"}},
        }
        response = handler(event, None)
        body = response["body"].encode("utf-8")

        self.send_response(response["statusCode"])
        for header_name, header_value in response["headers"].items():
            self.send_header(header_name, header_value)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host = os.environ.get("POKEMON_SERVICE_HOST", "127.0.0.1")
    port = int(os.environ.get("POKEMON_SERVICE_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), PokemonRequestHandler)
    print(f"Serving on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
