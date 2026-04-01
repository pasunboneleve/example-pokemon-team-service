from __future__ import annotations

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
    server = ThreadingHTTPServer(("127.0.0.1", 8000), PokemonRequestHandler)
    print("Serving on http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
