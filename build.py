"""
aafaqcs.com — static site generator (no installs: plain Python 3).

    python3 build.py            -> writes the whole site into dist/

Content lives in data/*.json (profile, courses, classes, publications). Edit those and rebuild; never edit dist/ by hand.
Style: classic academic homepage (grey page, white sheet, portrait + boxed menu on the left, coloured name banner).
The earlier course-platform look is kept in build_platform_style.py.
Publish: drag the dist/ folder onto https://app.netlify.com/drop (free). When aafaqcs.com is connected, change SITE below and rebuild.
"""

import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE = "https://aafaqcs.github.io"      # live address (GitHub Pages); switch to "https://aafaqcs.com" once the domain is connected
D = lambda name: json.load(open(ROOT / "data" / f"{name}.json", encoding="utf-8"))
E = html.escape

CSS = """
:root{--page:#e9ecef;--sheet:#ffffff;--bar:#2f3439;--bar-ink:#eef1f3;--banner:#6aa142;--banner2:#3f8a5a;--banner-ink:#ffffff;--ink:#16191d;--muted:#5b6670;
 --link:#1f6fd1;--head:#1f63c4;--box:#d5dbe1;--bullet:#ef7a12;--line:#e3e7eb;--soft:#f4f6f8;--card:#ffffff;--glow:#1f6fd11a;
 --shadow:0 1px 2px #0000000d,0 12px 40px #0000001a;--r:14px;color-scheme:light;
 --sans:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,Verdana,sans-serif;--display:"Inter Tight","Inter",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,Consolas,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#0a0e13;--sheet:#121820;--bar:#070a0e;--bar-ink:#e8edf2;--banner:#5e9a37;--banner2:#2f7a52;--banner-ink:#f3faef;--ink:#e6edf3;--muted:#98a4b0;--link:#62adff;--head:#86c1ff;--box:#2c3540;--bullet:#ff9a45;--line:#232c37;--soft:#1a222c;--card:#151c25;--glow:#62adff22;--shadow:0 0 0 1px #1f2832,0 24px 70px #000a;color-scheme:dark}}
:root[data-theme="dark"]{--page:#0a0e13;--sheet:#121820;--bar:#070a0e;--bar-ink:#e8edf2;--banner:#5e9a37;--banner2:#2f7a52;--banner-ink:#f3faef;--ink:#e6edf3;--muted:#98a4b0;--link:#62adff;--head:#86c1ff;--box:#2c3540;--bullet:#ff9a45;--line:#232c37;--soft:#1a222c;--card:#151c25;--glow:#62adff22;--shadow:0 0 0 1px #1f2832,0 24px 70px #000a;color-scheme:dark}
*{box-sizing:border-box}html,body{margin:0}html{scroll-behavior:smooth}
body{background:var(--page);background-image:radial-gradient(1200px 500px at 50% -200px,var(--glow),transparent);background-attachment:fixed;color:var(--ink);font:15px/1.6 var(--sans);padding:22px 16px 48px;-webkit-font-smoothing:antialiased}
body,.sheet,.banner,.menu,.note,.quote,.card,.lec,.stat{transition:background-color .25s,color .25s,border-color .25s}
a{color:var(--link);text-decoration:none;text-underline-offset:3px}a:hover{text-decoration:underline}img{max-width:100%;display:block}
.sheet{max-width:1060px;margin:0 auto;background:var(--sheet);border-radius:var(--r);box-shadow:var(--shadow);overflow:clip}
.bar{background:var(--bar);color:var(--bar-ink);display:flex;align-items:center;gap:16px;padding:10px 28px}
.brand{font:800 17px var(--display);letter-spacing:-.01em;color:var(--bar-ink)}.brand b{color:#8fd16a}.brand:hover{text-decoration:none}
.inst{margin-left:auto;font:15px/1 Georgia,"Times New Roman",serif;letter-spacing:.18em;text-align:right}
.inst small{display:block;font-size:8.5px;letter-spacing:.32em;margin-top:3px;opacity:.75}
.theme{display:flex;gap:2px;background:#ffffff12;border:1px solid #ffffff24;border-radius:999px;padding:2px}
.theme button{border:0;background:none;color:#cfd5da;font:500 12px var(--sans);padding:4px 11px;border-radius:999px;cursor:pointer}
.theme button:hover{color:#fff}.theme button[aria-pressed="true"]{background:#eef1f3;color:#1d2125}
.cols{display:grid;grid-template-columns:230px minmax(0,1fr);gap:0 40px;padding:28px 36px 44px 28px}
.left{display:grid;gap:22px;align-content:start;position:sticky;top:18px;align-self:start}
.photo{width:84%;justify-self:center;margin:0 auto;display:block;aspect-ratio:1;object-fit:cover;object-position:50% 22%;border-radius:50%;border:4px solid var(--sheet);box-shadow:0 0 0 3px var(--banner),0 10px 28px #0000002e}
.menu{border:1px solid var(--box);border-radius:12px;padding:6px;display:grid;gap:1px;font-size:13.5px}
.menu a{color:var(--ink);padding:6px 12px;border-radius:8px;position:relative}.menu a:hover{background:var(--soft);text-decoration:none}
.menu a.on{font-weight:700;background:var(--soft)}.menu a.on::before{content:"";position:absolute;left:0;top:7px;bottom:7px;width:3px;border-radius:3px;background:var(--banner)}
.note{border:1px solid var(--box);border-radius:12px;padding:12px 14px;font-size:12.5px;line-height:1.55;background:linear-gradient(160deg,var(--soft),transparent)}
.note a{font-weight:700}
.follow{display:inline-flex;align-items:center;gap:8px;font-size:13px;font-weight:600;padding:8px 14px;border-radius:999px;background:#e62117;color:#fff;justify-self:start}
.follow:hover{text-decoration:none;filter:brightness(1.08)}
.banner{position:relative;overflow:hidden;background:linear-gradient(120deg,var(--banner),var(--banner2));color:var(--banner-ink);padding:22px 26px;border-radius:12px}
.banner h1{margin:0;font:800 clamp(28px,4vw,40px)/1.1 var(--display);letter-spacing:-.02em;position:relative}
.banner p{margin:6px 0 0!important;font-size:14px!important;opacity:.92;position:relative}
.banner svg{position:absolute;right:-10px;top:-14px;height:150%;opacity:.22}
.right{min-width:0}.right>p{margin:14px 0;font-size:15px}
h2{display:flex;align-items:center;gap:10px;color:var(--head);font:800 23px/1.2 var(--display);letter-spacing:-.01em;margin:44px 0 16px}
h2 svg{flex:none;color:var(--head);width:30px;height:30px}
h3{font:700 15px var(--display);margin:22px 0 8px;color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:20px 0 0}
.stat{border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--card)}
.stat b{display:block;font:800 26px/1.1 var(--display);color:var(--banner);letter-spacing:-.02em}.stat small{color:var(--muted);font-size:12px;line-height:1.35;display:block;margin-top:3px}
ul.news{list-style:none;padding:0;margin:0;border-left:2px solid var(--line);margin-left:8px}
ul.news li{position:relative;padding:0 0 16px 22px;font-size:14px;line-height:1.5}
ul.news .when{display:block;font:600 11.5px var(--mono);color:var(--muted);letter-spacing:.03em;margin:0 0 3px}
.tag.short{background:#7c3aed1f;color:#7c3aed}
ul.news li::before{content:"";position:absolute;left:-7px;top:6px;width:12px;height:12px;border-radius:50%;background:var(--sheet);border:2px solid var(--bullet)}
.tag{display:inline-block;font:700 10.5px var(--sans);letter-spacing:.08em;text-transform:uppercase;padding:2px 8px;border-radius:999px;margin-right:8px;vertical-align:1px}
.tag.video{background:#e621171a;color:#d0311f}.tag.paper{background:#1f6fd11a;color:var(--link)}.tag.milestone{background:#6aa1421f;color:#4f8a2c}
.pub{margin:0 0 14px;padding:10px 14px;border:1px solid var(--line);border-radius:10px;font-size:14px;line-height:1.45;background:var(--card)}
.pub b{font-weight:600;color:var(--ink)}.pub span{display:block;color:var(--muted);font-size:13px;margin-top:2px}
.badge{display:inline-block;font:700 11px var(--sans);padding:1px 8px;border-radius:999px;margin:6px 6px 0 0;background:var(--soft);color:var(--muted);border:1px solid var(--line)}
.badge.if{background:#ef7a121a;color:#c25f06;border-color:transparent}
.metrics{font-size:14px;color:var(--muted);margin:0 0 10px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}
.card{border:1px solid var(--line);border-radius:12px;overflow:hidden;display:grid;grid-template-rows:auto 1fr;background:var(--card);color:var(--ink);transition:transform .18s,box-shadow .18s,border-color .18s}
.card:hover{transform:translateY(-3px);box-shadow:0 12px 28px #0000001f;border-color:var(--link);text-decoration:none}
.card img,.card .ph{aspect-ratio:16/9;object-fit:cover;width:100%}.ph{background:repeating-linear-gradient(45deg,var(--soft),var(--soft) 10px,var(--sheet) 10px,var(--sheet) 20px)}
.card>div{padding:12px 14px 14px;display:grid;gap:6px;align-content:start}.card b{font:700 15px/1.3 var(--display);color:var(--head)}.card p{margin:0;font-size:13px;color:var(--muted)}
.prog{height:6px;background:var(--soft);border-radius:99px;overflow:hidden;border:1px solid var(--line)}.prog i{display:block;height:100%;background:linear-gradient(90deg,var(--banner),var(--banner2))}
.meta{font-size:12px;color:var(--muted)}
.lec{display:grid;grid-template-columns:132px minmax(0,1fr) auto;gap:16px;align-items:center;margin:0 0 10px;padding:8px;border:1px solid var(--line);border-radius:12px;background:var(--card);color:var(--ink);transition:border-color .18s,background-color .18s}
a.lec:hover{border-color:var(--link);background:var(--soft);text-decoration:none}
.lec img,.lec .ph{width:132px;aspect-ratio:16/9;object-fit:cover;border-radius:8px}
.lec .code{font:700 11.5px var(--mono);color:var(--banner);margin-right:8px}
.lec b{font-weight:600;font-size:14.5px}.lec small{display:block;color:var(--muted);font-size:12.5px;margin-top:2px}
.go{font-size:12.5px;font-weight:700;white-space:nowrap;padding:6px 12px;border-radius:999px;background:var(--link);color:#fff}
.soon{font-size:12px;color:var(--muted);white-space:nowrap;padding:5px 11px;border-radius:999px;border:1px dashed var(--box)}
.crumb{font-size:13px;margin:14px 0 0;color:var(--muted)}
.quote{border-left:4px solid var(--banner);background:var(--soft);padding:14px 18px;margin:16px 0;border-radius:0 12px 12px 0;font:italic 17px/1.5 Georgia,serif}
.tl{margin:0 0 14px;padding-left:16px;border-left:2px solid var(--line);font-size:14px;line-height:1.5}.tl .when{color:var(--muted);font:600 12px var(--mono)}
.tl ul{margin:4px 0 0;padding-left:18px;color:var(--muted)}
.plain{margin:0;padding-left:20px;font-size:14px}.plain li{margin:0 0 6px}
.empty{border:1px dashed var(--box);border-radius:12px;padding:14px 16px;font-size:14px;color:var(--muted)}
.ytm{position:fixed;inset:0;z-index:50;display:none;place-items:center;background:#05080ce6;padding:16px}.ytm.on{display:grid}
.ytm iframe{width:min(94vw,1000px);aspect-ratio:16/9;border:0;border-radius:12px;background:#000;box-shadow:0 30px 90px #000}
.ytm.v iframe{width:auto;height:min(86vh,820px);max-width:94vw;aspect-ratio:9/16}
.ytm .x{position:absolute;top:14px;right:16px;font:700 15px var(--sans);color:#fff;background:#ffffff22;border:1px solid #ffffff44;border-radius:999px;padding:8px 16px;cursor:pointer}
.ytm .yt{position:absolute;bottom:14px;font-size:13px;color:#cfd8e3}
.subj{border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:0 0 14px;background:var(--card)}
.subj h3{margin:0 0 4px}.subj p{margin:6px 0 10px}.subj .row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
.pill{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;white-space:nowrap;padding:6px 12px;border-radius:999px;background:var(--link);color:#fff}
a.pill:hover{text-decoration:none;filter:brightness(1.08)}
.pill.gcr{background:#1e8e3e}.pill.ghost{background:transparent;color:var(--link);border:1.5px solid var(--link)}
.pill.prac{background:#c2410c}.pill.off{background:transparent;color:var(--muted);border:1px dashed var(--box);font-weight:500}
.gcrbox{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;border:1px solid var(--line);border-left:5px solid #1e8e3e;border-radius:12px;padding:12px 16px;margin:0 0 18px;background:var(--soft);font-size:14px}
.week{display:grid;grid-template-columns:74px minmax(0,1fr) auto;gap:14px;align-items:center;padding:10px 12px;border:1px solid var(--line);border-radius:12px;margin:0 0 8px;background:var(--card)}
.week .wk{font:700 12px var(--mono);color:var(--banner);text-transform:uppercase;letter-spacing:.04em}
.week .t{font-size:14.5px}.week .files{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
@media (max-width:640px){.week{grid-template-columns:1fr}.week .files{justify-content:flex-start}}
.contact{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.contact div{border:1px solid var(--line);border-radius:12px;padding:14px 16px;font-size:14px;background:var(--card)}.contact b{display:block;font:700 12px var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.more{margin:4px 0 0;font-weight:600;font-size:14px}
footer{border-top:1px solid var(--line);padding:18px 36px;display:flex;flex-wrap:wrap;gap:8px 18px;font-size:12.5px;color:var(--muted);align-items:center}
footer .sp{margin-left:auto}

/* ===== Midnight Graph theme (navy + teal + amber, matches the YouTube thumbnails) ===== */
:root{--page:#e8eef6;--sheet:#ffffff;--bar:#0b1b2e;--bar-ink:#e8f1fb;--banner:#0f2a4a;--banner2:#0e8a7e;--banner-ink:#ffffff;--ink:#0f1c2b;--muted:#566578;
 --link:#0a7ea4;--head:#0b5d86;--box:#d2dbe6;--bullet:#f2a516;--line:#e1e8f0;--soft:#f2f6fb;--card:#ffffff;--glow:#0e8a7e1f;--amber:#f2a516;--teal:#0e8a7e;
 --shadow:0 1px 2px #0000000d,0 16px 44px #0b1b2e1f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#060a13;--sheet:#0c1424;--bar:#050912;--bar-ink:#e6eef8;--banner:#12305a;--banner2:#0e7c74;--banner-ink:#f2f8ff;
 --ink:#e6edf7;--muted:#93a3b8;--link:#4cc9f0;--head:#5ad1e6;--box:#24324a;--bullet:#ffb020;--line:#1c2840;--soft:#121d33;--card:#101a2e;--glow:#4cc9f022;--amber:#ffb020;--teal:#2ec4b6;
 --shadow:0 0 0 1px #1a2640,0 24px 70px #000b}}
:root[data-theme="dark"]{--page:#060a13;--sheet:#0c1424;--bar:#050912;--bar-ink:#e6eef8;--banner:#12305a;--banner2:#0e7c74;--banner-ink:#f2f8ff;
 --ink:#e6edf7;--muted:#93a3b8;--link:#4cc9f0;--head:#5ad1e6;--box:#24324a;--bullet:#ffb020;--line:#1c2840;--soft:#121d33;--card:#101a2e;--glow:#4cc9f022;--amber:#ffb020;--teal:#2ec4b6;
 --shadow:0 0 0 1px #1a2640,0 24px 70px #000b}
.brand b{color:var(--amber)!important}
.menu a.on::before{background:var(--amber)!important}
h2 svg{color:var(--teal)!important}
.follow{background:linear-gradient(90deg,#e62117,#ff4b3a)!important}

/* ----- playlist placards (video courses) ----- */
.pls{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:26px 22px;margin-top:8px}
.pl{display:block;color:var(--ink);text-decoration:none!important;position:relative;padding-top:14px}
.pl .stack{position:relative;aspect-ratio:16/9}
.pl .stack::before,.pl .stack::after{content:"";position:absolute;left:6%;right:6%;top:-7px;height:20px;border-radius:12px 12px 0 0;background:var(--box);opacity:.75}
.pl .stack::after{left:12%;right:12%;top:-13px;opacity:.45}
.pl .cov{position:absolute;inset:0;border-radius:14px;overflow:hidden;background:var(--soft);box-shadow:0 8px 22px #0b1b2e33;z-index:1;transition:transform .2s}
.pl .cov img{width:100%;height:100%;object-fit:cover}
.pl .side{position:absolute;right:0;top:0;bottom:0;width:34%;background:linear-gradient(90deg,#0b1b2ecc,#0b1b2ef2);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;font-weight:800}
.pl .side b{font:800 30px var(--display);line-height:1}.pl .side span{font-size:12px;letter-spacing:.08em;text-transform:uppercase;opacity:.85}
.pl .side i{font-style:normal;font-size:26px;line-height:1}
.pl .play{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:#0b1b2e99;color:#fff;font-weight:800;letter-spacing:.08em;opacity:0;transition:opacity .2s;z-index:2}
.pl:hover .cov{transform:translateY(-4px)}.pl:hover .play{opacity:1}
.pl .tx{padding:12px 4px 0;display:grid;gap:6px}
.pl .tx b{font:800 17px/1.3 var(--display)}.pl .tx p{margin:0;font-size:13.5px;color:var(--muted);line-height:1.45}
.pl .chip{justify-self:start;font:700 11px var(--sans);letter-spacing:.08em;text-transform:uppercase;padding:3px 9px;border-radius:999px;background:var(--soft);color:var(--head);border:1px solid var(--line)}
.plhead{display:grid;grid-template-columns:minmax(0,340px) minmax(0,1fr);gap:22px;align-items:center;margin:8px 0 22px;padding:18px;border-radius:16px;background:linear-gradient(120deg,var(--banner),var(--banner2));color:#fff}
.plhead img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:12px;box-shadow:0 10px 30px #0006}
.plhead h2{color:#fff!important;margin:0 0 6px!important}.plhead h2 svg{color:#fff!important}.plhead p{color:#e2ecf8!important;margin:6px 0!important}
.plhead .meta{color:#cfe0f2}.plhead .btnp{display:inline-block;margin-top:8px;padding:9px 18px;border-radius:999px;background:var(--amber);color:#0b1b2e;font-weight:800;text-decoration:none}
.plnum{font:800 13px var(--mono);color:var(--muted);width:26px;text-align:center}

/* ----- teaching placards ----- */
.tcs{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}
.tc{display:grid;grid-template-rows:auto 1fr;border-radius:16px;overflow:hidden;border:1px solid var(--line);background:var(--card);color:var(--ink);text-decoration:none!important;transition:transform .18s,box-shadow .18s}
.tc:hover{transform:translateY(-4px);box-shadow:0 16px 34px #0b1b2e2e}
.tc .top{position:relative;padding:22px 20px 18px;background:linear-gradient(130deg,var(--c1),var(--c2));color:#fff;min-height:130px}
.tc .top .code{font:800 44px/1 var(--display);letter-spacing:-.02em;opacity:.95}
.tc .top .nm{font:700 16px/1.3 var(--display);margin-top:8px}
.tc .top .sem{position:absolute;right:14px;top:14px;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;background:#ffffff26;padding:3px 9px;border-radius:999px}
.tc .bot{padding:14px 18px 18px;display:grid;gap:10px;align-content:start}
.tc .bot p{margin:0;font-size:13.5px;color:var(--muted);line-height:1.45}
.tc .res{display:flex;flex-wrap:wrap;gap:6px}
.tc .res span{font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;background:var(--soft);border:1px solid var(--line)}
.tc .res span b{color:var(--head)}

/* ----- subject page tabs ----- */
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 16px;border-bottom:1px solid var(--line);padding-bottom:10px}
.tabs button{border:1px solid var(--line);background:var(--card);color:var(--ink);font:700 14px var(--sans);padding:9px 16px;border-radius:999px;cursor:pointer}
.tabs button[aria-selected="true"]{background:var(--head);border-color:var(--head);color:#fff}
.tabs button .n{font:700 11px var(--mono);margin-left:6px;opacity:.75}
.tabpane{display:none}.tabpane.on{display:block}
.res-row{display:grid;grid-template-columns:86px minmax(0,1fr) auto;gap:14px;align-items:center;padding:12px 14px;border:1px solid var(--line);border-radius:12px;margin:0 0 9px;background:var(--card)}
.res-row .wk{font:700 12px var(--mono);color:var(--head)}.res-row .t{font-weight:600;font-size:14.5px}
.res-row .f{display:flex;flex-wrap:wrap;gap:6px;justify-content:flex-end}
.fbtn{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:800;padding:6px 12px;border-radius:999px;text-decoration:none!important;color:#fff;background:var(--teal)}
.fbtn.notes{background:#7c4dff}.fbtn.prac{background:#e8590c}.fbtn.off{background:var(--soft);color:var(--muted);border:1px dashed var(--box);font-weight:600}
.plhead .gcrbox{background:#ffffff1f!important;border:1px solid #ffffff40!important;color:#fff!important}.plhead .gcrbox .meta,.plhead .gcrbox span{color:#e8f1fb!important}.plhead .gcrbox b{color:#fff}
.empty-pane{padding:22px;border:1px dashed var(--box);border-radius:14px;color:var(--muted);text-align:center}
@media (max-width:780px){.plhead{grid-template-columns:1fr}.res-row{grid-template-columns:1fr}.res-row .f{justify-content:flex-start}}

/* ----- GCET Kashmir campus photo: blurred page backdrop + sharp banner ----- */
html{background:var(--page)}
body{background:transparent!important;position:relative}
body::before{content:"";position:fixed;inset:-30px;background:url(img/campus.jpg) center 58%/cover no-repeat;filter:blur(5px) saturate(1.15);z-index:-2}
body::after{content:"";position:fixed;inset:0;background:linear-gradient(180deg,#0b1b2eb8 0%,#0b1b2e66 45%,#0e8a7e59 75%,#0b1b2ed9 100%);z-index:-1}
.banner{background:linear-gradient(105deg,#0b1b2ef5 0%,#0f2a4ad9 42%,#0e8a7e8c 75%,#0e8a7e33 100%),url(img/campus.jpg) center 64%/cover no-repeat!important;min-height:150px}
.banner svg{opacity:.18!important}
.banner p{text-shadow:0 1px 6px #0009}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) body::after{background:linear-gradient(180deg,#050912e6 0%,#050912b3 50%,#05091ef0 100%)}}
:root[data-theme="dark"] body::after{background:linear-gradient(180deg,#050912e6 0%,#050912b3 50%,#05091ef0 100%)}
footer .photo-credit{font-size:12px;opacity:.8}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto}}
@media (max-width:780px){
 body{padding:0}.sheet{border-radius:0}.bar{padding:10px 14px;gap:10px;flex-wrap:wrap}.inst{display:none}.theme{margin-left:auto}.theme button{padding:4px 8px}
 .cols{grid-template-columns:1fr;padding:16px}
 .left{position:static;grid-template-columns:110px minmax(0,1fr);gap:14px;align-items:start}
 .photo{width:104px}.note,.follow{display:none}
 .banner{margin-top:14px;padding:18px}.banner svg{opacity:.12}
 .lec{grid-template-columns:96px minmax(0,1fr)}.lec img,.lec .ph{width:96px}.lec .go,.lec .soon{grid-column:2;justify-self:start}
 footer{padding:16px}footer .sp{margin-left:0}}
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


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@700;800&family=JetBrains+Mono:wght@600;700&display=swap">')
FAVICON = ("data:image/svg+xml," + "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 34 34'%3E%3Crect width='34' height='34' rx='8' fill='%230e8a7e'/%3E"
           "%3Cg stroke='white' stroke-width='2.4'%3E%3Cline x1='18' y1='17' x2='18' y2='7'/%3E%3Cline x1='18' y1='17' x2='8' y2='20'/%3E%3Cline x1='18' y1='17' x2='26' y2='26'/%3E%3C/g%3E"
           "%3Cg fill='white'%3E%3Ccircle cx='18' cy='17' r='4.5'/%3E%3Ccircle cx='18' cy='7' r='2.6'/%3E%3Ccircle cx='8' cy='20' r='2.6'/%3E%3Ccircle cx='26' cy='26' r='3'/%3E%3C/g%3E%3C/svg%3E")
# A small graph drawn faintly across the right of the name banner (his research is graph learning).
NET = ('<svg viewBox="0 0 300 120" aria-hidden="true"><g stroke="#fff" stroke-width="1.6" fill="none">'
       '<path d="M40 90 L95 40 L160 70 L215 25 L270 60 M95 40 L120 105 L160 70 L200 110 L270 60 M215 25 L200 110 M40 90 L120 105"/></g>'
       '<g fill="#fff"><circle cx="40" cy="90" r="5"/><circle cx="95" cy="40" r="7"/><circle cx="160" cy="70" r="9"/><circle cx="215" cy="25" r="6"/>'
       '<circle cx="270" cy="60" r="7"/><circle cx="120" cy="105" r="5"/><circle cx="200" cy="110" r="6"/></g></svg>')


PAGES = []
import hashlib
CSS_V = None


PLAYER = """<div class="ytm" id="ytm" role="dialog" aria-label="Video player"><button class="x" type="button">✕ Close</button><a class="yt" id="ytl" href="#">Open on YouTube ↗</a></div>
<script>(function(){var m=document.getElementById("ytm"),l=document.getElementById("ytl");if(!m)return;
function close(){var f=m.querySelector("iframe");if(f)f.remove();m.classList.remove("on","v")}
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("a[data-yt]");
if(a&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey){e.preventDefault();close();var f=document.createElement("iframe");
f.src="https://www.youtube-nocookie.com/embed/"+a.dataset.yt+"?autoplay=1&rel=0";f.allow="autoplay; encrypted-media; picture-in-picture; fullscreen";f.allowFullscreen=true;
m.insertBefore(f,l);l.href=a.href;m.classList.add("on");if(a.hasAttribute("data-short"))m.classList.add("v");return}
if(e.target===m||e.target.classList.contains("x"))close()});
document.addEventListener("keydown",function(e){if(e.key==="Escape")close()})})()</script>"""


def page(path, title, body, prof, active, desc, up=None, index=True):
    up = "../" * path.count("/") if up is None else up
    if index:
        PAGES.append(path)
    links = prof["links"]
    menu = "".join(f'<a class="{"on" if active == href else ""}" href="{up}{href}"{" aria-current=page" if active == href else ""}>{lab}</a>' for href, lab in MENU)
    ext = " · ".join(f'<a href="{E(u)}">{n}</a>' for n, u in (("YouTube", links.get("youtube")), ("LinkedIn", links.get("linkedin")), ("Google Scholar", links.get("scholar"))) if u)
    banner = f"""<div class="banner">{NET}<h1>{E(prof["name"])}.</h1><p>{E(prof["title"])} · {E(prof["institution"])}</p></div>"""
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="icon" href="{FAVICON}">{f'<link rel="canonical" href="{SITE}/{"" if path == "index.html" else path}">' if index else '<meta name="robots" content="noindex">'}
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="{SITE}/assets/img/photo.jpg">
<meta name="theme-color" content="#0b1b2e">{THEME_JS}{FONTS}<link rel="stylesheet" href="{up}assets/site.css?v={CSS_V}"></head>
<body><div class="sheet"><div class="bar"><a class="brand" href="{up}index.html">aafaq<b>cs</b></a><span class="inst">GCET KASHMIR<small>DEPARTMENT OF CSE</small></span>{THEME}</div>
<div class="cols"><div class="left"><img class="photo" src="{up}assets/img/photo.jpg" alt="{E(prof["name"])}">
<nav class="menu">{menu}</nav>
<div class="note">Preparing for GATE DA 2027? The full <a href="{up}courses/gate-da-ml.html">Machine Learning series</a> is free on YouTube, built on real data.</div>
<a class="follow" href="{E(links.get("youtube", ""))}">▶ Subscribe on YouTube</a></div>
<main class="right">{banner}{body}</main></div>{PLAYER}
<footer><span>© {date.today().year} {E(prof["name"])}</span><span>{ext}</span><span class="photo-credit">Campus photo: GCET Kashmir</span><span class="sp">Last updated {date.today():%B %Y}</span></footer></div></body></html>"""
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")


