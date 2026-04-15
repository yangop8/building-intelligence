#!/usr/bin/env python3
"""
Build script for Building Intelligence (构建智能)

Generates book.html (Chinese) and book_en.html (English) from source chapter files.

Usage:
    python3 build.py          # Build both books
    python3 build.py zh       # Build Chinese only
    python3 build.py en       # Build English only
    python3 build.py verify   # Verify consistency without rebuilding
"""
import re
import os
import sys

BOOK_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Paper ordering: source IDs → renumbered P01-P26
# ============================================================
PAPER_ORDER_ZH = [
    ("第2章相关 · 系统基础", ["p18", "p19"]),
    ("第3章相关 · 经典模型", ["p01", "p02", "p03", "p04", "p05", "p20", "p21", "p22", "p23"]),
    ("第4章相关 · Transformer与预训练", ["p06", "p07", "p08", "p09"]),
    ("第4章相关 · 效率与推理", ["p10", "p11", "p12", "p13", "p24"]),
    ("第4章相关 · 对齐与应用", ["p14", "p15", "p16", "p17", "p25", "p26"]),
]

PAPER_ORDER_EN = [
    ("Ch 2 Related · Systems", ["p18", "p19"]),
    ("Ch 3 Related · Classic Models", ["p01", "p02", "p03", "p04", "p05", "p20", "p21", "p22", "p23"]),
    ("Ch 4 Related · Transformer & Pretraining", ["p06", "p07", "p08", "p09"]),
    ("Ch 4 Related · Efficiency & Inference", ["p10", "p11", "p12", "p13", "p24"]),
    ("Ch 4 Related · Alignment & Applications", ["p14", "p15", "p16", "p17", "p25", "p26"]),
]

# Flat order for renumbering
RENUM_ORDER = [
    "p18", "p19",
    "p01", "p02", "p03", "p04", "p05", "p20", "p21", "p22", "p23",
    "p06", "p07", "p08", "p09",
    "p10", "p11", "p12", "p13", "p24",
    "p14", "p15", "p16", "p17", "p25", "p26",
]

CHAPTERS_ZH = [
    ("ch0_preface.html", "preface", "序章", "AI工程师知识体系"),
    ("ch1_math_foundations.html", "ch1", "第一章 数学基础", "面向AI工程师的复习手册"),
    ("ch2_systems_software.html", "ch2", "第二章 系统软件", "从CPU到DPDK"),
    ("ch3_ai_model_tech.html", "ch3", "第三章 AI模型技术", "从传统ML到性能工程"),
    ("ch4_llm_tech.html", "ch4", "第四章 LLM技术", "从Transformer到Agent"),
]

CHAPTERS_EN = [
    ("ch0_preface.html", "preface", "Preface", "The Complete AI Engineer's Knowledge Map"),
    ("ch1_math_foundations.html", "ch1", "Chapter 1: Mathematical Foundations", "A Review for AI Engineers"),
    ("ch2_systems_software.html", "ch2", "Chapter 2: Systems Software", "From CPU to DPDK"),
    ("ch3_ai_model_tech.html", "ch3", "Chapter 3: AI Model Technology", "From Traditional ML to Performance Engineering"),
    ("ch4_llm_tech.html", "ch4", "Chapter 4: LLM Technology", "From Transformer to Agent"),
]

CH5_SOURCE_FILES = [
    "ch5_partA_preview.html",
    "ch5_partB_preview.html",
    "ch5_partC_supplement.html",
]

