"""
Push this website's source to GitHub without git (plain Python 3, GitHub REST API).

    python3 push_github.py "commit message"

Settings: GITHUB_REPO below (owner is taken from the token). The token is read from GITHUB_TOKEN or the file
~/.config/github_token (never stored in the project). It needs permission to write repository contents: a classic token
with the "repo" scope, or a fine-grained token with "Contents: Read and write" (plus "Administration: write" if the
script should create the repository). Files matching .gitignore are skipped. Each push uploads a full snapshot,
so files deleted here are deleted on GitHub too.
"""

import base64
import fnmatch
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GITHUB_REPO = "aafaqcs-website"
PRIVATE = False
API = "https://api.github.com"


def token():
    t = os.environ.get("GITHUB_TOKEN")
    f = Path.home() / ".config" / "github_token"
    if not t and f.exists():
        t = f.read_text().strip()
    if not t:
        sys.exit("No token: set GITHUB_TOKEN or save it in ~/.config/github_token")
    return t


def call(method, path, tok, body=None, ok404=False):
    req = urllib.request.Request(API + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                                          "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "aafaqcs-push"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        if ok404 and e.code in (404, 409):
            return None
        sys.exit(f"GitHub API {method} {path} failed: HTTP {e.code} {e.read()[:400]!r}")


def ignored(rel, patterns):
    parts = rel.split("/")
    for p in patterns:
        p = p.rstrip("/")
        if fnmatch.fnmatch(rel, p) or any(fnmatch.fnmatch(x, p) for x in parts):
            return True
    return False


def files():
    pats = [l.strip() for l in (ROOT / ".gitignore").read_text().splitlines() if l.strip() and not l.startswith("#")]
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT).as_posix()
        if f.is_file() and not ignored(rel, pats):
            yield rel, f


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "Update website"
    tok = token()
    owner = call("GET", "/user", tok)["login"]
    repo = call("GET", f"/repos/{owner}/{GITHUB_REPO}", tok, ok404=True)
    if repo is None:
        print(f"Creating repository {owner}/{GITHUB_REPO} ({'private' if PRIVATE else 'public'}) ...")
        repo = call("POST", "/user/repos", tok, {"name": GITHUB_REPO, "private": PRIVATE, "auto_init": True,
                                                  "description": "Source of aafaqcs.com: Dr. Aafaq Mohi Ud Din's academic website (plain-Python static site)"})
    full, branch = repo["full_name"], repo.get("default_branch") or "main"
    ref = call("GET", f"/repos/{full}/git/ref/heads/{branch}", tok, ok404=True)
    if ref is None:            # empty repository: create the first commit through the contents API
        call("PUT", f"/repos/{full}/contents/.gitkeep", tok, {"message": "Initial commit", "content": "", "branch": branch})
        ref = call("GET", f"/repos/{full}/git/ref/heads/{branch}", tok)
    parent = ref["object"]["sha"]
    tree, n, size = [], 0, 0
    for rel, f in files():
        data = f.read_bytes()
        blob = call("POST", f"/repos/{full}/git/blobs", tok, {"content": base64.b64encode(data).decode(), "encoding": "base64"})
        tree.append({"path": rel, "mode": "100755" if os.access(f, os.X_OK) and f.suffix == ".py" else "100644", "type": "blob", "sha": blob["sha"]})
        n, size = n + 1, size + len(data)
    t = call("POST", f"/repos/{full}/git/trees", tok, {"tree": tree})
    c = call("POST", f"/repos/{full}/git/commits", tok, {"message": msg, "tree": t["sha"], "parents": [parent]})
    call("PATCH", f"/repos/{full}/git/refs/heads/{branch}", tok, {"sha": c["sha"]})
    print(f"Pushed {n} files ({size / 1e6:.1f} MB) -> https://github.com/{full}  (commit {c['sha'][:7]})")


if __name__ == "__main__":
    main()
