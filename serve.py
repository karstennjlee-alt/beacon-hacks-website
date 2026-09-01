#!/usr/bin/env python3
"""Threaded static server for the Beacon Hacks site.

python3 -m http.server is single threaded: one slow client stalls everyone
else, which shows up fast when a few people open the page at once. This
serves the same directory with a thread per connection.

    ./serve.py [port]        # default 8791, localhost only
"""
import functools
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8791


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def end_headers(self):
        # The countdown and prices change; don't let anyone cache a stale copy.
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    handler = functools.partial(Handler, directory=ROOT)
    # Bind to loopback only: Tailscale Funnel/Serve proxies in from there.
    server = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    server.daemon_threads = True
    print("Serving %s on http://127.0.0.1:%d" % (ROOT, PORT), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
