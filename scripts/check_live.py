"""Verify that the public Pages URL serves the files from this build."""
from pathlib import Path
import sys
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen


def response(url):
    request = Request(url, headers={"Cache-Control": "no-cache"})
    try:
        stream = urlopen(request, timeout=15)
    except HTTPError as error:
        stream = error
    with stream:
        return stream.status, stream.read()


def verify(base):
    dist = Path(__file__).resolve().parents[1] / "dist"
    paths = sorted(path for path in dist.rglob("*") if path.is_file())
    for path in paths:
        relative = path.relative_to(dist).as_posix()
        url = base if relative == "index.html" else urljoin(base, quote(relative))
        status, body = response(url)
        if status != 200 or body != path.read_bytes():
            raise ValueError(f"{url} returned HTTP {status}, or its content differs from the build")

    status, body = response(urljoin(base, "missing/check/deep-link.html"))
    archive = urlsplit(urljoin(base, "index.html")).path + "#archive"
    if status != 404 or f'href="{archive}"'.encode() not in body:
        raise ValueError(f"Nested missing page returned HTTP {status}, or lacks the archive link")
    print(f"Verified {len(paths)} published files and the nested 404 at {base}")


if __name__ == "__main__":
    base = sys.argv[1].rstrip("/") + "/"
    for attempt in range(6):
        try:
            verify(base)
            break
        except (OSError, URLError, ValueError) as error:
            if attempt == 5:
                raise
            print(f"{error}. Retrying in 10 seconds.", flush=True)
            sleep(10)
