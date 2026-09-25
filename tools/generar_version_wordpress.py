"""Builds the WordPress / Elementor paste-in version from the standalone index.html.

Usage (from the repo root):
    python3 tools/generar_version_wordpress.py index.html wordpress/codigo-para-wordpress-elementor.html

Run it again after every change to index.html so both versions stay identical.

The standalone page styles <html>/<body> and uses generic class names. Pasted inside a
WordPress theme that would leak both ways, so this script:
  * prefixes every class, keyframe, data-attribute and internal id with "lo-"
  * scopes every CSS rule under #lo-page (and neutralises theme styles with all:revert)
  * moves the "js" state class from <html> to the wrapper
  * makes the wrapper break out to full width inside boxed containers
"""
import re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
src = open(SRC, encoding='utf-8').read()

css = re.search(r'<style>\n(.*?)\n  </style>', src, re.S).group(1)
tracking = re.search(r'(  <!-- Meta Pixel Code -->.*?<!-- End Microsoft Clarity Code -->)', src, re.S).group(1)
body = re.search(r'<body>\n(.*?)\n<script>\n\(\(\) => \{', src, re.S).group(1)
js = re.search(r'\n<script>\n(\(\(\) => \{.*?\}\)\(\);)\n</script>\n</body>', src, re.S).group(1)
fonts = re.search(r'(  <link rel="preconnect" href="https://fonts.googleapis.com">.*?rel="stylesheet" />)', src, re.S).group(1)

DATA = ['reveal', 'split', 'inview', 'keep', 'anagram', 'receipt', 'timeline', 'board', 'chat', 'magnetic', 'intro', 'year']
KEYFRAMES = sorted(set(re.findall(r'@keyframes\s+([\w-]+)', css)))
IDS = ['nav', 'top', 'hero-title', 'whom-title', 'services-title', 'how-title', 'price-title', 'faq-title', 'cta-title']
SYMBOLS = sorted(set(re.findall(r'<symbol id="([\w-]+)"', body)))

def ren_data(s):
    return re.sub(r'data-(%s)\b' % '|'.join(DATA), r'data-lo-\1', s)

# ---------- CSS ----------
def ren_classes(sel):
    return re.sub(r'\.([A-Za-z_][\w-]*)', r'.lo-\1', sel)

def split_top(sel):
    parts, depth, cur = [], 0, ''
    for ch in sel:
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == ',' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]

GLOBAL_EL = {'svg', 'a', 'button', '::selection', ':focus-visible', '[hidden]'}
def scope_selector(prelude):
    out = []
    for s in split_top(prelude):
        s = ren_data(s)
        if s in ('html', 'body'):
            continue
        if s == ':root':
            out.append('#lo-page'); continue
        if s.startswith('*'):
            out.append('#lo-page ' + s); continue
        if s in GLOBAL_EL:
            out.append('#lo-page ' + s); continue
        if s == '.js' or s.startswith('.js ') or s.startswith('.js.'):
            out.append('#lo-page.lo-js' + ren_classes(s[3:])); continue
        out.append('#lo-page ' + ren_classes(s))
    return ', '.join(out)

def ren_keyframes_in_decls(block):
    def fix(m):
        val = m.group(2)
        for k in KEYFRAMES:
            val = re.sub(r'(?<![\w-])%s(?![\w-])' % re.escape(k), 'lo-' + k, val)
        return m.group(1) + val
    return re.sub(r'(animation(?:-name)?\s*:)([^;}]*)', fix, block)

def parse_rules(text):
    """Recursive pass over a rule list; returns the transformed text."""
    out, i, n = [], 0, len(text)
    while i < n:
        j = text.find('{', i)
        if j == -1:
            out.append(text[i:]); break
        # copy comments / whitespace that precede the prelude untouched
        pre = text[i:j]
        lead = re.match(r'(\s*(?:/\*.*?\*/\s*)*)', pre, re.S).group(1)
        prelude = pre[len(lead):]
        # find the matching closing brace
        depth, k = 0, j
        while k < n:
            if text[k] == '{': depth += 1
            elif text[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        inner = text[j + 1:k]
        p = prelude.strip()
        if p.startswith('@media') or p.startswith('@supports'):
            out.append(lead + prelude + '{' + parse_rules(inner) + '}')
        elif p.startswith('@keyframes'):
            name = p.split()[1]
            out.append(lead + prelude.replace(name, 'lo-' + name, 1) + '{' + inner + '}')
        else:
            sel = scope_selector(p)
            if sel:
                trailing = prelude[len(prelude.rstrip()):]
                out.append(lead + sel + trailing + '{' + ren_keyframes_in_decls(inner) + '}')
            else:
                out.append(lead.rstrip(' ') if lead.endswith('\n    ') else lead)
        i = k + 1
    return ''.join(out)

css_scoped = parse_rules(css)
assert css_scoped.count('position: fixed; top: 0; left: 0; right: 0; z-index: 60;') == 1
css_scoped = css_scoped.replace('position: fixed; top: 0; left: 0; right: 0; z-index: 60;', 'position: fixed; top: 0; left: 0; right: 0; z-index: 9990;')

# ---------- HTML ----------
html = body
html = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % ' '.join('lo-' + t for t in m.group(1).split()), html)
for sid in SYMBOLS:
    html = html.replace('id="%s"' % sid, 'id="lo-%s"' % sid).replace('href="#%s"' % sid, 'href="#lo-%s"' % sid)
