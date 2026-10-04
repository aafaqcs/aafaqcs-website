"""
aafaqcs.com — static site generator (no installs: plain Python 3).

    python3 build.py            -> writes the whole site into dist/

Content lives in data/*.json (profile, courses, classes, publications). Edit those and rebuild; never edit dist/ by hand.
Publish: drag the dist/ folder onto https://app.netlify.com/drop (free), later point aafaqcs.com at it.
"""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
D = lambda name: json.load(open(ROOT / "data" / f"{name}.json", encoding="utf-8"))
E = html.escape

CSS = """
:root{--bg:#ffffff;--soft:#f2f7f6;--line:#dfeae8;--ink:#14212b;--muted:#5a6b78;--brand:#0e8a7e;--brand-ink:#ffffff;--live:#dff5f1;--live-ink:#0b6e64;--soon:#f1f3f6;--soon-ink:#6b7785;--warm:#ffb25e;
 --display:"Plus Jakarta Sans",ui-sans-serif,system-ui,sans-serif;--body:"Plus Jakarta Sans",ui-sans-serif,system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1517;--soft:#141d20;--line:#24323a;--ink:#e6eef0;--muted:#97a8b2;--brand:#2fc4b4;--brand-ink:#08201d;--live:#123832;--live-ink:#7fe3d6;--soon:#1b2428;--soon-ink:#93a1aa;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0f1517;--soft:#141d20;--line:#24323a;--ink:#e6eef0;--muted:#97a8b2;--brand:#2fc4b4;--brand-ink:#08201d;--live:#123832;--live-ink:#7fe3d6;--soon:#1b2428;--soon-ink:#93a1aa;color-scheme:dark}
:root[data-theme="light"]{color-scheme:light}
.theme{display:flex;gap:2px;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:3px;margin-top:auto}
.theme button{flex:1;border:0;background:none;color:var(--muted);font:600 12px var(--body);padding:6px 4px;border-radius:7px;cursor:pointer}
.theme button[aria-pressed="true"]{background:var(--brand);color:var(--brand-ink)}
.topbar .theme{margin:0}
.ccard{border:1px solid var(--line);border-radius:16px;overflow:hidden;text-decoration:none;display:grid;grid-template-rows:auto 1fr;min-width:0;transition:transform .15s,border-color .15s}
.ccard:hover{transform:translateY(-3px);border-color:var(--brand)}
.ccard img,.ccard .ph{aspect-ratio:16/9;object-fit:cover;width:100%}.ccard .ph{background:repeating-linear-gradient(45deg,var(--soon),var(--soon) 10px,var(--bg) 10px,var(--bg) 20px)}
.ccard .in{padding:14px 16px 16px;display:grid;gap:8px;align-content:start}.ccard b{font-size:17px;font-family:var(--display)}.ccard p{margin:0;color:var(--muted);font-size:14px}
.chero{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:28px;align-items:center}.chero img{border-radius:14px;aspect-ratio:16/9;object-fit:cover;width:100%;border:1px solid var(--line)}
.crumb{font-size:13px;color:var(--muted)}.crumb a{color:var(--brand);text-decoration:none;font-weight:600}
@media (max-width:820px){.chero{grid-template-columns:1fr}}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.6}
a{color:inherit}img{max-width:100%;display:block}
.shell{display:grid;grid-template-columns:240px minmax(0,1fr);min-height:100vh}
aside{background:var(--soft);border-right:1px solid var(--line);padding:22px 16px;position:sticky;top:0;height:100vh;overflow:auto;display:flex;flex-direction:column;gap:4px}
.logo{font-weight:800;font-size:17px;text-decoration:none;margin-bottom:6px;display:block}.logo b{color:var(--brand)}
.who-mini{display:flex;gap:10px;align-items:center;font-size:12px;color:var(--muted);margin-bottom:18px}.who-mini img{width:36px;height:36px;border-radius:50%;object-fit:cover}
.navlabel{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:14px 10px 4px}
aside a.nav{padding:8px 10px;border-radius:8px;color:var(--muted);text-decoration:none;font-weight:600;font-size:14px}
aside a.nav:hover{background:var(--line);color:var(--ink)}aside a.nav.on{background:var(--brand);color:var(--brand-ink)}
main{padding:28px clamp(16px,4vw,48px) 60px;min-width:0;display:grid;gap:28px;align-content:start;max-width:1100px}
h1{font-family:var(--display);font-weight:800;font-size:clamp(28px,4vw,44px);line-height:1.1;margin:0;text-wrap:balance}
h2{font-family:var(--display);font-weight:800;font-size:clamp(20px,2.4vw,26px);margin:0}
.lede{color:var(--muted);max-width:62ch;margin:6px 0 0}
.hero{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center}
.hero img{width:150px;height:150px;border-radius:50%;object-fit:cover;border:4px solid var(--brand)}
.btns{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}
.btn{display:inline-block;padding:10px 16px;border-radius:10px;font-weight:700;font-size:14px;text-decoration:none;border:2px solid var(--brand)}
.btn.p{background:var(--brand);color:var(--brand-ink)}.btn.s{color:var(--brand)}
.track{border:1px solid var(--line);border-radius:14px;padding:18px;display:grid;gap:14px}
.track .t{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-weight:700}
.meta{font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.prog{height:10px;background:var(--soon);border-radius:99px;overflow:hidden}.prog i{display:block;height:100%;background:var(--brand)}
.lessons{display:grid;gap:8px}
.lesson{display:grid;grid-template-columns:120px minmax(0,1fr) auto;gap:14px;align-items:center;border:1px solid var(--line);border-radius:12px;padding:8px 12px 8px 8px;text-decoration:none}
.lesson img,.lesson .ph{width:120px;aspect-ratio:16/9;border-radius:8px;object-fit:cover}
.lesson .ph{background:repeating-linear-gradient(45deg,var(--soon),var(--soon) 8px,var(--bg) 8px,var(--bg) 16px)}
.lesson b{display:block;font-size:15px}.lesson small{color:var(--muted);font-size:12.5px}
.code{font-family:var(--mono);font-size:12px;color:var(--brand);font-weight:700;margin-right:6px}
.pill{font-size:12px;font-weight:700;padding:4px 10px;border-radius:99px;white-space:nowrap}
.pill.live{background:var(--live);color:var(--live-ink)}.pill.soon{background:var(--soon);color:var(--soon-ink)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;display:grid;min-width:0}
.card img{aspect-ratio:16/9;object-fit:cover;width:100%}
.card div{padding:12px 14px}.card b{display:block}.card small{color:var(--muted)}
.pubs{display:grid;gap:12px}.pub{border-left:3px solid var(--brand);padding:2px 0 2px 14px}
.pub b{display:block}.pub small{color:var(--muted)}
.stats{display:flex;gap:12px;flex-wrap:wrap}.stat{border:1px solid var(--line);border-radius:12px;padding:10px 16px}
.stat b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.stat small{color:var(--muted);font-size:12px}
.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{background:var(--soft);border:1px solid var(--line);border-radius:99px;padding:4px 12px;font-size:13px;font-weight:600}
.empty{border:1px dashed var(--line);border-radius:14px;padding:22px;color:var(--muted)}
.links{display:flex;gap:10px;flex-wrap:wrap}
.bio{max-width:70ch;font-size:17px;margin:0}
.story{display:grid;gap:14px;max-width:72ch}
.story blockquote{margin:0 0 6px;padding:18px 22px;border-left:5px solid var(--brand);background:var(--soft);border-radius:0 14px 14px 0;font-family:var(--display);font-weight:700;font-size:clamp(19px,2.3vw,24px);line-height:1.35;text-wrap:balance}
.story p{margin:0;font-size:16.5px;color:var(--muted)}.story p.lead{font-size:18.5px;color:var(--ink)}
.hls{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-top:8px}
.hl{border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:linear-gradient(160deg,var(--live),transparent 70%)}
.hl b{display:block;font-family:var(--display);font-weight:800;font-size:28px;line-height:1.1;color:var(--brand)}.hl small{color:var(--muted);font-size:12.5px;line-height:1.3;display:block;margin-top:4px}
h3.sub{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:10px 0 2px}
.tl{display:grid;gap:14px}.tli{display:grid;grid-template-columns:150px minmax(0,1fr);gap:16px}
.tli .when{font-family:var(--mono);font-size:12.5px;color:var(--brand);padding-top:3px}.tli b{display:block}.tli small{color:var(--muted)}
.tli ul{margin:6px 0 0;padding-left:18px;color:var(--muted);font-size:14.5px}
ul.plain{margin:8px 0 0;padding-left:18px;display:grid;gap:4px}
.two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}
@media (max-width:820px){.tli{grid-template-columns:1fr;gap:2px}.two{grid-template-columns:1fr}}
footer{color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:16px}
.topbar{display:none}
@media (max-width:820px){.shell{grid-template-columns:1fr}aside{display:none}
 .topbar{display:flex;gap:14px;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--bg);z-index:2;flex-wrap:wrap}
 .topbar nav{display:flex;gap:12px;font-weight:600;font-size:14px;flex-wrap:wrap}.topbar a{text-decoration:none}
 .hero{grid-template-columns:1fr}.hero img{width:110px;height:110px}
 .lesson{grid-template-columns:88px minmax(0,1fr)}.lesson img,.lesson .ph{width:88px}.lesson .pill{grid-column:2;justify-self:start}}
"""

FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap">'

THEME = '<div class="theme" role="group" aria-label="Theme"><button data-t="light">Light</button><button data-t="dark">Dark</button><button data-t="auto">Auto</button></div>'
THEME_JS = """<script>(function(){var r=document.documentElement,t="auto";try{t=localStorage.getItem("theme")||"auto"}catch(e){}
function set(v){t=v;if(v==="auto")r.removeAttribute("data-theme");else r.setAttribute("data-theme",v);try{localStorage.setItem("theme",v)}catch(e){}
document.querySelectorAll(".theme button").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.t===v)})}
set(t);document.addEventListener("DOMContentLoaded",function(){set(t);document.querySelectorAll(".theme button").forEach(function(b){b.onclick=function(){set(b.dataset.t)}})})})()</script>"""


def page(path, title, body, prof, courses, active, desc):
    depth = path.count("/")
    up = "../" * depth
    nav_courses = "".join(f'<a class="nav{" on" if active == c["slug"] else ""}" href="{up}courses/{c["slug"]}.html">{E(c["short"])}</a>' for c in courses)
    side = f"""<aside><a class="logo" href="{up}index.html">aafaq<b>cs</b></a>
<div class="who-mini"><img src="{up}assets/img/photo.jpg" alt=""><span>{E(prof["name"])}<br>{E(prof["title"].split(",")[0])}</span></div>
<a class="nav{" on" if active == "about" else ""}" href="{up}index.html">About &amp; research</a>
<div class="navlabel">Video courses</div><a class="nav{" on" if active == "home" else ""}" href="{up}courses.html">All courses</a>{nav_courses}
<div class="navlabel">Teaching</div><a class="nav{" on" if active == "classes" else ""}" href="{up}classes.html">My classes</a>
{THEME}</aside>"""
    top = f"""<div class="topbar"><a class="logo" href="{up}index.html">aafaq<b>cs</b></a><nav><a href="{up}index.html">About</a><a href="{up}courses.html">Courses</a><a href="{up}classes.html">Classes</a></nav>{THEME}</div>"""
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{up}assets/img/ml01.jpg">
{THEME_JS}<link rel="preconnect" href="https://fonts.googleapis.com">{FONTS}<link rel="stylesheet" href="{up}assets/site.css"></head>
<body>{top}<div class="shell">{side}<main>{body}
<footer>© {E(prof["name"])} · {E(prof.get("channel_name", ""))} · {E(prof.get("email", ""))} · Lectures checked &amp; verified</footer></main></div></body></html>"""
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def lesson_row(l, up):
    img = f'<img src="{up}{l["thumb"]}" alt="" loading="lazy">' if l.get("thumb") else '<div class="ph"></div>'
    pill = '<span class="pill live">Watch</span>' if l["status"] == "live" else '<span class="pill soon">Soon</span>'
    code = f'<span class="code">{E(l["code"])}</span>' if l.get("code") else ""
    inner = f'{img}<div><b>{code}{E(l["title"])}</b><small>{E(l.get("meta", ""))}</small></div>{pill}'
    href = l.get("youtube") or ""
    return f'<a class="lesson" href="{E(href)}">{inner}</a>' if href else f'<div class="lesson">{inner}</div>'


def track(c, up, limit=None):
    live = sum(l["status"] == "live" for l in c["lessons"])
    total = c.get("total", len(c["lessons"]))
    rows = c["lessons"][:limit] if limit else c["lessons"]
    more = f'<a class="btn s" href="{up}courses/{c["slug"]}.html">See all {total} lectures</a>' if limit and total > limit else ""
    return f"""<div class="track"><div class="t"><span>{E(c["title"])}</span><span class="meta">{live} published · {total - live} coming</span></div>