def redirect(path, to):
    (DIST / path).write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}"><a href="{to}">{to}</a>')


TEACH = ROOT / "teaching"
PRACTICE_WORDS = ("practice", "question", "assignment", "quiz", "tutorial", "sheet", "problem", "exercise")


NOTES_WORDS = ("note", "handout")


def week_files(slug, n):
    """Files in teaching/<slug>/weekNN/: 'note'/'handout' → notes; practice/question/... → practice; everything else → slides."""
    d = TEACH / slug / f"week{n:02d}"
    slides, practice, notes = [], [], []
    if d.is_dir():
        for f in sorted(d.iterdir()):
            if f.is_file() and not f.name.startswith(".") and f.name.lower() != "readme.txt":
                low = f.name.lower()
                (notes if any(w in low for w in NOTES_WORDS) else practice if any(w in low for w in PRACTICE_WORDS) else slides).append(f)
    return slides, practice, notes


def file_pill(f, up, slug, n, cls, label):
    from urllib.parse import quote
    out = DIST / "teaching" / slug / f"week{n:02d}" / f.name
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(f, out)
    kind = {".ppt": "PPT", ".pptx": "PPT", ".pdf": "PDF", ".doc": "DOC", ".docx": "DOC", ".key": "Keynote"}.get(f.suffix.lower(), f.suffix.lstrip(".").upper())
    icon = {"Slides": "▣", "Notes": "✎", "Practice": "?"}.get(label, "⬇")
    return f'<a class="fbtn {cls}" href="{up}teaching/{slug}/week{n:02d}/{quote(f.name)}" target="_blank" rel="noopener">{icon} {label} · {kind}</a>'