for i in IDS:
    html = re.sub(r'(id|aria-labelledby)="%s"' % re.escape(i), r'\1="lo-%s"' % i, html)
    html = html.replace('href="#%s"' % i, 'href="#lo-%s"' % i)
html = ren_data(html)
html = html.replace('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">',
                    '<svg style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true" focusable="false">')
# a WordPress theme already has its own <main>: keep a single main landmark on the page
html = html.replace('<main id="lo-top">', '<div class="lo-main" id="lo-top">').replace('</main>', '</div>')

# ---------- JS ----------
CLASSES = set(re.findall(r'\.([A-Za-z_][\w-]*)', ' '.join(re.findall(r'([^{}]+)\{', css)))) - {'js'}
CLASSES |= set(t for m in re.findall(r'class="([^"]*)"', body) for t in m.split())

def ren_js_string(s):
    s = ren_data(s)
    s = re.sub(r'#(%s)(?![\w-])' % '|'.join(map(re.escape, IDS)), r'#lo-\1', s)
    s = re.sub(r'class="([^"]*)"', lambda m: 'class="%s"' % ' '.join('lo-' + t for t in m.group(1).split()), s)
    s = re.sub(r'\.([A-Za-z_][\w-]*)', lambda m: '.lo-' + m.group(1) if m.group(1) in CLASSES else m.group(0), s)
    if s == 'js' or s in CLASSES:
        s = 'lo-' + s
    return s

js2 = re.sub(r"'((?:[^'\\\n]|\\.)*)'", lambda m: "'" + ren_js_string(m.group(1)) + "'", js)

def must(old, new):
    global js2
    assert js2.count(old) == 1, (js2.count(old), old)
    js2 = js2.replace(old, new)

must("""  const root = document.documentElement;
  if (window.__loInit) return;
  window.__loInit = true;

  const motionOK = root.classList.contains('lo-js') && !matchMedia('(prefers-reduced-motion: reduce)').matches;""",
"""  const root = document.getElementById('lo-page');
  if (!root || root.hasAttribute('data-lo-init')) return;
  root.setAttribute('data-lo-init', '');
  // Dentro del editor de Elementor se muestra quieta (las animaciones se ven en la vista previa / página publicada)
  const inEditor = !!(document.body && document.body.classList.contains('elementor-editor-active'));
  if (inEditor) root.classList.remove('lo-js');

  const motionOK = root.classList.contains('lo-js') && !matchMedia('(prefers-reduced-motion: reduce)').matches;""")
must("  const $ = (s, c = document) => c.querySelector(s);\n  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));",
     "  const $ = (s, c = root) => c.querySelector(s);\n  const $$ = (s, c = root) => Array.from(c.querySelectorAll(s));")
must("    window.__loReady = true;", "    root.setAttribute('data-lo-ready', '');")
must("    maxScroll = Math.max(1, root.scrollHeight - vh);", "    maxScroll = Math.max(1, document.documentElement.scrollHeight - vh);")
must("""  function update() {
    ticking = false;""", """  function update() {
    ticking = false;
    if (!root.isConnected) { removeEventListener('scroll', requestUpdate); return; }""")
must("""  safe(setupScroll);""", """  /* ── Ancho completo aunque el contenedor de WordPress sea angosto ── */
  function setupFullWidth() {
    const fit = () => root.style.setProperty('--lo-sbw', Math.max(0, innerWidth - document.documentElement.clientWidth) + 'px');
    fit();
    if ('ResizeObserver' in window) new ResizeObserver(fit).observe(document.documentElement);
    else addEventListener('resize', fit);
  }

  /* ── Enlaces internos (#servicios, volver arriba) con desplazamiento suave ── */
  function setupAnchors() {
    root.addEventListener('click', e => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const target = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: motionOK ? 'smooth' : 'auto', block: 'start' });
    });
  }

  safe(setupFullWidth);
  safe(setupAnchors);
  safe(setupScroll);""")

