"""
aafaqcs.com — static site generator (no installs: plain Python 3).

    python3 build.py            -> writes the whole site into dist/

Content lives in data/*.json (profile, courses, classes, publications). Edit those and rebuild; never edit dist/ by hand.
Style: classic academic homepage (grey page, white sheet, portrait + boxed menu on the left, coloured name banner).
The earlier course-platform look is kept in build_platform_style.py.
Publish: drag the dist/ folder onto https://app.netlify.com/drop (free), later point aafaqcs.com at it.
"""

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
D = lambda name: json.load(open(ROOT / "data" / f"{name}.json", encoding="utf-8"))
E = html.escape

CSS = """
:root{--page:#b3b3b3;--sheet:#ffffff;--bar:#444444;--banner:#76a748;--banner-ink:#ffffff;--ink:#111111;--muted:#555555;
 --link:#2b7bd6;--head:#2b6fcf;--box:#888888;--bullet:#f07c1a;--line:#dddddd;--soft:#f6f6f6;--shadow:0 2px 14px #0000001f;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#0b0f14;--sheet:#151b23;--bar:#06090d;--banner:#5b8c33;--banner-ink:#f4fbef;--ink:#e6edf3;--muted:#9aa6b2;--link:#5aa9ff;--head:#7dbbff;--box:#3b444f;--bullet:#ff9a45;--line:#2a323c;--soft:#1d2530;--shadow:0 0 0 1px #222b36,0 20px 60px #0008;color-scheme:dark}}
:root[data-theme="dark"]{--page:#0b0f14;--sheet:#151b23;--bar:#06090d;--banner:#5b8c33;--banner-ink:#f4fbef;--ink:#e6edf3;--muted:#9aa6b2;--link:#5aa9ff;--head:#7dbbff;--box:#3b444f;--bullet:#ff9a45;--line:#2a323c;--soft:#1d2530;--shadow:0 0 0 1px #222b36,0 20px 60px #0008;color-scheme:dark}
body,.sheet,.banner,.menu,.note,.quote{transition:background-color .25s,color .25s,border-color .25s}
.sheet{box-shadow:var(--shadow)}
.bar{gap:16px}.theme{margin-right:auto;display:flex;gap:2px;background:#ffffff14;border:1px solid #ffffff26;border-radius:999px;padding:2px}
.theme button{border:0;background:none;color:#d8d8d8;font:12px Verdana,Geneva,sans-serif;padding:3px 10px;border-radius:999px;cursor:pointer}
.theme button:hover{color:#fff}.theme button[aria-pressed="true"]{background:#e8e8e8;color:#222}
h2 svg{color:var(--head)}
.photo{border-radius:2px}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--page);color:var(--ink);font:14px/1.5 Verdana,Geneva,"DejaVu Sans",sans-serif;padding:15px 0 40px}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}img{max-width:100%;display:block}
.sheet{max-width:1000px;margin:0 auto;background:var(--sheet)}
.bar{background:var(--bar);height:40px;display:flex;align-items:center;justify-content:flex-end;padding:0 68px}
.bar span{color:#e8e8e8;font:15px/1 Georgia,"Times New Roman",serif;letter-spacing:.18em;text-align:center}
.bar small{display:block;font-size:8.5px;letter-spacing:.32em;margin-top:2px}
.foot{background:var(--bar);height:10px}
.cols{display:grid;grid-template-columns:240px minmax(0,1fr);gap:0 38px;padding:20px 30px 40px 10px}
.left{display:grid;gap:30px;align-content:start}
.photo{width:201px;aspect-ratio:201/213;object-fit:cover;object-position:50% 30%}
.menu{border:1px solid var(--box);margin-left:20px;width:160px;padding:4px 0 4px 20px;font-size:12px;line-height:1.5}
.menu a{display:block;color:var(--ink)}.menu a.on{font-weight:bold}
.note{border:1px solid var(--box);margin-left:20px;width:160px;padding:4px 5px;font-size:12px;line-height:1.5}
.note a{font-weight:bold}
.follow{margin-left:17px;font-size:13px}
.banner{background:var(--banner);color:var(--banner-ink);padding:16px 20px;font:bold 36px/1.15 Arial,Helvetica,sans-serif}
.right{padding-top:0;min-width:0}
.right p{margin:12px 0;font-size:13.5px}
h2{display:flex;align-items:center;gap:8px;color:var(--head);font:bold 24px/1.2 Arial,Helvetica,sans-serif;margin:44px 0 18px}
h2 svg{flex:none}
h3{font:bold 15px Arial,Helvetica,sans-serif;margin:22px 0 8px;color:var(--ink)}
ul.news{list-style:none;padding:0 0 0 16px;margin:0}
ul.news li{position:relative;padding-left:24px;margin:0 0 14px;font-size:13px;line-height:1.3}
ul.news li::before{content:"";position:absolute;left:0;top:5px;border-left:7px solid var(--bullet);border-top:4px solid transparent;border-bottom:4px solid transparent}
ul.news li::after{content:"";position:absolute;left:-2px;top:9px;width:3px;height:1px;background:var(--bullet)}
.pub{margin:0 0 12px 16px;font-size:13px;line-height:1.35}.pub b{font-weight:normal;color:var(--link)}.pub span{display:block;color:var(--muted)}
.metrics{font-size:13px;color:var(--muted);margin:0 0 6px 16px}
.course{display:grid;grid-template-columns:150px minmax(0,1fr);gap:16px;margin:0 0 18px 16px;align-items:start}
.course img,.course .ph{width:150px;aspect-ratio:16/9;object-fit:cover;border:1px solid var(--line)}
.course .ph{background:var(--soft)}
.course b{font-size:14px}.course p{margin:3px 0 0!important;font-size:13px!important;color:var(--muted)}
.lec{display:grid;grid-template-columns:120px minmax(0,1fr) auto;gap:14px;align-items:center;margin:0 0 10px 16px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.lec img,.lec .ph{width:120px;aspect-ratio:16/9;object-fit:cover;border:1px solid var(--line)}.lec .ph{background:var(--soft)}
.lec .code{font-family:"DejaVu Sans Mono",Consolas,monospace;font-size:12px;color:var(--muted);margin-right:6px}
.lec small{display:block;color:var(--muted);font-size:12px}
.lec .go{font-size:12px;font-weight:bold;white-space:nowrap}.lec .soon{font-size:12px;color:var(--muted);white-space:nowrap}
.crumb{font-size:12px;margin:10px 0 0}
.hl{display:flex;flex-wrap:wrap;gap:8px 22px;margin:4px 0 0 16px;font-size:13px}.hl b{color:var(--banner);font:bold 20px Arial,Helvetica,sans-serif;margin-right:4px}
.quote{border-left:4px solid var(--banner);background:var(--soft);padding:10px 14px;margin:14px 0;font:italic 15px/1.45 Georgia,serif}
.tl{margin:0 0 12px 16px;font-size:13px;line-height:1.4}.tl .when{color:var(--muted);font-size:12px}
.tl ul{margin:4px 0 0;padding-left:18px;color:var(--muted)}
.plain{margin:0 0 0 16px;padding-left:18px;font-size:13px}.plain li{margin:0 0 5px}
.empty{border:1px dashed var(--box);padding:12px 14px;margin-left:16px;font-size:13px;color:var(--muted)}
.contact{margin-left:16px;font-size:13.5px;line-height:1.8}
@media (max-width:760px){
 body{padding:0}.bar{padding:0 12px;justify-content:space-between}.bar span{font-size:12px}.theme button{padding:3px 7px}
 .cols{grid-template-columns:1fr;padding:16px}
 .left{grid-template-columns:120px minmax(0,1fr);gap:14px;align-items:start}
 .photo{width:120px}.menu{margin:0;width:auto}.note,.follow{display:none}
 .banner{font-size:26px;margin-top:14px}
 .course,.lec{grid-template-columns:96px minmax(0,1fr);margin-left:0}.course img,.course .ph,.lec img,.lec .ph{width:96px}
 .lec .go,.lec .soon{grid-column:2}ul.news{padding-left:0}.pub,.tl,.plain,.metrics,.hl,.contact,.empty{margin-left:0}}
"""

