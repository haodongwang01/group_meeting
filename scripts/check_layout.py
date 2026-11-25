"""Check the weekly roster and the latest meeting before Pages uploads the site."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import json
import subprocess


DIST = Path(__file__).resolve().parents[1] / "dist"
PROBE = b"""<!doctype html><meta charset="utf-8"><main></main>
<script>
const checks = [];
function probe(width, url, check) {
  checks.push(new Promise((resolve, reject) => {
    const frame = document.createElement('iframe');
    frame.style.width = width + 'px';
    frame.onload = async () => {
      try {
        const doc = frame.contentDocument;
        resolve(await check(doc) && doc.documentElement.scrollWidth <= width);
      } catch (error) { reject(error); }
    };
    frame.src = url;
    document.querySelector('main').append(frame);
  }));
}
for (const width of [320, 390]) {
  probe(width, '/weekly/index.html', doc => {
    const row = doc.querySelector('.w-rows li');
    const name = row.querySelector('.w-name');
    const content = row.children[1];
    const nav = doc.querySelector('.site-header a[href$="weekly/index.html"]');
    const button = doc.querySelector('.w-weeks summary');
    button.click();
    return nav.getClientRects().length &&
      name.getBoundingClientRect().bottom <= content.getBoundingClientRect().top &&
      doc.querySelector('.w-weeks[open] nav a').getClientRects().length;
  });
}
for (const width of [390, 1280]) {
  probe(width, LATEST_MEETING, async doc => {
    const links = [...doc.querySelectorAll('.toc a[href^="#"]')];
    if (!doc.querySelector('.article-header h1') || !links.length ||
        !links.every(link => doc.getElementById(link.hash.slice(1)))) return false;
    for (const section of doc.querySelectorAll('.evidence')) section.open = true;
    for (const img of doc.querySelectorAll('.prose figure img')) {
      img.loading = 'eager';
      await img.decode();
      if (!img.naturalWidth || !img.alt || !img.closest('figure').querySelector('figcaption')) return false;
      const zoom = img.closest('a.zoom');
      if (zoom) {
        zoom.click();
        const dialog = doc.querySelector('#lightbox');
        if (!dialog.open || dialog.querySelector('img').src !== zoom.href) return false;
        dialog.close();
      }
    }
    return true;
  });
}
Promise.all(checks).then(results => {
  if (results.every(Boolean)) document.body.dataset.checked = 'yes';
});
</script>"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/probe":
            return super().do_GET()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.server.probe)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=DIST)) as server:
        meetings = json.loads((DIST.parent / "content" / "meetings.json").read_text(encoding="utf-8"))
        url = f"/meetings/{meetings[0]['date']}.html"
        server.probe = PROBE.replace(b"LATEST_MEETING", json.dumps(url).encode())
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            dom = subprocess.check_output([
                "google-chrome", "--headless", "--disable-gpu", "--dump-dom",
                "--virtual-time-budget=4000", f"http://127.0.0.1:{server.server_port}/probe",
            ], timeout=40)
            if b'<body data-checked="yes">' not in dom:
                raise SystemExit("Weekly roster or latest meeting layout failed browser checks")
            print(f"Verified weekly layout at 320/390 px and {url} at 390/1280 px (TOC, figures, zoom, overflow).")
        finally:
            server.shutdown()