leftovers = re.findall(r"'([\w-]+)'", js2)
# ---------- CSS additions ----------
KF_LIST = ', '.join(KEYFRAMES)
head_css = """    /* ── AISLAMIENTO ──
       El tema de WordPress / Elementor no puede cambiar el diseño de esta página
       y esta página no cambia nada del resto del sitio. */
    #lo-page :where(*:not(svg, svg *)),
    #lo-page :where(*:not(svg, svg *))::before,
    #lo-page :where(*:not(svg, svg *))::after { all: revert; }

    /* ── CONTENEDOR (ocupa todo el ancho de la pantalla aunque la sección de Elementor sea angosta) ── */
    #lo-page {
      display: block; position: relative; box-sizing: border-box;
      width: calc(100vw - var(--lo-sbw, 0px)) !important;
      max-width: none !important;
      margin: 0 calc(50% - 50vw + var(--lo-sbw, 0px) / 2) !important;
      padding: 0 !important;
      border: 0 !important;
      overflow-x: clip;
      font-family: var(--sans); font-size: 16px; line-height: 1.6;
      font-weight: 400; font-style: normal; letter-spacing: normal; word-spacing: normal;
      text-align: left; text-transform: none; text-indent: 0; text-shadow: none;
      white-space: normal; -webkit-hyphens: manual; hyphens: manual;
      color: var(--text);
      background: var(--paper) var(--noise-dark) repeat;
      -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
      -webkit-text-size-adjust: 100%; text-size-adjust: 100%;
      color-scheme: only light;
      --d: 0; --i: 0; --ci: 0; --wi: 0; --depth: 0; --p: 0;
    }
    /* Elementor: sin márgenes internos en la sección que contiene la página (evita franjas blancas arriba y abajo) */
    .e-con:has(#lo-page), .e-con-inner:has(#lo-page),
    .elementor-element-populated:has(#lo-page), .elementor-widget-container:has(> #lo-page) {
      padding: 0 !important; gap: 0 !important;
    }
    .elementor-widget:has(> .elementor-widget-container > #lo-page) { margin: 0 !important; }

    #lo-page [id] { scroll-margin-top: 96px; }
    #lo-page button { -webkit-appearance: none; appearance: none; }
    #lo-page a { text-decoration: none; }
    /* con la barra de administración de WordPress visible (solo la ves vos, logueado) el menú se corre hacia abajo */
    body.admin-bar #lo-page .lo-nav { top: 32px; }
    @media (max-width: 782px) { body.admin-bar #lo-page .lo-nav { top: 46px; } }
    @media (max-width: 600px) { body.admin-bar #lo-page .lo-nav { top: 0; } }

"""

early = """<script>
/* Activa las animaciones solo si el JavaScript corre; si algo falla, a los 4 s se muestra todo quieto. */
(function () {
  var w = document.getElementById('lo-page');
  if (!w || w.hasAttribute('data-lo-ready')) return;
  if (document.body && document.body.classList.contains('elementor-editor-active')) return;
  w.style.setProperty('--lo-sbw', Math.max(0, window.innerWidth - document.documentElement.clientWidth) + 'px');
  w.classList.add('lo-js');
  setTimeout(function () { if (!w.hasAttribute('data-lo-ready')) w.classList.remove('lo-js'); }, 4000);
})();
</script>"""

header = """<!-- =====================================================================
     Lucas Olivera · Servicios Contables — versión para WordPress / Elementor
     Pegá TODO este código (de la primera a la última línea) en:
       · Elementor: widget «HTML»   ·   Editor de bloques: bloque «HTML personalizado»
     ===================================================================== -->

<!-- Pixel de Meta y Microsoft Clarity.
     Si ya los tenés instalados en todo el sitio (con un plugin o en el encabezado),
     borrá desde esta línea hasta «End Microsoft Clarity Code» para no contar visitas dobles. -->
"""

tracking_out = '\n'.join(l[2:] if l.startswith('  ') else l for l in tracking.split('\n'))
fonts_out = '\n'.join(l[2:] if l.startswith('  ') else l for l in fonts.split('\n'))

out = (header + tracking_out + '\n\n<!-- Tipografías -->\n' + fonts_out + '\n\n<style>\n' + head_css + css_scoped + '\n</style>\n\n'
       + '<div id="lo-page" class="lo-page alignfull">\n' + early + '\n\n' + html + '\n\n<script>\n' + js2 + '\n</script>\n</div>\n')
out = out.replace('\n\n\n', '\n\n')
open(OUT, 'w', encoding='utf-8').write(out)

print('keyframes:', KEYFRAMES)
print('symbols:', len(SYMBOLS), 'classes:', len(CLASSES))
print('bare js strings left unprefixed:', sorted(set(l for l in leftovers if l in CLASSES)))
print('bytes:', len(out.encode('utf-8')))
