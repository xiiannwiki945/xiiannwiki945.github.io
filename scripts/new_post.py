#!/usr/bin/env python3
"""半山笔记 · 发文助手

生成一篇新文章的 HTML，并自动同步 index.html / archive.html / search-index.js / feed.xml。
用法示例：

    python3 scripts/new_post.py --title "文章标题" --slug my-post \
        --tags Hugo,工作流 --excerpt "一句话摘要"

可选参数：--date 2026-11-15  --minutes 3
生成后：编辑 <slug>.html 填正文（prose 区块），search-index.js 里把 body 换成正文纯文本，
然后 git push 即可。再次运行同 slug 会拒绝，避免覆盖。
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://xiiannwiki945.github.io"

HEAD = """<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — 半山笔记</title>
<meta name="description" content="{excerpt}">
<link rel="stylesheet" href="assets/style.css">
<link rel="canonical" href="{domain}/{slug}.html">
<meta property="og:type" content="article">
<meta property="og:site_name" content="半山笔记">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{excerpt}">
<meta property="og:url" content="{domain}/{slug}.html">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="半山笔记" href="feed.xml">
<script>(function(){{try{{var t=localStorage.getItem("banshan-theme");if(t!=="dark"&&t!=="light"){{t=window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";}}document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}}})();</script>
</head>
<body>
"""

HEADER = """<header class="site-header">
  <div class="wrap site-header__inner">
    <a class="brand serif" href="index.html"><span class="brand-mark" aria-hidden="true"></span>半山笔记</a>
    <nav class="nav" aria-label="主导航">
      <a href="index.html" class="is-accent">文章</a>
      <a href="tags.html">标签</a>
      <a href="archive.html">归档</a>
      <a href="about.html">关于</a>
    </nav>
    <div class="nav-tools">
      <a class="icon-btn" href="search.html" aria-label="搜索">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m16.5 16.5 4 4"></path></svg>
      </a>
      <button class="icon-btn" type="button" data-theme-toggle aria-label="切换主题">
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5Z"></path></svg>
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"></circle><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"></path></svg>
      </button>
    </div>
  </div>
</header>
"""

FOOTER = """<footer class="site-footer">
  <div class="wrap site-footer__inner">
    <p>© 2026 半山笔记 · xiiannwiki945.github.io</p>
    <div class="footer-links">
      <a href="feed.xml">RSS</a>
      <a href="https://github.com/xiiannwiki945" rel="noopener">GitHub</a>
      <a href="search.html">搜索</a>
    </div>
  </div>
</footer>

<script src="assets/app.js" defer></script>
</body>
</html>
"""


def tags_spans(tags):
    return "\n            ".join("<span>#{}</span>".format(t) for t in tags)


def build_post(title, slug, date, tags, minutes, excerpt):
    meta_tags = "\n          ".join('<a href="tags.html">#{}</a>'.format(t) for t in tags)
    body = HEAD.format(title=title, excerpt=excerpt, domain=DOMAIN, slug=slug) + HEADER + """<main class="wrap">
  <div class="post-layout">
    <article class="post">
      <header class="post-header">
        <h1 class="serif">{title}</h1>
        <div class="meta-line">
          <time datetime="{date}">{date}</time>
          <span class="meta-sep">·</span>
          <span>{minutes} 分钟</span>
          <span class="meta-sep">·</span>
          {meta_tags}
        </div>
      </header>

      <div class="prose">
        <!-- TODO: 在这里写正文。小节标题用 <h2 id="sec-1">小节标题</h2>，
             写完后把右侧 toc 里的 <a href="#sec-1"> 补上对应条目。 -->
        <p>（正文从这里开始……）</p>
      </div>

      <div class="post-foot">
        <a href="index.html">← 返回文章列表</a>
      </div>
    </article>

    <aside class="toc" aria-label="目录">
      <h2 class="toc__title">目录</h2>
      <!-- 正文有 h2 小节后，在这里加 <a href="#sec-1">小节标题</a> -->
    </aside>
  </div>
</main>

""".format(title=title, date=date, minutes=minutes, meta_tags=meta_tags) + FOOTER
    return body


def insert_index(title, slug, date, tags, minutes, excerpt):
    p = ROOT / "index.html"
    s = p.read_text(encoding="utf-8")
    if slug + ".html" in s:
        sys.exit("index.html 里已有 {}，请勿重复运行".format(slug))
    y, m, d = date.split("-")
    block = """      <article class="post-item">
        <div class="post-date"><span>{md}</span><span class="year">{y}</span></div>
        <div>
          <h2><a href="{slug}.html">{title}</a></h2>
          <p class="excerpt">{excerpt}</p>
          <div class="meta-line">
            <span>{minutes} 分钟</span>
            <span class="meta-sep">·</span>
            {tags}
          </div>
        </div>
      </article>

""".format(md="{}-{}".format(m, d), y=y, slug=slug, title=title,
           excerpt=excerpt, minutes=minutes, tags=tags_spans(tags))
    marker = '<section class="post-list" aria-label="文章列表">\n'
    if marker not in s:
        sys.exit("index.html 中找不到文章列表标记")
    s = s.replace(marker, marker + block, 1)
    p.write_text(s, encoding="utf-8")


def insert_archive(title, slug, date, tags):
    p = ROOT / "archive.html"
    s = p.read_text(encoding="utf-8")
    y, m, d = date.split("-")
    item = """      <div class="archive-item">
        <time datetime="{date}">{md}</time>
        <a href="{slug}.html">{title}</a>
        <span class="tag-mini">{tags}</span>
      </div>
""".format(date=date, md="{}-{}".format(m, d), slug=slug, title=title,
           tags=" ".join("#" + t for t in tags))
    year_head = '<h2 class="archive-year serif">{}</h2>'.format(y)
    if year_head in s:
        marker = '<div class="archive-list">\n'
        first = s.find(marker)
        # 当前实现每年只有一个列表，直接插到第一个列表的最前面
        s = s[: first + len(marker)] + item + s[first + len(marker):]
    else:
        block = "    {}\n    <div class=\"archive-list\">\n{}    </div>\n\n".format(year_head, item)
        anchor = '    <h2 class="archive-year serif">'
        pos = s.find(anchor)
        if pos == -1:
            sys.exit("archive.html 中找不到年份标记")
        s = s[:pos] + block + s[pos:]
    total = len(re.findall(r'class="archive-item"', s))
    s = re.sub(r"全部 \d+ 篇", "全部 {} 篇".format(total), s)
    p.write_text(s, encoding="utf-8")


def insert_search(title, slug, date, tags, excerpt):
    p = ROOT / "assets" / "search-index.js"
    s = p.read_text(encoding="utf-8")
    entry = """  {{
    title: {title},
    url: "{slug}.html",
    date: "{date}",
    tags: {tags},
    body:
      "{excerpt} （TODO: 发文后把这段换成正文纯文本，搜索摘要取自这里）"
  }},
""".format(title=json.dumps(title, ensure_ascii=False), slug=slug, date=date,
           tags=json.dumps(tags, ensure_ascii=False), excerpt=excerpt.replace('"', '\\"'))
    marker = "window.POSTS = [\n"
    if marker not in s:
        sys.exit("search-index.js 中找不到 window.POSTS 标记")
    s = s.replace(marker, marker + entry, 1)
    p.write_text(s, encoding="utf-8")


def insert_feed(title, slug, date, excerpt):
    p = ROOT / "feed.xml"
    s = p.read_text(encoding="utf-8")
    dt = datetime.strptime(date, "%Y-%m-%d").replace(
        hour=9, tzinfo=timezone(timedelta(hours=8)))
    rfc = dt.strftime("%a, %d %b %Y %H:%M:%S %z")
    rfc = rfc[:-2] + ":" + rfc[-2:]
    now = datetime.now(timezone(timedelta(hours=8))).strftime(
        "%a, %d %b %Y %H:%M:%S %z")
    now = now[:-2] + ":" + now[-2:]
    item = """    <item>
      <title>{title}</title>
      <link>{domain}/{slug}.html</link>
      <guid>{domain}/{slug}.html</guid>
      <pubDate>{rfc}</pubDate>
      <description>{excerpt}</description>
    </item>
""".format(title=title, domain=DOMAIN, slug=slug, rfc=rfc, excerpt=excerpt)
    anchor = 'rel="self" type="application/rss+xml" />\n'
    if anchor not in s:
        sys.exit("feed.xml 中找不到 atom:link 标记")
    s = s.replace(anchor, anchor + item, 1)
    s = re.sub(r"<lastBuildDate>.*?</lastBuildDate>",
               "<lastBuildDate>{}</lastBuildDate>".format(now), s, count=1)
    p.write_text(s, encoding="utf-8")


def main():
    today = time.strftime("%Y-%m-%d")
    ap = argparse.ArgumentParser(description="半山笔记发文助手")
    ap.add_argument("--title", required=True, help="文章标题")
    ap.add_argument("--slug", required=True, help="文件名（英文短横线，如 my-post）")
    ap.add_argument("--date", default=today, help="日期 YYYY-MM-DD，默认今天")
    ap.add_argument("--tags", default="", help="逗号分隔，如 Hugo,工作流")
    ap.add_argument("--minutes", default="3", help="预计阅读分钟数")
    ap.add_argument("--excerpt", required=True, help="列表页摘要（一两句话）")
    args = ap.parse_args()

    slug = args.slug.strip()
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        sys.exit("slug 只能是小写字母、数字和短横线，例如 my-post")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    if not tags:
        sys.exit("至少给一个标签：--tags Hugo,随笔")
    post = ROOT / (slug + ".html")
    if post.exists():
        sys.exit("{} 已存在，换一个 slug".format(post.name))

    post.write_text(build_post(args.title, slug, args.date, tags,
                               args.minutes, args.excerpt), encoding="utf-8")
    insert_index(args.title, slug, args.date, tags, args.minutes, args.excerpt)
    insert_archive(args.title, slug, args.date, tags)
    insert_search(args.title, slug, args.date, tags, args.excerpt)
    insert_feed(args.title, slug, args.date, args.excerpt)

    print("已生成：")
    print("  - {}.html          ← 打开填正文（prose 区块）和右侧目录".format(slug))
    print("  - index.html / archive.html / feed.xml / assets/search-index.js 已同步")
    print("下一步：编辑正文与索引 body，然后 git add -A && git commit -m 'post: {}' && git push".format(args.title))


if __name__ == "__main__":
    main()