def gcr_html(sub, big=False):
    if sub.get("gcr_link"):
        code = f' <span class="meta">Class code: <b>{E(sub["gcr_code"])}</b></span>' if sub.get("gcr_code") else ""
        return f'<a class="pill gcr" href="{E(sub["gcr_link"])}">Join Google Classroom</a>{code}'
    if sub.get("gcr_code"):
        return f'<span>Google Classroom code: <b>{E(sub["gcr_code"])}</b></span> <a class="pill gcr" href="https://classroom.google.com/">Open Classroom</a>'
    return '<span class="meta">Google Classroom: ask in class for the joining code.</span>'


def news_date(d):
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", d or "")
    if not m:
        return E(d or "")
    return f"{int(m.group(3))} {('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')[int(m.group(2)) - 1]} {m.group(1)}"


def news_item(n):
    """A news entry is a dict {date, kind, text, pin} (older plain strings still work)."""
    if isinstance(n, str):
        return f"<li>{news_tag(n)}{rich(n)}</li>"
    kind = n.get("kind", "")
    tag = {"video": '<span class="tag video">Video</span>', "short": '<span class="tag short">Short</span>',
           "paper": '<span class="tag paper">Paper</span>', "milestone": '<span class="tag milestone">Milestone</span>'}.get(kind) or news_tag(n["text"])
    return f'<li><span class="when">{news_date(n.get("date"))}</span>{tag}{rich(n["text"])}</li>'