ICON = ('<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true"><g stroke="currentColor" stroke-width="2.4">'
        '<line x1="19" y1="17" x2="19" y2="5"/><line x1="19" y1="17" x2="6" y2="20"/><line x1="19" y1="17" x2="29" y2="28"/></g>'
        '<g fill="currentColor"><circle cx="19" cy="17" r="5.5"/><circle cx="19" cy="4.5" r="3"/><circle cx="5" cy="20.5" r="3"/><circle cx="29.5" cy="28.5" r="3.6"/></g></svg>')

MENU = [("index.html", "Home"), ("publications.html", "Publications"), ("courses.html", "Video courses"),
        ("classes.html", "Teaching"), ("bio.html", "Bio"), ("contact.html", "Contact")]


THEME = ('<div class="theme" role="group" aria-label="Colour theme"><button data-t="light" title="Light theme">☀ Light</button>'
         '<button data-t="dark" title="Dark theme">☾ Dark</button><button data-t="auto" title="Follow my device">Auto</button></div>')
THEME_JS = """<script>(function(){var r=document.documentElement,t="auto";try{t=localStorage.getItem("theme")||"auto"}catch(e){}
function set(v){t=v;if(v==="auto")r.removeAttribute("data-theme");else r.setAttribute("data-theme",v);try{localStorage.setItem("theme",v)}catch(e){}
document.querySelectorAll(".theme button").forEach(function(b){b.setAttribute("aria-pressed",b.dataset.t===v)})}
set(t);document.addEventListener("DOMContentLoaded",function(){set(t);document.querySelectorAll(".theme button").forEach(function(b){b.onclick=function(){set(b.dataset.t)}})})})()</script>"""