# Known bare-$ formulas containing < that need special handling
BARE_DOLLAR_FIXES = [
    ('($m < n$)', '(<span class="math-i">m &lt; n</span>)'),
    ('($\\lambda < 0$', '(<span class="math-i">\\lambda &lt; 0</span>'),
    ('($k < r$)', '(<span class="math-i">k &lt; r</span>)'),
    ('差距$< 1$', '差距<span class="math-i">&lt; 1</span>'),
    ('(gap $< 1$', '(gap <span class="math-i">&lt; 1</span>'),
    ('(gap $&lt; 1$', '(gap <span class="math-i">&lt; 1</span>'),
    ('$R < C$', '<span class="math-i">R &lt; C</span>'),
    ('$f(a) f(b) < 0$', '<span class="math-i">f(a) f(b) &lt; 0</span>'),
    ('$I < I^*$', '<span class="math-i">I &lt; I^*</span>'),
    ('$m &lt; n$', '<span class="math-i">m &lt; n</span>'),
    ('$\\lambda &lt; 0$', '<span class="math-i">\\lambda &lt; 0</span>'),
    ('$k &lt; r$', '<span class="math-i">k &lt; r</span>'),
    ('$&lt; 1$', '<span class="math-i">&lt; 1</span>'),
    ('$R &lt; C$', '<span class="math-i">R &lt; C</span>'),
    ('$f(a) f(b) &lt; 0$', '<span class="math-i">f(a) f(b) &lt; 0</span>'),
    ('$I &lt; I^*$', '<span class="math-i">I &lt; I^*</span>'),
]

CURRENCY_FIXES_ZH = [
    ('约$5.3M)', '约530万美元)'),
    ('——$560万', '——560万美元'),
    ('仅$200K', '仅20万美元'),
    ('约$5.6M)', '约560万美元)'),
]

CURRENCY_FIXES_EN = [
    ('just $200K', 'just US$200K'),
    ('approximately $5.6M)', 'approximately US$5.6M)'),
    ('(~$5.3M)', '(~US$5.3M)'),
    ('Approximately $5.6M', 'Approximately US$5.6M'),
    ('debated — $5.6M', 'debated — US$5.6M'),
    ('$155M ARR', 'US$155M ARR'),
    ('~$250M)', '~US$250M)'),
    ('$19/month', 'US$19/month'),
]