def news_tag(text):
    t = text.lower()
    if t.startswith(("released", "started", "finished")):
        return '<span class="tag video">Video</span>'
    if t.startswith("our paper") or "journal" in t:
        return '<span class="tag paper">Paper</span>'
    return '<span class="tag milestone">Milestone</span>'


def build():
    prof, courses, classes, pubs = D("profile"), D("courses")["courses"], D("classes")["classes"], D("publications")
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    shutil.copytree(ROOT / "assets" / "img", DIST / "assets" / "img")
    (DIST / "assets" / "site.css").write_text(CSS, encoding="utf-8")
    global CSS_V
    CSS_V = hashlib.sha1(CSS.encode()).hexdigest()[:8]
    links, m = prof["links"], pubs["metrics"]
    name = prof["name"]

    def counts(c):
        live = sum(l["status"] == "live" for l in c["lessons"])
        return live, c.get("total", len(c["lessons"]))

    def cover(c, up=""):
        t = next((l["thumb"] for l in c["lessons"] if l.get("thumb")), None)
        return f'<img src="{up}{t}" alt="" loading="lazy">' if t else '<div class="ph"></div>'

    def card(c, up=""):
        live, total = counts(c)
        return f"""<a class="pl" href="{up}courses/{c["slug"]}.html"><div class="stack"><div class="cov">{cover(c, up)}
<div class="side"><i>≡▶</i><b>{live}</b><span>video{"s" if live != 1 else ""}</span></div><div class="play">▶ VIEW PLAYLIST</div></div></div>
<div class="tx"><span class="chip">{E(c["short"])}</span><b>{E(c["title"])}</b><p>{E(c["blurb"])}</p>
<div class="prog"><i style="width:{100 * live / max(total, 1):.0f}%"></i></div><span class="meta">{live} of {total} published</span></div></a>"""

    def pub_html(p):
        badges = f'<span class="badge">{p["year"]}</span>'
        if p.get("impact_factor"):
            badges += f'<span class="badge if">IF {E(str(p["impact_factor"]))}</span>'
        if p.get("citations"):
            badges += f'<span class="badge">cited by {p["citations"]}</span>'
        return f'<div class="pub"><b>{E(p["title"])}</b><span>{E(p["venue"])}</span>{badges}</div>'

    stats = '<div class="stats">' + "".join(f'<div class="stat"><b>{E(n)}</b><small>{E(t)}</small></div>' for n, t in
                                            (prof.get("highlights", [])[:3] + [[str(m["citations"]), "citations on Google Scholar"]])) + "</div>"

    # Home
    research = ", ".join(pubs["interests"]).lower()
    home = f"""<p>I am an Assistant Professor in the Department of Computer Science &amp; Engineering at <a href="https://gcetkashmir.ac.in">GCET Kashmir</a>.</p>
<p>My research is in machine learning on graphs: {E(research)}. My PhD at <a href="https://nitsri.ac.in">NIT Srinagar</a> studied why deep graph neural networks lose information as they grow (over-smoothing and over-squashing) and how to build networks that don't. I also make free visual lectures for GATE and engineering students, where every graph is computed from real data and every answer is checked.</p>
{stats}
{h2("What's new")}<ul class="news">{"".join(news_item(n) for n in prof.get("news", []))}</ul>
{h2("Video courses")}<div class="pls">{"".join(card(c) for c in courses[:3])}</div>
<p class="more"><a href="courses.html">All video courses →</a></p>
{h2("Latest publications")}{"".join(pub_html(p) for p in sorted(pubs["publications"], key=lambda p: -p["year"])[:3])}
<p class="more"><a href="publications.html">All publications →</a></p>"""
    page("index.html", f"{name} · GCET Kashmir", home, prof, "index.html", f"{name}: Assistant Professor, CSE, GCET Kashmir. Graph learning research and free visual lectures for GATE.")

    # Publications
    labels = {"journal": "Journal articles", "conference": "Conference papers", "chapter": "Book chapters"}
    groups = ""
    for t, lab in labels.items():
        items = sorted((p for p in pubs["publications"] if p.get("type") == t), key=lambda p: -p["year"])
        if items:
            groups += f"<h3>{lab}</h3>" + "".join(pub_html(p) for p in items)
    if pubs.get("under_review"):
        groups += "<h3>Under review</h3>" + "".join(f'<div class="pub"><b>{E(p["title"])}</b><span>{E(p["venue"])}</span><span class="badge">{p["year"]}</span></div>' for p in pubs["under_review"])
    proj = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["title"])}</b><br><span class="meta">{E(x["note"])}</span></div>' for x in prof.get("projects", []))
    pubs_body = f"""{h2("Publications")}
<p class="metrics"><b>{m["citations"]}</b> citations · h-index <b>{m["h_index"]}</b> · i10-index <b>{m["i10_index"]}</b> · <a href="{E(links.get("scholar", ""))}">Google Scholar profile</a></p>{groups}
{h2("Research projects")}{proj}"""
    page("publications.html", f"Publications · {name}", pubs_body, prof, "publications.html", f"Publications of {name} on graph neural networks and geometric deep learning.")

    # Courses
    page("courses.html", f"Video courses · {name}", f"""{h2("Video courses")}
<p>Free visual lectures for GATE and engineering students, on my <a href="{E(links.get("youtube", ""))}">YouTube channel</a>. Every graph is computed from real data, and every answer is verified. Pick a course to see its lectures.</p>
<div class="pls">{"".join(card(c) for c in courses)}</div>""",
         prof, "courses.html", "Free visual computer-science lectures for GATE and engineering students, built on real data.")
    for c in courses:
        live, total = counts(c)
        rows = ""
        for l in c["lessons"]:
            img = f'<img src="../{l["thumb"]}" alt="" loading="lazy">' if l.get("thumb") else '<div class="ph"></div>'
            code = f'<span class="code">{E(l["code"])}</span>' if l.get("code") else ""
            inner = f'{img}<div>{code}<b>{E(l["title"])}</b><small>{E(l.get("meta", ""))}</small></div>'
            if l.get("youtube"):
                vid = l["youtube"].rstrip("/").rsplit("/", 1)[-1].split("=")[-1]
                rows += f'<a class="lec" href="{E(l["youtube"])}" data-yt="{E(vid)}"{" data-short" if l.get("code") == "SHORT" else ""}>{inner}<span class="go">Watch ▸</span></a>'
            else:
                rows += f'<div class="lec">{inner}<span class="soon">Coming soon</span></div>'
        first = next((l for l in c["lessons"] if l.get("youtube")), None)
        play = (f'<a class="btnp" href="{E(first["youtube"])}" data-yt="{E(first["youtube"].rstrip("/").rsplit("/", 1)[-1].split("=")[-1])}">▶ Play first video</a>' if first else "")
        body = f"""<p class="crumb"><a href="../courses.html">Video courses</a> › {E(c["short"])}</p>
<div class="plhead">{cover(c, "../")}<div>{h2(c["title"])}<p>{E(c["blurb"])}</p><p class="meta">{live} of {total} lectures published · free on YouTube</p>{play}</div></div>{rows}"""
        page(f"courses/{c['slug']}.html", f"{c['title']} · {prof['short_name']}", body, prof, "courses.html", c["blurb"])

    # Teaching: a placard per subject → subject page with Slides · Notes · Practice · Videos tabs
    T = D("teaching")
    by_slug = {c["slug"]: c for c in courses}
    PALETTE = [("#0f2a4a", "#0e8a7e"), ("#3b1d6e", "#7c4dff"), ("#7a2e0b", "#e8590c"), ("#0b3b5c", "#1f9ad6"), ("#1e3a1e", "#2f9e44")]
    TABJS = """<script>document.addEventListener("click",function(e){var b=e.target.closest&&e.target.closest(".tabs button");if(!b)return;
var w=b.closest(".tabwrap");w.querySelectorAll(".tabs button").forEach(function(x){x.setAttribute("aria-selected",x===b)});
w.querySelectorAll(".tabpane").forEach(function(p){p.classList.toggle("on",p.id===b.dataset.t)});history.replaceState(null,"","#"+b.dataset.t)});
window.addEventListener("load",function(){var h=location.hash.slice(1);var b=h&&document.querySelector('.tabs button[data-t="'+h+'"]');if(b)b.click()})</script>"""
    cards = ""
    for i, sub in enumerate(T["subjects"]):
        c1, c2 = PALETTE[i % len(PALETTE)]
        n_w = len(sub["weeks"])
        wf = [week_files(sub["slug"], k) for k in range(1, n_w + 1)]
        n_sl, n_pr, n_no = (sum(len(w[j]) for w in wf) for j in range(3))
        vids = [l for vc in sub.get("video_courses", []) for l in by_slug.get(vc, {}).get("lessons", []) if l.get("youtube")]
        cards += f"""<a class="tc" href="teaching/{sub["slug"]}.html" style="--c1:{c1};--c2:{c2}"><div class="top"><span class="sem">{E(T.get("semester", ""))}</span>
<div class="code">{E(sub["code"])}</div><div class="nm">{E(sub["title"])}</div></div>
<div class="bot"><p>{E(sub["blurb"])}</p><div class="res"><span>▣ Slides <b>{n_sl}</b></span><span>✎ Notes <b>{n_no}</b></span><span>? Practice <b>{n_pr}</b></span><span>▶ Videos <b>{len(vids)}</b></span></div>
<span class="meta">{E(sub.get("programme", ""))} · {n_w} weeks · open course →</span></div></a>"""

        def pane(idx, cls, label):
            rows = ""
            for k, topic in enumerate(sub["weeks"], 1):
                files = "".join(file_pill(f, "../", sub["slug"], k, cls, label) for f in wf[k - 1][idx])
                rows += f'<div class="res-row"><span class="wk">WEEK {k:02d}</span><span class="t">{E(topic)}</span><span class="f">{files or f"<span class=\'fbtn off\'>{label} soon</span>"}</span></div>'
            return rows
        vrows = ""
        for k, l in enumerate(vids, 1):
            vid = l["youtube"].rstrip("/").rsplit("/", 1)[-1].split("=")[-1]
            img = f'<img src="../{l["thumb"]}" alt="" loading="lazy">' if l.get("thumb") else '<div class="ph"></div>'
            vrows += f'<a class="lec" href="{E(l["youtube"])}" data-yt="{E(vid)}">{img}<div><b>{E(l["title"])}</b><small>{E(l.get("meta", ""))}</small></div><span class="go">Watch ▸</span></a>'
        vpane = vrows or '<div class="empty-pane">Video lectures for this course are on the way. Meanwhile, see all <a href="../courses.html">video courses</a>.</div>'
        tabs = [("slides", "▣ Slides", n_sl, pane(0, "", "Slides")), ("notes", "✎ Notes", n_no, pane(2, "notes", "Notes")),
                ("practice", "? Practice Questions", n_pr, pane(1, "prac", "Practice")), ("videos", "▶ Videos", len(vids), vpane)]
        tabbar = "".join(f'<button type="button" role="tab" data-t="{t}" aria-selected="{"true" if j == 0 else "false"}">{lab}<span class="n">{n}</span></button>' for j, (t, lab, n, _) in enumerate(tabs))
        panes = "".join(f'<div class="tabpane{" on" if j == 0 else ""}" id="{t}" role="tabpanel">{html_}</div>' for j, (t, _, _, html_) in enumerate(tabs))
        body = f"""<p class="crumb"><a href="../classes.html">Teaching</a> › {E(sub["code"])}</p>
<div class="plhead" style="grid-template-columns:1fr"><div>{h2(sub["title"])}<p>{E(sub["blurb"])}</p><p class="meta">{E(sub.get("programme", ""))} · {E(T.get("semester", ""))} · {n_w} weeks</p><div class="gcrbox" style="margin-top:8px">{gcr_html(sub)}</div></div></div>
<div class="tabwrap"><div class="tabs" role="tablist">{tabbar}</div>{panes}</div>{TABJS}"""
        page(f"teaching/{sub['slug']}.html", f"{sub['title']} · {prof['short_name']}", body, prof, "classes.html", f"{sub['title']}: slides, notes, practice questions and video lectures. {sub['blurb']}")
    page("classes.html", f"Teaching · {name}", f"""{h2("My courses · " + T.get("semester", ""))}<p>Courses I teach at {E(prof["institution"])}. Open a course for its slides, notes, practice questions and videos, week by week, plus its Google Classroom.</p>
<div class="tcs">{cards}</div>{h2("Free video courses")}<p>Visual lectures that go with these courses are on the <a href="courses.html">video courses</a> page.</p>""",
         prof, "classes.html", f"Courses taught by {name}: slides, notes, practice questions, videos and Google Classroom links.")

    # Bio
    story = "".join(f"<p>{E(x)}</p>" for x in (prof.get("bio_story") or [prof["bio"]]))
    hl = '<div class="stats">' + "".join(f'<div class="stat"><b>{E(n)}</b><small>{E(t)}</small></div>' for n, t in prof.get("highlights", [])) + "</div>"
    exp = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["role"])}</b>, {E(x["where"])}<ul>{"".join(f"<li>{E(pt)}</li>" for pt in x["points"])}</ul></div>' for x in prof.get("experience", []))
    edu = "".join(f'<div class="tl"><span class="when">{E(x["when"])}</span><br><b>{E(x["degree"])}</b>, {E(x["where"])}<br><span class="meta">{E(x["note"])}</span></div>' for x in prof.get("education", []))
    lst = lambda xs: '<ul class="plain">' + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    bio_body = f"""{h2("Bio")}{f'<div class="quote">{E(prof["headline"])}</div>' if prof.get("headline") else ""}{story}
{hl}{h2("Experience")}{exp}{h2("Education")}{edu}
{h2("Achievements & fellowships")}{lst(prof.get("achievements", []))}
{h2("Roles at GCET")}{lst(prof.get("roles", []))}<h3>Certifications</h3>{lst(prof.get("certifications", []))}"""
    page("bio.html", f"Bio · {name}", bio_body, prof, "bio.html", f"Biography of {name}.")

    # Contact
    em = "<br>".join(f'<a href="mailto:{E(x)}">{E(x)}</a>' for x in prof.get("emails", []))
    ext = "<br>".join(f'<a href="{E(u)}">{n}</a>' for n, u in (("YouTube", links.get("youtube")), ("LinkedIn", links.get("linkedin")), ("Google Scholar", links.get("scholar")), ("ORCID", links.get("orcid"))) if u)
    page("contact.html", f"Contact · {name}", f"""{h2("Contact")}
<div class="contact"><div><b>Email</b>{em}</div><div><b>Office</b>{E(prof.get("address", prof["institution"]))}</div><div><b>Elsewhere</b>{ext}</div></div>""",
         prof, "contact.html", f"How to contact {name}.")

    redirect("about.html", "index.html")

    # Netlify extras: 404 page (absolute paths, so it works at any depth), caching/security headers, robots + sitemap
    page("404.html", f"Page not found · {name}", f"""{h2("Page not found")}
<p>That page doesn't exist, or it has moved.</p><p class="more"><a href="/index.html">Go to the home page →</a> · <a href="/courses.html">Video courses →</a></p>""",
         prof, "", "Page not found.", up="/", index=False)
    (DIST / "_headers").write_text("""/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
/assets/img/*
  Cache-Control: public, max-age=604800
/assets/site.css
  Cache-Control: public, max-age=86400
""", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(f"<url><loc>{SITE}/{'' if p == 'index.html' else p}</loc><lastmod>{date.today()}</lastmod></url>" for p in PAGES)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
    print("built", sum(1 for _ in DIST.rglob("*.html")), "pages into", DIST)


if __name__ == "__main__":
    build()
