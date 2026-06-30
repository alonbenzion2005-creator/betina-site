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

# c4 "The Reveal": continue glimpse big photo (cut at its bottom) downward, then space into colors.
REVEAL = ('  <!-- connector: The Reveal (completes glimpse big photo into colors) -->\n'
          '  <section class="connector" id="c4" data-name="The Reveal">\n'
          '    <div class="cinner" style="height:18cqw">\n'
          '      <div class="ph" style="left:0%; top:0; width:72.047%; height:11cqw; border:0; '
          'background-image:url(\'assets/glimpse-group.jpg\'); background-size:cover; background-position:center bottom;"></div>\n'
          '    </div>\n'
          '  </section>')

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
