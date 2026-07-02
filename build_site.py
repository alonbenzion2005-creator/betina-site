#!/usr/bin/env python3
"""Assemble the 8 measured screens into one long site.html with named connectors.

Each screen is a self-contained doc with an inline <style> whose component class
names collide across screens. We scope every rule under a per-section id (#s1..#s8)
so the screens stack without cross-contamination, sharing one head/palette.
Connectors (named) sit between screens: spacing + completion of edge-sliced photos.
Re-runnable: edit a screen, re-run, site.html regenerates.
"""
import re, pathlib

HERE = pathlib.Path(__file__).parent

# (section id, file, connector-after spec)  -- in the user's build order
SCREENS = [
    ("s1", "home2.html"),
    ("s2", "reviews.html"),
    ("s3", "methods.html"),
    ("s4", "glimpse.html"),
    ("s5", "colors.html"),
    ("s6", "pricing.html"),
    ("s7", "group.html"),
    ("s8", "cta-footer.html"),
]

def extract(html, tag):
    m = re.search(r"<%s[^>]*>(.*?)</%s>" % (tag, tag), html, re.S)
    return m.group(1) if m else ""

def scope_css(css, scope):
    """Prefix every rule's selector with #scope. :root -> #scope; drop */body/html."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)  # strip comments
    out, i, n = [], 0, len(css)
    while i < n:
        b = css.find("{", i)
        if b == -1:
            break
        sel = css[i:b].strip()
        e = css.find("}", b + 1)
        if e == -1:
            break
        block = css[b + 1:e].strip()
        i = e + 1
        if not sel:
            continue
        if sel.startswith("@"):            # at-rule (none expected) -> leave as-is
            out.append("%s{ %s }" % (sel, block))
            continue
        parts = [p.strip() for p in sel.split(",") if p.strip()]
        new, drop = [], False
        for p in parts:
            if p == ":root":
                new.append("#" + scope)
            elif p in ("*", "body", "html"):
                drop = True
                break
            else:
                new.append("#%s %s" % (scope, p))
        if drop:
            continue
        out.append("%s{ %s }" % (", ".join(new), block))
    return "\n".join(out)

# ---- gather screens ----
sections_css, sections_html = [], {}
for sid, fname in SCREENS:
    html = (HERE / fname).read_text(encoding="utf-8")
    sections_css.append("/* ===== %s (%s) ===== */\n%s" % (sid, fname, scope_css(extract(html, "style"), sid)))
    sections_html[sid] = extract(html, "body").strip()

# ---- connectors (named): spacing + photo completion only ----
def spacer(cid, name, h):
    return ('  <!-- connector: %s -->\n'
            '  <section class="connector" id="%s" data-name="%s">'
            '<div class="cinner" style="height:%scqw"></div></section>' % (name, cid, name, h))

# c3 "The Seam": methods top-half photo abuts glimpse lower-half photo (zero gap;
# the join is done by border overrides in shared CSS so the two halves read as one).
SEAM = ('  <!-- connector: The Seam (methods ↔ glimpse photo join) -->\n'
        '  <section class="connector" id="c3" data-name="The Seam"></section>')

# c4 "The Reveal": glimpse group is now a complete photo, so just space into colors
# (no continuation strip -- that duplicated the photo's bottom band).
REVEAL = spacer("c4", "The Reveal", 8)

CONNECTORS = {
    "c1": spacer("c1", "The Drop-In", 7),
    "c2": spacer("c2", "The Turn", 7),
    "c3": SEAM,
    "c4": REVEAL,
    "c5": spacer("c5", "The Ledger", 7),
    "c6": spacer("c6", "The Gather", 8),
    "c7": spacer("c7", "The Close", 8),
}

# The header "Find Your Perfect Match" is identical on methods (s3), colors (s5) and
# pricing (s6). Instead of repeating it three times, render it ONCE as a sticky title
# that stays pinned at the top of the viewport while that whole band (s3..s6) scrolls
# past -- "rolled down at the top from the first marking to the last".
BAND_TITLE = ('  <div class="bandtitle">\n'
              '    <h2 class="bt-title">Find Your Perfect Match</h2>\n'
              '    <p class="bt-sub">We offer a curated selection of premium methods for flawless results.</p>\n'
              '  </div>')

# ---- assemble body in order: s1 c1 s2 c2 [titleband: s3 c3 s4 c4 s5 c5 s6] c6 s7 c7 s8 ----
body_parts = []
for idx, (sid, _) in enumerate(SCREENS):
    if sid == "s3":
        body_parts.append('  <!-- unified sticky section title: methods -> pricing -->')
        body_parts.append('  <div class="titleband">')
        body_parts.append(BAND_TITLE)
    body_parts.append('  <section class="screen" id="%s">\n%s\n  </section>' % (sid, sections_html[sid]))
    if sid == "s6":
        body_parts.append('  </div><!-- /titleband -->')
    cid = "c%d" % (idx + 1)
    if cid in CONNECTORS:
        body_parts.append(CONNECTORS[cid])
body_html = "\n".join(body_parts)

SHARED_HEAD = """    :root{
      --paper:#fdfcfa; --ink:#1b1815; --ink-soft:#6b6358; --gold-deep:#8f6a3f;
      --rule:#e6ded0; --quote:#2e3a45; --card:#f2efe9;
      --serif:"Cormorant Garamond",Georgia,serif;
      --display:"Bodoni Moda","Didot",Georgia,serif;
      --label:"Jost","Helvetica Neue",Arial,sans-serif;
    }
    *{box-sizing:border-box;margin:0;padding:0;}
    body{ background:var(--paper); color:var(--ink); font-family:var(--serif);
      min-height:100vh; display:flex; flex-direction:column; align-items:center; }

    /* stacking wrappers */
    .screen{ width:100%; display:flex; justify-content:center; }
    .connector{ width:100%; display:flex; justify-content:center; background:var(--paper); }
    .cinner{ position:relative; width:100%; max-width:1109px; container-type:inline-size; }
    .connector .ph{
      position:absolute; display:flex; align-items:center; justify-content:center;
      background:repeating-linear-gradient(135deg,#ece5da 0 14px,#e6ddcf 14px 28px);
      border:1px dashed #bcae97; color:#9a8c74; overflow:hidden;
    }
    .connector .ph span{ font-family:var(--label); text-transform:uppercase; letter-spacing:0.2em;
      font-size:0.85cqw; text-align:center; padding:0.6em; }
    .connector .ph span::before{ content:"\\2b21"; display:block; font-size:1.6cqw; margin-bottom:0.4em; color:#c2b49b; }
"""

# Placed AFTER the section CSS so it wins the same-specificity cascade.
JOIN_OVERRIDES = """    /* ---- photo joins (assembled-site only; original screens untouched) ---- */
    /* The Seam: methods' top-half photo + glimpse's lower-half photo -> one portrait */
    #s3 .pic{ border-bottom:0; }
    #s4 .pic-top{ left:41.840%; width:27.773%; border-top:0; }
    /* The Reveal: glimpse big photo flows past its bottom edge */
    #s4 .pic-big{ border-bottom:0; }

    /* ---- Unified sticky section title (methods -> pricing) ---- */
    /* the three duplicate per-screen titles are suppressed; one sticky title rides the band */
    #s3 .title, #s3 .subtitle,
    #s5 .title, #s5 .subtitle,
    #s6 .title, #s6 .subtitle{ display:none; }

    .titleband{ position:relative; width:100%; display:flex; flex-direction:column; align-items:center; }
    .bandtitle{
      position:sticky; top:0; z-index:30;
      width:100%; max-width:1109px;
      container-type:inline-size;
      background:var(--paper);
      text-align:center;
      padding-top:2.2cqw; padding-bottom:1.4cqw;
      border-bottom:1px solid rgba(27,24,21,0.07);
    }
    .bandtitle .bt-title{
      font-family:var(--display); font-weight:500;
      font-size:1.85cqw; line-height:1; letter-spacing:0.005em; color:var(--ink);
    }
    .bandtitle .bt-sub{
      font-family:var(--serif); font-style:italic; color:var(--ink-soft);
      font-size:1.07cqw; line-height:1; letter-spacing:0.01em; margin-top:1.0cqw;
    }
"""

doc = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LA GOLD</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,500;1,6..96,500&family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&family=Jost:wght@300;400&display=swap" rel="stylesheet" />
  <style>
%s

%s

%s
  </style>
</head>
<body>
%s
</body>
</html>
""" % (SHARED_HEAD, "\n\n".join(sections_css), JOIN_OVERRIDES, body_html)

(HERE / "index.html").write_text(doc, encoding="utf-8")
print("Wrote index.html  (%d bytes)" % len(doc))
print("Sections:", ", ".join(sid for sid, _ in SCREENS))
print("Connectors:", "c1 The Drop-In, c2 The Turn, c3 The Seam, c4 The Reveal, c5 The Ledger, c6 The Gather, c7 The Close")

# ======================================================================
# alive.html -- a livelier *interpretation* of the same site. Same content
# and layout; adds motion (scroll reveals, a slow Ken-Burns drift on the
# feature photos, hover warmth). The static index.html stays untouched.
# ======================================================================
ALIVE_CSS = """
    /* ============ alive interpretation (motion layer) ============ */
    body.alive{ scroll-behavior:smooth; }

    /* scroll reveal: everything fades up as it enters view */
    body.alive .rv{ opacity:0; transition:opacity 1s ease, transform 1s cubic-bezier(.22,.61,.36,1); }
    body.alive .rv.up{ transform:translateY(26px); }
    body.alive .rv.in{ opacity:1; transform:none; }

    /* slow Ken-Burns drift on the big feature photographs. The photo FRAME
       keeps the exact static geometry and clips its content; only an oversized
       inner image layer (inset:-9% -> larger than the frame on every side)
       moves, so the drift never spills past the frame or shifts the layout,
       and the enlargement guarantees no edge gaps while it pans/zooms. */
    body.alive .kbimg{
      position:absolute; inset:-9%;
      background-size:cover; background-position:center;
      will-change:transform;
      animation: aliveKB 26s ease-in-out infinite alternate;
    }
    @keyframes aliveKB{
      from{ transform:scale(1.00) translate(-1.6%, -1.3%); }
      to  { transform:scale(1.05) translate( 1.6%,  1.4%); }
    }

    /* hero logo breathes in on load */
    body.alive #s1 .logo{ animation: aliveRise 1.4s cubic-bezier(.22,.61,.36,1) both; }
    @keyframes aliveRise{ from{opacity:0; letter-spacing:0.18em;} to{opacity:1;} }

    /* photographs warm slightly on hover */
    body.alive .ph{ transition:filter .6s ease, box-shadow .6s ease; }
    body.alive .screen .ph:hover{ filter:brightness(1.05) contrast(1.02);
      box-shadow:0 12px 44px rgba(27,24,21,.18); }
    /* The Seam portrait is one image split across two screens (#s3 .pic +
       #s4 .pic-top). JS mirrors the hover onto both halves (.seamhover) so the
       whole portrait lights up as one. Filter-only glow -- no box-shadow, which
       would otherwise draw a line along the internal join. */
    body.alive #s3 .pic:hover, body.alive #s4 .pic-top:hover{ box-shadow:none; }
    body.alive #s3 .pic.seamhover, body.alive #s4 .pic-top.seamhover{
      filter:brightness(1.05) contrast(1.02); box-shadow:none; }

    @media (prefers-reduced-motion: reduce){
      body.alive .rv{ opacity:1 !important; transform:none !important; transition:none; }
      body.alive .kbimg, body.alive .logo{ animation:none !important; }
    }
"""

ALIVE_JS = """  <script>
  (function(){
    var mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    if (mq.matches) return;
    // reveal every stage child + the sticky band title as it scrolls into view
    var targets = document.querySelectorAll('.screen .stage > *, .bandtitle');
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function(el, i){
      el.classList.add('rv');
      // photos fade only (they carry the Ken-Burns transform); text also rises
      var bg = el.style && el.style.backgroundImage;
      if(!(el.classList.contains('ph') || bg)) el.classList.add('up');
      // gentle stagger within each screen
      var stage = el.closest('.stage');
      var sibs = stage ? Array.prototype.indexOf.call(stage.children, el) : i;
      el.style.transitionDelay = (Math.max(0, sibs) % 8 * 70) + 'ms';
      io.observe(el);
    });
    // The Seam portrait is split across two screens -- mirror hover onto both
    // halves so the whole photo lights up uniformly.
    var seam = [document.querySelector('#s3 .pic'),
                document.querySelector('#s4 .pic-top')].filter(Boolean);
    if(seam.length === 2){
      seam.forEach(function(el){
        el.addEventListener('mouseenter', function(){
          seam.forEach(function(x){ x.classList.add('seamhover'); }); });
        el.addEventListener('mouseleave', function(){
          seam.forEach(function(x){ x.classList.remove('seamhover'); }); });
      });
    }
  })();
  </script>
"""

alive_doc = doc.replace("<body>", '<body class="alive">', 1)
alive_doc = alive_doc.replace("  </style>", ALIVE_CSS + "  </style>", 1)
alive_doc = alive_doc.replace("</body>", ALIVE_JS + "</body>", 1)

# Wrap the six feature photos so the Ken-Burns moves an inner oversized layer
# inside the exact static frame (which now just clips), instead of scaling the
# frame itself. Identify them by their asset filenames so only these six change.
import re as _re
_KB_PHOTOS = ("home-portrait", "reviews-community", "glimpse-group",
              "colors-portrait", "pricing-custom", "group-squad")
def _wrap_kb(m):
    cls, asset = m.group(1), m.group(2)
    return ('<div class="ph %s" style="border:0;overflow:hidden;">'
            '<div class="kbimg" style="background-image:url(\'assets/%s.jpg\');">'
            '</div></div>' % (cls, asset))
_kb_pat = _re.compile(
    r'<div class="ph ([^"]+)" style="background-image:url\(\'assets/('
    + "|".join(_KB_PHOTOS) +
    r')\.jpg\'\);background-size:cover;background-position:center;border:0;"></div>')
alive_doc, _n = _kb_pat.subn(_wrap_kb, alive_doc)
assert _n == len(_KB_PHOTOS), "expected %d KB photos, wrapped %d" % (len(_KB_PHOTOS), _n)
(HERE / "alive.html").write_text(alive_doc, encoding="utf-8")
print("Wrote alive.html  (%d bytes)  -- livelier interpretation, index.html untouched" % len(alive_doc))