def rich(text, up=""):
    """Escape text, then turn [label](url) into links; site-relative urls get the right ../ prefix."""
    def link(m):
        url = m.group(2)
        if not re.match(r"https?://|mailto:", url):
            url = up + url
        return f'<a href="{url}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, E(text))


def h2(title):
    return f"<h2>{ICON}{E(title)}</h2>"


def page(path, title, body, prof, active, desc):
    up = "../" * path.count("/")
    links = prof["links"]
    menu = "".join(f'<a class="{"on" if active == href else ""}" href="{up}{href}">{lab}</a>' for href, lab in MENU)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{up}assets/img/photo.jpg">
{THEME_JS}<link rel="stylesheet" href="{up}assets/site.css"></head>
<body><div class="sheet"><div class="bar">{THEME}<span>GCET KASHMIR<small>DEPARTMENT OF CSE</small></span></div>
<div class="cols"><div class="left"><img class="photo" src="{up}assets/img/photo.jpg" alt="{E(prof["name"])}">
<nav class="menu">{menu}</nav>
<div class="note">Preparing for GATE DA 2027? The full <a href="{up}courses/gate-da-ml.html">Machine Learning series</a> is free on YouTube, built on real data.</div>
<a class="follow" href="{E(links.get("youtube", ""))}">Subscribe on YouTube</a></div>
<div class="right">{body}</div></div><div class="foot"></div></div></body></html>"""
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def redirect(path, to):
    (DIST / path).write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}"><a href="{to}">{to}</a>')


def build():
    prof, courses, classes, pubs = D("profile"), D("courses")["courses"], D("classes")["classes"], D("publications")
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "img", DIST / "assets" / "img")
    (DIST / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    links, m = prof["links"], pubs["metrics"]
    name = prof["name"]
    banner = f'<div class="banner">{E(name)}.</div>'

    def counts(c):
        live = sum(l["status"] == "live" for l in c["lessons"])
        return live, c.get("total", len(c["lessons"]))

    def cover(c, up=""):
        t = next((l["thumb"] for l in c["lessons"] if l.get("thumb")), None)
        return f'<img src="{up}{t}" alt="" loading="lazy">' if t else '<div class="ph"></div>'

    def pub_html(p):
        extra = [str(p["year"])]
        if p.get("impact_factor"):
            extra.append(f"impact factor {p['impact_factor']}")
        if p.get("citations"):
            extra.append(f"cited by {p['citations']}")
        return f'<div class="pub"><b>{E(p["title"])}</b><span>{E(p["venue"])} · {" · ".join(E(x) for x in extra)}</span></div>'

    # Home
    research = ", ".join(pubs["interests"]).lower()
    home = f"""{banner}