<div class="prog"><i style="width:{100 * live / total:.0f}%"></i></div><div class="lessons">{"".join(lesson_row(l, up) for l in rows)}</div>{more}</div>"""


def build():
    prof, courses, classes, pubs = D("profile"), D("courses")["courses"], D("classes")["classes"], D("publications")
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "img", DIST / "assets" / "img")
    (DIST / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    links = prof["links"]
    linkbtns = "".join(f'<a class="btn s" href="{E(u)}">{n}</a>' for n, u in (("YouTube", links.get("youtube")), ("LinkedIn", links.get("linkedin")), ("Google Scholar", links.get("scholar")), ("ORCID", links.get("orcid"))) if u)
    ml = next(c for c in courses if c["slug"] == "gate-da-ml")
    cards = "".join(f'<a class="card" href="courses/{c["slug"]}.html">{f"<img src=\"{c["lessons"][0]["thumb"]}\" alt=\"\" loading=\"lazy\">" if c["lessons"][0].get("thumb") else ""}<div><b>{E(c["title"])}</b><small>{len(c["lessons"])} lecture{"" if len(c["lessons"]) == 1 else "s"}</small></div></a>' for c in courses if c["slug"] != "gate-da-ml")
    def counts(c):
        live = sum(l["status"] == "live" for l in c["lessons"])
        return live, c.get("total", len(c["lessons"]))

    def cover(c, up=""):
        t = next((l["thumb"] for l in c["lessons"] if l.get("thumb")), None)
        return f'<img src="{up}{t}" alt="" loading="lazy">' if t else '<div class="ph"></div>'

    def ccard(c):
        live, total = counts(c)
        return f"""<a class="ccard" href="courses/{c["slug"]}.html">{cover(c)}<div class="in"><b>{E(c["title"])}</b><p>{E(c["blurb"])}</p>