# ============================================================
# Text processing functions
# ============================================================

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def extract_main(filepath):
    text = read_file(filepath)
    m = re.search(r'<main>(.*?)</main>', text, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_toc_groups(filepath):
    text = read_file(filepath)
    m = re.search(r'<aside class="toc">(.*?)</aside>', text, re.DOTALL)
    if not m:
        return []
    return re.findall(
        r'<div class="group">(.*?)</div>\s*<ol>(.*?)</ol>',
        m.group(1), re.DOTALL
    )


def fix_cross_refs(content):
    for fname in CH5_SOURCE_FILES + [c[0] for c in CHAPTERS_ZH]:
        content = content.replace(fname + '#', '#')
    return content


def escape_code_blocks(content):
    def _esc(m):
        attr, inner = m.group(1), m.group(2)
        # Protect already-escaped entities
        inner = inner.replace('&lt;', '\x00LT')
        inner = inner.replace('&gt;', '\x00GT')
        inner = inner.replace('&amp;', '\x00AMP')
        # Escape raw < and >
        inner = inner.replace('<', '&lt;')
        inner = inner.replace('>', '&gt;')
        # Restore
        inner = inner.replace('\x00LT', '&lt;')
        inner = inner.replace('\x00GT', '&gt;')
        inner = inner.replace('\x00AMP', '&amp;')
        return f'<pre><code{attr}>{inner}</code></pre>'
    return re.sub(r'<pre><code([^>]*)>(.*?)</code></pre>', _esc, content, flags=re.DOTALL)


def convert_math_to_spans(content):
    # Display math in formula divs: $...$ or $$...$$ → <span class="math-d">
    def _conv_display(m):
        inner = m.group(1).strip()
        if inner.startswith('<span class="math-'):
            return m.group(0)
        if inner.startswith('$$') and inner.endswith('$$'):
            return f'<div class="formula"><span class="math-d">{inner[2:-2]}</span></div>'
        if inner.startswith('$') and inner.endswith('$'):
            return f'<div class="formula"><span class="math-d">{inner[1:-1]}</span></div>'
        return m.group(0)
    content = re.sub(r'<div class="formula">(.*?)</div>', _conv_display, content, flags=re.DOTALL)

    # Inline math: $...$ → <span class="math-i">
    skip_pattern = (
        r'(<pre>.*?</pre>|<code>.*?</code>|<script[^>]*>.*?</script>|'
        r'<style>.*?</style>|<span class="math-[di]">.*?</span>|<[^>]+>)'
    )
    parts = re.split(skip_pattern, content, flags=re.DOTALL)
    result = []
    for part in parts:
        if part is None:
            continue
        if part.startswith('<'):
            result.append(part)
            continue
        part = re.sub(
            r'(?<!\$)\$([^$]+?)\$(?!\$)',
            lambda m: f'<span class="math-i">{m.group(1)}</span>',
            part
        )
        result.append(part)
    content = ''.join(result)

    # Fix Unicode symbols inside math spans
    def _fix_unicode(m):
        tag_class, math = m.group(1), m.group(2)
        replacements = [
            ('≈', '\\approx '), ('≤', '\\le '), ('≥', '\\ge '),
            ('×', '\\times '), ('→', '\\to '), ('∈', '\\in '),
            ('∞', '\\infty '),
        ]
        for old, new in replacements:
            math = math.replace(old, new)
        return f'<span class="{tag_class}">{math}</span>'
    content = re.sub(
        r'<span class="(math-[id])">(.*?)</span>',
        _fix_unicode, content, flags=re.DOTALL
    )
    return content


def remove_chinese_english_spaces(content):
    for _ in range(2):
        content = re.sub(
            r'([\u4e00-\u9fff]) ([A-Za-z0-9$\\(\["\'《])',
            r'\1\2', content
        )
        content = re.sub(
            r'([A-Za-z0-9$\\)\].\!\?,"\'>》%]) ([\u4e00-\u9fff])',
            r'\1\2', content
        )
    return content


def fix_bare_dollars(content, is_zh):
    for old, new in BARE_DOLLAR_FIXES:
        content = content.replace(old, new)
    # Also catch $...<..$ patterns that slipped through
    content = re.sub(
        r'\$([^$]*<[^$]*)\$',
        lambda m: f'<span class="math-i">{m.group(1).replace("<", "&lt;")}</span>',
        content
    )
    # Currency
    fixes = CURRENCY_FIXES_ZH if is_zh else CURRENCY_FIXES_EN
    for old, new in fixes:
        content = content.replace(old, new)
    return content


def process_content(content, is_zh=True):
    content = fix_cross_refs(content)
    content = escape_code_blocks(content)
    content = convert_math_to_spans(content)
    if is_zh:
        content = remove_chinese_english_spaces(content)
    content = fix_bare_dollars(content, is_zh)
    return content


def renumber_papers(content):
    """Renumber paper IDs from source order to chapter-based sequential order."""
    old_to_ph = {old: f"__P{i+1:02d}__" for i, old in enumerate(RENUM_ORDER)}
    ph_to_new = {f"__P{i+1:02d}__": f"p{i+1:02d}" for i in range(26)}

    # Phase 1: old → placeholder
    for old_id, ph in old_to_ph.items():
        content = content.replace(f'id="{old_id}"', f'id="{ph}"')
        content = content.replace(f'href="#{old_id}"', f'href="#{ph}"')
        content = content.replace(f'>{old_id.upper()}<', f'>{ph}<')
    # Phase 2: placeholder → new
    for ph, new_id in ph_to_new.items():
        content = content.replace(f'id="{ph}"', f'id="{new_id}"')
        content = content.replace(f'href="#{ph}"', f'href="#{new_id}"')
        content = content.replace(f'>{ph}<', f'>{new_id.upper()}<')
    return content


# ============================================================
# Book builder
# ============================================================

def build_book(lang):
    is_zh = (lang == 'zh')
    src_dir = BOOK_DIR if is_zh else os.path.join(BOOK_DIR, 'en')
    chapters = CHAPTERS_ZH if is_zh else CHAPTERS_EN
    paper_order = PAPER_ORDER_ZH if is_zh else PAPER_ORDER_EN

    # --- Extract chapters ---
    chapter_data = []
    toc_groups_all = []
    for fname, cid, title, subtitle in chapters:
        content = process_content(extract_main(os.path.join(src_dir, fname)), is_zh)
        toc = extract_toc_groups(os.path.join(src_dir, fname))
        chapter_data.append((cid, title, subtitle, content))
        toc_groups_all.append((cid, title, toc))
        print(f"  {fname}: {len(content) // 1024}KB")

    # --- Extract and reorder papers ---
    papers = {}
    for fname in CH5_SOURCE_FILES:
        text = fix_cross_refs(extract_main(os.path.join(src_dir, fname)))
        for pm in re.finditer(r'(<h2 id="(p\d+)">.*?)(?=<h2 id="p\d+"|$)', text, re.DOTALL):
            papers[pm.group(2)] = pm.group(1).strip()
    print(f"  Papers extracted: {len(papers)}")

    ch5_parts = []
    ch5_toc_lines = []
    for label, pids in paper_order:
        ch5_toc_lines.append(
            f'    <li style="margin-top:6px;font-weight:600;font-size:11px;'
            f'color:var(--muted);letter-spacing:0.05em">{label}</li>'
        )
        ch5_parts.append(f'<div class="part-header"><div class="part-label">{label}</div></div>')
        for pid in pids:
            if pid in papers:
                ch5_parts.append(papers[pid])
                tm = re.search(r'<span class="num">(\w+)</span>(.*?)</h2>', papers[pid])
                if tm:
                    ptitle = re.sub(r'<[^>]+>', '', tm.group(2)).strip()[:40]
                    ch5_toc_lines.append(
                        f'    <li><a href="#{pid}"><span class="num">{tm.group(1)}</span>{ptitle}</a></li>'
                    )

    ch5_content = process_content('\n\n'.join(ch5_parts), is_zh)
    ch5_title = "第五章 论文精读" if is_zh else "Chapter 5: Paper Deep Dives"
    ch5_sub = "26篇精选论文" if is_zh else "26 Selected Papers"
    chapter_data.append(("ch5", ch5_title, ch5_sub, ch5_content))

    # --- Build sidebar TOC ---
    toc_lines = []
    for cid, title, groups in toc_groups_all:
        toc_lines.append(
            f'  <div class="group"><a href="#{cid}" '
            f'style="color:inherit;text-decoration:none">{title}</a></div>'
        )
        if groups:
            toc_lines.append('  <ol>')
            for group_label, ol_content in groups:
                toc_lines.append(
                    f'    <li style="margin-top:6px;font-weight:600;font-size:11px;'
                    f'color:var(--muted);letter-spacing:0.05em">{group_label}</li>'
                )
                for item in re.findall(r'<li>(.*?)</li>', ol_content, re.DOTALL):
                    toc_lines.append(f'    <li>{item.strip()}</li>')
            toc_lines.append('  </ol>')

    toc_lines.append(
        f'  <div class="group"><a href="#ch5" '
        f'style="color:inherit;text-decoration:none">{ch5_title}</a></div>'
    )
    toc_lines.append('  <ol>\n' + '\n'.join(ch5_toc_lines) + '\n  </ol>')
    refs_label = "参考文献" if is_zh else "References"
    toc_lines.append(
        f'  <div class="group"><a href="#refs" '
        f'style="color:inherit;text-decoration:none">{refs_label}</a></div>'
    )

    # --- Build body sections ---
    body_parts = []
    for cid, title, subtitle, content in chapter_data:
        body_parts.append(
            f'<section id="{cid}" class="chapter">\n'
            f'<div class="chapter-divider">\n'
            f'  <div class="chapter-divider-line"></div>\n'
            f'  <div class="chapter-divider-label">{title}</div>\n'
            f'  <div class="chapter-divider-sub">{subtitle}</div>\n'
            f'</div>\n'
            f'{content}\n'
            f'</section>'
        )

    # --- Apply paper renumbering ---
    full_body = renumber_papers('\n\n'.join(body_parts))
    toc_html = renumber_papers('\n'.join(toc_lines))

    return toc_html, full_body


def assemble_html(lang, toc_html, body_html):
    """Assemble final HTML using CSS/cover/refs from existing merged book."""
    is_zh = (lang == 'zh')
    outfile = 'book.html' if is_zh else 'book_en.html'
    existing_path = os.path.join(BOOK_DIR, outfile)

    # Read existing file for CSS, cover, and refs
    existing = read_file(existing_path)

    css_m = re.search(r'<style>(.*?)</style>', existing, re.DOTALL)
    css = css_m.group(1) if css_m else ""

    cover_m = re.search(
        r'(<!-- .*?COVER.*?-->.*?</div>\s*</div>\s*</div>)',
        existing, re.DOTALL
    )
    cover = cover_m.group(1) if cover_m else "<!-- COVER MISSING -->"

    refs_m = re.search(r'(<section id="refs".*?</section>)', existing, re.DOTALL)
    refs = refs_m.group(1) if refs_m else "<!-- REFS MISSING -->"

    html_lang = 'zh-CN' if is_zh else 'en'
    title = '构建智能 — AI工程师的完整知识体系' if is_zh else "Building Intelligence — The Complete AI Engineer's Knowledge Map"
    book_title = '构建智能' if is_zh else 'Building Intelligence'
    book_sub = 'AI工程师的完整知识体系' if is_zh else "The Complete AI Engineer's Knowledge Map"

    html = f'''<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/rust.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<style>{css}</style>
</head>
<body>

<aside class="toc">
  <div class="book-title">{book_title}</div>
  <div class="book-sub">{book_sub}</div>
{toc_html}
</aside>

<main>

{cover}

{body_html}

{refs}

</main>

<button class="back-top" id="backTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" title="↑">↑</button>

<script>
  hljs.highlightAll();
  if (typeof mermaid !== 'undefined') {{ mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }}); }}
  document.getElementById('backTop').style.display = 'none';
  window.addEventListener('scroll', function() {{
    document.getElementById('backTop').style.display = window.scrollY > 800 ? 'flex' : 'none';
  }});
</script>
<script>
  document.addEventListener("DOMContentLoaded", function() {{
    document.querySelectorAll('.math-d').forEach(function(el) {{
      katex.render(el.textContent, el, {{ displayMode: true, throwOnError: false }});
    }});
    document.querySelectorAll('.math-i').forEach(function(el) {{
      katex.render(el.textContent, el, {{ displayMode: false, throwOnError: false }});
    }});
  }});
</script>

</body>
</html>'''

    write_file(existing_path, html)
    return html


def count_bare_dollars(html):
    parts = re.split(r'<[^>]+>', html)
    return sum(p.replace('US$', '').count('$') for p in parts)


def verify(html, label):
    papers = len(re.findall(r'<h2 id="p\d+">', html))
    new_sections = len(re.findall(r'id="s4-11-[34]"', html))
    bare = count_bare_dollars(html)
    has_refs = 'id="refs"' in html
    has_ch5 = 'id="ch5"' in html
    size_kb = len(html.encode('utf-8')) // 1024

    print(f"  {label}: {size_kb}KB | {papers} papers | bare $: {bare} | "
          f"4.11.3+4: {new_sections} | ch5: {has_ch5} | refs: {has_refs}")

    if bare > 0:
        print(f"  WARNING: {bare} bare $ signs remain!")
    if papers != 26:
        print(f"  WARNING: Expected 26 papers, found {papers}")
    return bare == 0 and papers == 26 and has_refs and has_ch5


# ============================================================
# Main
# ============================================================

def main():
    args = sys.argv[1:]
    target = args[0] if args else 'all'

    if target == 'verify':
        print("=== Verifying existing books ===")
        ok = True
        for outfile in ['book.html', 'book_en.html']:
            html = read_file(os.path.join(BOOK_DIR, outfile))
            if not verify(html, outfile):
                ok = False
        sys.exit(0 if ok else 1)

    build_zh = target in ('all', 'zh')
    build_en = target in ('all', 'en')

    if build_zh:
        print("=== Building Chinese book.html ===")
        toc, body = build_book('zh')
        html = assemble_html('zh', toc, body)
        verify(html, 'book.html')

    if build_en:
        print("\n=== Building English book_en.html ===")
        toc, body = build_book('en')
        html = assemble_html('en', toc, body)
        verify(html, 'book_en.html')

    print("\nDone!")


if __name__ == '__main__':
    main()
