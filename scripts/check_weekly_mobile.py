"""Check the generated report layout inside phone-sized browser viewports."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import subprocess


DIST = Path(__file__).resolve().parents[1] / "dist"
PROBE = b"""<!doctype html><meta charset="utf-8"><main></main>
<script>
const results = [];
for (const width of [320, 390]) {
  const frame = document.createElement('iframe');
  frame.style.width = width + 'px';
  frame.onload = () => {
    const doc = frame.contentDocument;
    const row = doc.querySelector('.w-rows li');
    const name = row.querySelector('.w-name');
    const content = row.children[1];
    const nav = doc.querySelector('.site-header a[href$="weekly/index.html"]');
    const button = doc.querySelector('.w-weeks summary');
    button.click();
    const ok = doc.documentElement.scrollWidth <= width && nav.getClientRects().length &&
      name.getBoundingClientRect().bottom <= content.getBoundingClientRect().top &&
      doc.querySelector('.w-weeks[open] nav a').getClientRects().length;
    results.push(!!ok);
    if (results.length === 2 && results.every(Boolean)) document.body.dataset.checked = 'yes';
  };
  frame.src = '/weekly/index.html';
  document.querySelector('main').append(frame);
}
</script>"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/probe":
            return super().do_GET()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(PROBE)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=DIST)) as server:
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            dom = subprocess.check_output([
                "google-chrome", "--headless", "--disable-gpu", "--dump-dom",
                "--virtual-time-budget=4000", f"http://127.0.0.1:{server.server_port}/probe",
            ], timeout=40)
            if b'<body data-checked="yes">' not in dom:
                raise SystemExit("Weekly navigation, layout or week selection failed on mobile")
            print("Weekly navigation, stacked rows and week selection passed at 320 and 390 pixels.")
        finally:
            server.shutdown()
