"""
Publish dist/ to Netlify (site "aafaqcs" -> https://aafaqcs.netlify.app). Plain Python 3, no installs.

    python3 build.py && python3 deploy.py

Needs a Netlify personal access token, read from the NETLIFY_AUTH_TOKEN environment variable or from the file
~/.config/netlify_token (create it once; it is never stored inside this project). Create the token at
app.netlify.com -> avatar -> User settings -> Applications -> Personal access tokens -> New access token.
Only the contents of dist/ are uploaded (index.html at the top level), so the source files never go online.
"""

import io
import json
import os
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE_NAME = "aafaqcs"
API = "https://api.netlify.com/api/v1"


def token():
    t = os.environ.get("NETLIFY_AUTH_TOKEN")
    f = Path.home() / ".config" / "netlify_token"
    if not t and f.exists():
        t = f.read_text().strip()
    if not t:
        sys.exit("No token: set NETLIFY_AUTH_TOKEN or save it in ~/.config/netlify_token")
    return t


def call(method, path, tok, data=None, ctype="application/json"):
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": ctype, "User-Agent": "aafaqcs-deploy"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        sys.exit(f"Netlify API {method} {path} failed: HTTP {e.code} {e.read()[:300]!r}")


def main():
    if not (DIST / "index.html").exists():
        sys.exit("dist/index.html missing: run  python3 build.py  first")
    tok = token()
    sites = call("GET", "/sites?per_page=100", tok)
    site = next((s for s in sites if s["name"] == SITE_NAME), None)
    if site is None:
        sys.exit(f"No site named '{SITE_NAME}' in this Netlify account. Found: {[s['name'] for s in sites]}")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(DIST.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(DIST).as_posix())
    n = sum(1 for f in DIST.rglob("*") if f.is_file())
    print(f"Uploading {n} files ({buf.tell() / 1e6:.1f} MB) to {site['name']} ...")
    d = call("POST", f"/sites/{site['id']}/deploys", tok, buf.getvalue(), "application/zip")
    print("Deploy state:", d.get("state"), "| live at", site.get("ssl_url") or site.get("url"))


if __name__ == "__main__":
    main()
