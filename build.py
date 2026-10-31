#!/usr/bin/env python3
"""Build static blog from Markdown posts in _posts/.

Usage: python3 build.py
Output: _site/index.html and _site/posts/<slug>.html, plus copied assets.
New post workflow (GitHub): add a file _posts/YYYY-MM-DD-slug.md with
front matter (title, date, category, excerpt, optional image/minutes),
commit, and the GitHub Action in .github/workflows/deploy.yml rebuilds.
"""
import pathlib, re, shutil, html
import yaml
import markdown

ROOT = pathlib.Path(__file__).parent
POSTS_DIR = ROOT / "_posts"
OUT = ROOT / "_site"

def parse_post(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError(f"{path} missing front matter")
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2).strip()
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    date = str(meta.get("date", path.stem[:10]))
    # yaml may parse date as date object
    try:
        date = meta["date"].isoformat() if hasattr(meta.get("date"), "isoformat") else date
    except Exception:
        pass
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "date": date,
        "category": meta.get("category", "生活"),
        "excerpt": meta.get("excerpt", ""),
        "image": meta.get("image", ""),
        "minutes": meta.get("minutes", ""),
        "body_html": markdown.markdown(body, extensions=["extra", "sane_lists"]),
        "cat_code": "code" if str(meta.get("category", "")).strip() == "编程" else "life",
    }

def fmt_date(d):
    # 2026-10-31 -> 2026 年 10 月 31 日
    try:
        y, mo, da = d.split("-")
        return f"{int(y)} 年 {int(mo)} 月 {int(da)} 日"
    except Exception:
        return d

def header():
    return """<header class="topbar"><div class="wrap topbar-inner">
<a class="wordmark" href="/">代码<em>与</em>日子</a>
<nav class="topnav" aria-label="栏目"><a href="/">全部</a><a href="/?cat=code">编程</a><a href="/?cat=life">生活</a><a href="/#columns">两个栏目</a><a href="/#archive">归档</a></nav>
</div></header>"""

def footer():
    return """<footer><div class="wrap"><span>代码与日子 · 写编程，也写生活</span><span>2026</span></div></footer>"""

def page(title, body, desc=""):
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta name="color-scheme" content="light dark" />
<meta name="description" content="{html.escape(desc)}" />
<title>{html.escape(title)} · 代码与日子</title>
<link rel="stylesheet" href="/assets/style.css" />
</head><body>{header()}<main><div class="wrap">{body}</div></main>{footer()}</body></html>
"""

def main():
    posts = sorted((parse_post(p) for p in POSTS_DIR.glob("*.md")), key=lambda x: x["date"], reverse=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "posts").mkdir(parents=True)
    shutil.copytree(ROOT / "assets", OUT / "assets")

    # Index
    cards = []
    for p in posts:
        img = f'<span class="thumb"><img src="{p["image"]}" alt="" loading="lazy" /></span>' if p["image"] else ""
        cards.append(f"""<article class="card" data-cat="{p['cat_code']}">
<a href="/posts/{p['slug']}.html">{img}<span class="kicker">{p['category']}</span>
<h3>{html.escape(p['title'])}</h3><p>{html.escape(p['excerpt'])}</p>
<span class="meta">{fmt_date(p['date'])} · {p['minutes']}</span></a></article>""")
    archive_rows = "".join(
        f'<a class="arch-row" href="/posts/{p["slug"]}.html"><span class="arch-date">{p["date"]}</span><span class="arch-title">{html.escape(p["title"])}</span><span class="arch-cat">{p["category"]}</span><span class="arch-min">{p["minutes"]}</span></a>'
        for p in posts
    )
    n_code = sum(1 for p in posts if p["cat_code"] == "code")
    n_life = len(posts) - n_code
    index_body = f"""
