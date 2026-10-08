"""
Publish the built site (dist/) to GitHub Pages at https://aafaqcs.github.io  (plain Python 3, no git needed).

    python3 build.py && python3 push_pages.py "message"

Uses the same token as push_github.py (~/.config/github_token, 'repo' scope). The repository <owner>.github.io is created
on first run; GitHub serves it automatically from its main branch. Each push is a full snapshot of dist/.
"""

import base64
import json
import sys
import time
from pathlib import Path

import push_github as pg

DIST = Path(__file__).resolve().parent / "dist"


def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else "Update site"
    tok = pg.token()
    owner = pg.call("GET", "/user", tok)["login"]
    name = f"{owner}.github.io"
    repo = pg.call("GET", f"/repos/{owner}/{name}", tok, ok404=True)
    if repo is None:
        print(f"Creating repository {owner}/{name} ...")
        repo = pg.call("POST", "/user/repos", tok, {"name": name, "private": False, "auto_init": True,
                                                    "description": "Dr. Aafaq Mohi Ud Din: courses, teaching material and research (built site)"})
        time.sleep(3)
    full, branch = repo["full_name"], repo.get("default_branch") or "main"
    ref = pg.call("GET", f"/repos/{full}/git/ref/heads/{branch}", tok, ok404=True)
    if ref is None:
        pg.call("PUT", f"/repos/{full}/contents/.gitkeep", tok, {"message": "Initial commit", "content": "", "branch": branch})
        ref = pg.call("GET", f"/repos/{full}/git/ref/heads/{branch}", tok)
    (DIST / ".nojekyll").write_text("")
    tree, size = [], 0
    for f in sorted(DIST.rglob("*")):
        if f.is_file():
            data = f.read_bytes()
            blob = pg.call("POST", f"/repos/{full}/git/blobs", tok, {"content": base64.b64encode(data).decode(), "encoding": "base64"})
            tree.append({"path": f.relative_to(DIST).as_posix(), "mode": "100644", "type": "blob", "sha": blob["sha"]})
            size += len(data)
    t = pg.call("POST", f"/repos/{full}/git/trees", tok, {"tree": tree})
    c = pg.call("POST", f"/repos/{full}/git/commits", tok, {"message": msg, "tree": t["sha"], "parents": [ref["object"]["sha"]]})
    pg.call("PATCH", f"/repos/{full}/git/refs/heads/{branch}", tok, {"sha": c["sha"]})
    pages = pg.call("GET", f"/repos/{full}/pages", tok, ok404=True)
    if pages is None:
        pg.call("POST", f"/repos/{full}/pages", tok, {"source": {"branch": branch, "path": "/"}}, ok404=True)
    print(f"Published {len(tree)} files ({size / 1e6:.1f} MB) -> https://{name}  (commit {c['sha'][:7]})")


if __name__ == "__main__":
    main()