<div class="prog"><i style="width:{100 * live / total:.0f}%"></i></div><span class="meta">{live} published · {total - live} coming</span></div></a>"""
    home = f"""<section><h1>Video courses</h1><p class="lede">{E(prof["tagline"])} Visual lectures for GATE and engineering students: every graph is computed from real data, and every answer is verified. Pick a course to see its lectures.</p></section>
<section class="grid">{"".join(ccard(c) for c in courses)}</section>
<section style="display:grid;gap:10px"><h2>Teaching</h2><p class="lede">Enrolled students: find your class, its Google Classroom and the lectures that go with it.</p><div class="btns"><a class="btn s" href="classes.html">My classes</a></div></section>"""
    page("courses.html", f"Courses · {prof['name']}", home, prof, courses, "home", "Visual computer-science lectures for GATE and engineering students, built on real data.")
    for c in courses:
        live, total = counts(c)
        first = next((l for l in c["lessons"] if l.get("youtube")), None)
        start = f'<a class="btn p" href="{E(first["youtube"])}">Start with {E(first.get("code") or "lecture 1")}</a>' if first else '<span class="pill soon">First lecture coming soon</span>'
        body = f"""<section class="chero"><div><div class="crumb"><a href="../courses.html">All courses</a> / {E(c["short"])}</div><h1 style="margin-top:6px">{E(c["title"])}</h1><p class="lede">{E(c["blurb"])}</p>