<section class="hero"><div><h1>写代码，<br />也好好<span class="accent">生活</span>。</h1>
<p class="lede">这里记两件事：一是编程里想明白的东西——怎么写出读得懂的代码、怎么把 bug 一步步找出来；二是生活里慢下来的时刻——散步、做饭，和一个不被手机打断的清晨。</p>
<div class="hero-actions"><a class="btn primary" href="#articles">开始阅读</a><a class="btn" href="#about">写在前面</a></div></div>
<figure><img src="/assets/images/desk.webp" alt="窗边的书桌" /><figcaption><span>窗边的书桌，写东西的地方</span><span>插画</span></figcaption></figure></section>
<div class="toolbar" id="articles"><h2>最新文章</h2>
<div class="pills"><button class="pill" data-filter="all">全部</button><button class="pill" data-filter="code">编程</button><button class="pill" data-filter="life">生活</button></div>
<label class="search"><input type="search" id="searchInput" placeholder="搜标题或内容…" /></label>
<p class="count" id="countText">共 {len(posts)} 篇文章 · {n_code} 篇编程，{n_life} 篇生活</p></div>
<div class="grid" id="grid">{''.join(cards)}</div>
<p class="empty" id="emptyText" hidden>没有找到符合条件的文章，换个关键词试试。</p>
<section class="block" id="columns"><h2>两个栏目，各写各的</h2>
<p class="block-intro">编程写给未来的自己，生活写给现在的自己。两个栏目没有高下，写代码累了就去散步，散步回来再把代码写清楚。</p>
<div class="columns"><div class="col"><h3><span>01</span> · 编程</h3><p>不追新工具，先把基本功写扎实。每一篇都带一个能直接用的做法。</p></div>
<div class="col"><h3><span>02</span> · 生活</h3><p>不写宏大叙事，只写具体的日子：一条路、一顿饭、一个清晨。</p></div></div></section>
<section class="block" id="archive"><h2>归档</h2><p class="block-intro">按时间倒序，点任意一行打开全文。</p><div id="archiveList">{archive_rows}</div></section>
<section class="block" id="about"><div class="about"><h2>写在前面</h2><div>
<p>这个博客从六篇开篇的文章开始：<strong>三篇编程，三篇生活</strong>。它们不是定稿，是第一版——写出来，放在这里，以后一篇篇替换、补充，博客就长成了自己的样子。</p>
<p>写博客的规矩只有一条：<strong>写具体的东西</strong>。不写“要努力”这种空话，写今天改了哪一行代码、走了哪条路、做了哪道菜。具体，才经得起回看。</p>
</div></div></section>
<script>
const pills=document.querySelectorAll('.pill');let cat='all';
function apply(){{const q=(document.getElementById('searchInput').value||'').toLowerCase();let n=0;
document.querySelectorAll('#grid .card').forEach(c=>{{const ok=(cat==='all'||c.dataset.cat===cat)&&c.textContent.toLowerCase().includes(q);c.style.display=ok?'':'none';if(ok)n++;}});
document.getElementById('emptyText').hidden=n>0;}}
pills.forEach(b=>b.onclick=()=>{{cat=b.dataset.filter;apply();}});
document.getElementById('searchInput').oninput=apply;
const u=new URL(location.href);if(u.searchParams.get('cat')){{cat=u.searchParams.get('cat');apply();}}
</script>
"""
    (OUT / "index.html").write_text(page("写编程，也写生活", index_body, "代码与日子——一个写编程也写生活的个人博客。"), encoding="utf-8")

    # Post pages
    for i, p in enumerate(posts):
        prev_link = ""
        next_link = ""
        if i > 0:
            q = posts[i-1]
            prev_link = f'<a href="/posts/{q["slug"]}.html"><small>← 更新的一篇</small><strong>{html.escape(q["title"])}</strong></a>'
        if i + 1 < len(posts):
            q = posts[i+1]
            next_link = f'<a href="/posts/{q["slug"]}.html"><small>更早的一篇 →</small><strong>{html.escape(q["title"])}</strong></a>'
        img = f'<figure><img src="{p["image"]}" alt="" /></figure>' if p["image"] else ""
        body = f"""<div class="reader-bar"><div class="wrap"><a class="back" href="/">← 返回首页</a><span class="crumb">{p['category']}</span></div></div>
<article class="article"><span class="kicker">{p['category']}</span><h1>{html.escape(p['title'])}</h1>
<p class="meta">{fmt_date(p['date'])} · {p['minutes']}</p>{img}{p['body_html']}<p class="endmark">◆ ◆ ◆</p></article>
<nav class="prevnext">{prev_link}{next_link}</nav>"""
        (OUT / "posts" / f"{p['slug']}.html").write_text(page(p["title"], body, p["excerpt"]), encoding="utf-8")
    print(f"Built {len(posts)} posts -> {OUT}")

if __name__ == "__main__":
    main()