<p>I am Assistant Professor and Head of the Department of Computer Science &amp; Engineering at <a href="https://gcetkashmir.ac.in">GCET Kashmir</a>.</p>
<p>My research is in machine learning on graphs: {E(research)}. My PhD at <a href="https://nitsri.ac.in">NIT Srinagar</a> studied why deep graph neural networks lose information as they grow (over-smoothing and over-squashing) and how to build networks that don't. I also make free visual lectures for GATE and engineering students, where every graph is computed from real data and every answer is checked.</p>
{h2("What's new")}<ul class="news">{"".join(f"<li>{rich(n)}</li>" for n in prof.get("news", []))}</ul>
{h2("Video courses")}{"".join(f'<div class="course"><a href="courses/{c["slug"]}.html">{cover(c)}</a><div><a href="courses/{c["slug"]}.html"><b>{E(c["title"])}</b></a><p>{E(c["blurb"])} {counts(c)[0]} of {counts(c)[1]} lectures published.</p></div></div>' for c in courses[:3])}
<p style="margin-left:16px"><a href="courses.html">All video courses »</a></p>
{h2("Latest publications")}{"".join(pub_html(p) for p in sorted(pubs["publications"], key=lambda p: -p["year"])[:4])}
<p style="margin-left:16px"><a href="publications.html">All publications »</a></p>"""
    page("index.html", f"{name} · GCET Kashmir", home, prof, "index.html", f"{name}: Assistant Professor and Head, CSE, GCET Kashmir. Graph learning research and free visual lectures for GATE.")

    # Publications
    labels = {"journal": "Journal articles", "conference": "Conference papers", "chapter": "Book chapters"}
    groups = ""
    for t, lab in labels.items():
        items = sorted((p for p in pubs["publications"] if p.get("type") == t), key=lambda p: -p["year"])
        if items:
            groups += f"<h3>{lab}</h3>" + "".join(pub_html(p) for p in items)
    if pubs.get("under_review"):
        groups += "<h3>Under review</h3>" + "".join(f'<div class="pub"><b>{E(p["title"])}</b><span>{E(p["venue"])} · {p["year"]}</span></div>' for p in pubs["under_review"])
    proj = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["title"])}</b><br><span class="when">{E(x["note"])}</span></div>' for x in prof.get("projects", []))
    pubs_body = f"""{banner}{h2("Publications")}
<p class="metrics">{m["citations"]} citations · h-index {m["h_index"]} · i10-index {m["i10_index"]} (<a href="{E(links.get("scholar", ""))}">Google Scholar</a>)</p>{groups}
{h2("Research projects")}{proj}"""
    page("publications.html", f"Publications · {name}", pubs_body, prof, "publications.html", f"Publications of {name} on graph neural networks and geometric deep learning.")

    # Courses
    cat = "".join(f'<div class="course"><a href="courses/{c["slug"]}.html">{cover(c)}</a><div><a href="courses/{c["slug"]}.html"><b>{E(c["title"])}</b></a><p>{E(c["blurb"])}</p><p>{counts(c)[0]} of {counts(c)[1]} lectures published.</p></div></div>' for c in courses)
    page("courses.html", f"Video courses · {name}", f"""{banner}{h2("Video courses")}
<p>Free visual lectures for GATE and engineering students, on my <a href="{E(links.get("youtube", ""))}">YouTube channel</a>. Every graph is computed from real data, and every answer is verified.</p>{cat}""",
         prof, "courses.html", "Free visual computer-science lectures for GATE and engineering students, built on real data.")
    for c in courses:
        live, total = counts(c)
        rows = ""
        for l in c["lessons"]:
            img = f'<img src="../{l["thumb"]}" alt="" loading="lazy">' if l.get("thumb") else '<div class="ph"></div>'
            code = f'<span class="code">{E(l["code"])}</span>' if l.get("code") else ""
            title = f'<a href="{E(l["youtube"])}">{E(l["title"])}</a>' if l.get("youtube") else E(l["title"])
            act = f'<a class="go" href="{E(l["youtube"])}">Watch ▸</a>' if l.get("youtube") else '<span class="soon">Coming soon</span>'
            rows += f'<div class="lec">{img}<div>{code}{title}<small>{E(l.get("meta", ""))}</small></div>{act}</div>'
        body = f"""{banner}<p class="crumb"><a href="../courses.html">Video courses</a> » {E(c["short"])}</p>{h2(c["title"])}