<div class="stats" style="margin-top:14px"><div class="stat"><b>{total}</b><small>lectures</small></div><div class="stat"><b>{live}</b><small>published</small></div><div class="stat"><b>{total - live}</b><small>coming</small></div></div>
<div class="btns">{start}<a class="btn s" href="{E(links.get("youtube", ""))}">YouTube channel</a></div></div>{cover(c, "../")}</section>
<section>{track(c, "../")}</section>"""
        page(f"courses/{c['slug']}.html", f"{c['title']} · {prof['short_name']}", body, prof, courses, c["slug"], c["blurb"])
    if classes:
        cls = "".join(f"""<div class="track"><div class="t"><span>{E(k["subject"])}</span><span class="meta">{E(k.get("programme", ""))}</span></div>
{f'<p class="meta">Class code: <b style="font-family:var(--mono)">{E(k["code"])}</b></p>' if k.get("code") and k.get("public", True) else ""}
{f'<div class="btns"><a class="btn p" href="{E(k["link"])}">Join on Google Classroom</a></div>' if k.get("link") and k.get("public", True) else '<p class="meta">Ask in class for the joining code.</p>'}</div>""" for k in classes)
    else:
        cls = '<div class="empty">Google Classroom links for each class will appear here.</div><h2>Subjects I teach</h2><div class="chips">' + "".join(f'<span class="chip">{E(x)}</span>' for x in prof.get("subjects", [])) + "</div>"
    page("classes.html", f"My classes · {prof['short_name']}", f'<section><h1>My classes</h1><p class="lede">Courses I teach at {E(prof["institution"])}, with their Google Classrooms.</p></section><section style="display:grid;gap:12px">{cls}</section>', prof, courses, "classes", "Classes taught by " + prof["name"])
    m = pubs["metrics"]
    labels = {"journal": "Journal articles", "conference": "Conference papers", "chapter": "Book chapters"}
    def pub_html(p):
        extra = []
        if p.get("impact_factor"):
            extra.append(f"Impact factor {p['impact_factor']}")
        if p.get("citations"):
            extra.append(f"cited by {p['citations']}")
        return f'<div class="pub"><b>{E(p["title"])}</b><small>{E(p["venue"])} · {p["year"]}{"".join(" · " + E(x) for x in extra)}</small></div>'
    groups = ""
    for t, lab in labels.items():
        items = [p for p in pubs["publications"] if p.get("type") == t]
        if items:
            groups += f'<h3 class="sub">{lab}</h3><div class="pubs">{"".join(pub_html(p) for p in items)}</div>'
    if pubs.get("under_review"):
        groups += '<h3 class="sub">Under review</h3><div class="pubs">' + "".join(f'<div class="pub"><b>{E(p["title"])}</b><small>{E(p["venue"])} · {p["year"]}</small></div>' for p in pubs["under_review"]) + "</div>"
    def timeline(rows):
        return '<div class="tl">' + "".join(rows) + "</div>"
    exp = timeline(f'<div class="tli"><span class="when">{E(x["when"])}</span><div><b>{E(x["role"])}</b><small>{E(x["where"])}</small><ul>{"".join(f"<li>{E(pt)}</li>" for pt in x["points"])}</ul></div></div>' for x in prof.get("experience", []))
    edu = timeline(f'<div class="tli"><span class="when">{E(x["when"])}</span><div><b>{E(x["degree"])}</b><small>{E(x["where"])} · {E(x["note"])}</small></div></div>' for x in prof.get("education", []))
    proj = timeline(f'<div class="tli"><span class="when">{E(x["when"])}</span><div><b>{E(x["title"])}</b><small>{E(x["note"])}</small></div></div>' for x in prof.get("projects", []))
    lst = lambda xs: "<ul class='plain'>" + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    bio = E(prof["bio"]) if prof["bio"] else "A short biography will appear here."
    paras = prof.get("bio_story") or [prof["bio"]]
    hl = "".join(f'<div class="hl"><b>{E(n)}</b><small>{E(t)}</small></div>' for n, t in prof.get("highlights", []))
    story = (f'<section class="story"><blockquote>{E(prof.get("headline", ""))}</blockquote>' if prof.get("headline") else '<section class="story">') + \
        "".join(f'<p{" class=lead" if i == 0 else ""}>{E(x)}</p>' for i, x in enumerate(paras)) + \
        (f'<div class="hls">{hl}</div>' if hl else "") + "</section>"
    about = f"""<section class="hero"><div><h1>{E(prof["name"])}</h1><p class="lede">{E(prof["title"])}, {E(prof["institution"])}</p><div class="btns"><a class="btn p" href="courses.html">Video courses</a>{linkbtns}</div>
<p class="meta">Email: {" · ".join(f'<a href="mailto:{E(x)}">{E(x)}</a>' for x in prof.get("emails", []))}</p></div><img src="assets/img/photo.jpg" alt=""></section>
{story}
<section style="display:grid;gap:12px"><h2>Research</h2><div class="chips">{"".join(f'<span class="chip">{E(i)}</span>' for i in pubs["interests"])}</div>
<div class="stats"><div class="stat"><b>{m["citations"]}</b><small>citations</small></div><div class="stat"><b>{m["h_index"]}</b><small>h-index</small></div><div class="stat"><b>{m["i10_index"]}</b><small>i10-index</small></div></div>{proj}</section>
<section style="display:grid;gap:12px"><h2>Publications</h2>{groups}<p class="meta">Citation counts from Google Scholar.</p></section>
<section style="display:grid;gap:12px"><h2>Experience</h2>{exp}</section>
<section style="display:grid;gap:12px"><h2>Education</h2>{edu}</section>
<section class="two"><div><h2>Achievements &amp; fellowships</h2>{lst(prof.get("achievements", []))}</div><div><h2>Roles at GCET</h2>{lst(prof.get("roles", []))}<h2 style="margin-top:18px">Certifications</h2>{lst(prof.get("certifications", []))}</div></section>"""
    page("index.html", f"{prof['name']} · Assistant Professor & Head, CSE", about, prof, courses, "about", f"{prof['name']}: research in graph learning and geometric deep learning; teaching computer science.")
    (DIST / "about.html").write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=index.html"><link rel="canonical" href="index.html"><a href="index.html">About</a>')
    print("built", sum(1 for _ in DIST.rglob("*.html")), "pages into", DIST)


if __name__ == "__main__":
    build()