<p>{E(c["blurb"])} <b>{live} of {total}</b> lectures published.</p>{rows}"""
        page(f"courses/{c['slug']}.html", f"{c['title']} · {prof['short_name']}", body, prof, "courses.html", c["blurb"])

    # Teaching
    if classes:
        cls = "".join(f"""<div class="tl"><b>{E(k["subject"])}</b> <span class="when">{E(k.get("programme", ""))}</span><br>
{f'Class code: <b>{E(k["code"])}</b> · ' if k.get("code") and k.get("public", True) else ""}{f'<a href="{E(k["link"])}">Join on Google Classroom</a>' if k.get("link") and k.get("public", True) else "Ask in class for the joining code."}</div>""" for k in classes)
    else:
        cls = '<div class="empty">Google Classroom links for each class will appear here.</div>'
    subj = '<ul class="plain">' + "".join(f"<li>{E(x)}</li>" for x in prof.get("subjects", [])) + "</ul>"
    page("classes.html", f"Teaching · {name}", f"""{banner}{h2("My classes")}<p>Courses I teach at {E(prof["institution"])}, with their Google Classrooms.</p>{cls}
{h2("Subjects I teach")}{subj}{h2("Video lectures")}<p>Lectures that go with these classes are on the <a href="courses.html">video courses</a> page.</p>""",
         prof, "classes.html", "Classes taught by " + name)

    # Bio
    story = "".join(f"<p>{E(x)}</p>" for x in (prof.get("bio_story") or [prof["bio"]]))
    hl = "".join(f"<span><b>{E(n)}</b>{E(t)}</span>" for n, t in prof.get("highlights", []))
    exp = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["role"])}</b>, {E(x["where"])}<ul>{"".join(f"<li>{E(pt)}</li>" for pt in x["points"])}</ul></div>' for x in prof.get("experience", []))
    edu = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["degree"])}</b>, {E(x["where"])}<br><span class="when">{E(x["note"])}</span></div>' for x in prof.get("education", []))
    lst = lambda xs: '<ul class="plain">' + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    bio_body = f"""{banner}{h2("Bio")}{f'<div class="quote">{E(prof["headline"])}</div>' if prof.get("headline") else ""}{story}
<div class="hl">{hl}</div>{h2("Experience")}{exp}{h2("Education")}{edu}
{h2("Achievements & fellowships")}{lst(prof.get("achievements", []))}
{h2("Roles at GCET")}{lst(prof.get("roles", []))}<h3>Certifications</h3>{lst(prof.get("certifications", []))}"""
    page("bio.html", f"Bio · {name}", bio_body, prof, "bio.html", f"Biography of {name}.")

    # Contact
    em = "<br>".join(f'<a href="mailto:{E(x)}">{E(x)}</a>' for x in prof.get("emails", []))
    ext = " · ".join(f'<a href="{E(u)}">{n}</a>' for n, u in (("YouTube", links.get("youtube")), ("LinkedIn", links.get("linkedin")), ("Google Scholar", links.get("scholar")), ("ORCID", links.get("orcid"))) if u)
    page("contact.html", f"Contact · {name}", f"""{banner}{h2("Contact")}
<div class="contact"><b>Email</b><br>{em}<br><br><b>Office</b><br>{E(prof.get("address", prof["institution"]))}<br><br><b>Elsewhere</b><br>{ext}</div>""",
         prof, "contact.html", f"How to contact {name}.")

    redirect("about.html", "index.html")
    print("built", sum(1 for _ in DIST.rglob("*.html")), "pages into", DIST)


if __name__ == "__main__":
    build()
