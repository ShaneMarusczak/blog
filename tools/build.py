#!/usr/bin/env python3
"""Tiny static-site generator for the blog.

Sources you edit:
  posts.json                  per-post front matter (file, title, date,
                              category, description, keywords)
  content/posts/<file>        the article body of each post (the inner HTML
                              of <article>, minus the <h1> and meta line —
                              those are generated from posts.json)
  templates/post.html         the shell wrapped around every post
  templates/index.html        the landing-page shell
  partials/masthead.html      the banner shared by every page
  partials/footer.html        the footer shared by every page

Files this generates (do NOT hand-edit; commit the output so GitHub Pages
serves it):
  index.html
  posts/<file>
  feed.xml
  sitemap.xml
  robots.txt

Usage:
  python3 tools/build.py

CI rebuilds and fails if any generated file differs from what's committed,
so a stale page can't ship.
"""

import json
import pathlib
import re
from xml.sax.saxutils import escape as xml_escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://shanemarusczak.github.io/blog"
TITLE = "shane's blog"
SUBTITLE = "Notes on software, tools, and building things."
AUTHOR = "Shane Marusczak"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def date_display(iso):
    year, month, day = iso.split("-")
    return f"{MONTHS[int(month) - 1]} {int(day)}, {year}"


def read(rel):
    return (ROOT / rel).read_text()


def write(rel, text):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)


def attr(value):
    """Escape a string for HTML text or a double-quoted attribute.

    Apostrophes are left alone to match the hand-written style already in
    the posts (they're safe inside double quotes)."""
    return (value.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;"))


def fill(template, **tokens):
    """Replace every {{token}} in a single left-to-right pass, so an inserted
    value that happens to contain another token's text is never re-substituted."""
    pattern = re.compile(r"\{\{(" + "|".join(map(re.escape, tokens)) + r")\}\}")
    return pattern.sub(lambda m: tokens[m.group(1)], template)


def masthead(is_index):
    if is_index:
        wordmark = ('<h1 class="wordmark">'
                    '<a href="./" aria-current="page">shane\'s blog</a></h1>')
        prefix = ""
    else:
        wordmark = '<a class="wordmark" href="../">shane\'s blog</a>'
        prefix = "../"
    return fill(read("partials/masthead.html"),
                wordmark=wordmark, prefix=prefix).rstrip("\n")


def site_footer(is_index):
    return fill(read("partials/footer.html"),
                home="./" if is_index else "../").rstrip("\n")


def build_pages(posts):
    post_tpl = read("templates/post.html")
    for post in posts:
        url = f"{SITE}/posts/{post['file']}"
        body = read(f"content/posts/{post['file']}").strip("\n")
        page = fill(
            post_tpl,
            title=attr(post["title"]),
            description=attr(post["description"]),
            keywords=attr(post.get("keywords", "")),
            date=post["date"],
            category=attr(post["category"]),
            url=url,
            masthead=masthead(False),
            content=body,
            footer=site_footer(False),
        )
        write(f"posts/{post['file']}", page)

    index = fill(read("templates/index.html"),
                 site=SITE,
                 masthead=masthead(True),
                 footer=site_footer(True),
                 postlist=post_list(posts))
    write("index.html", index)


def post_list(posts):
    """Render the landing-page cards as static HTML (no runtime JS)."""
    items = []
    for post in posts:
        meta = (f'<time datetime="{post["date"]}">{date_display(post["date"])}</time>'
                f'<span class="dot">&middot;</span>'
                f'<span class="category">{attr(post["category"])}</span>')
        item = (
            f'      <li class="post-item"><a href="posts/{post["file"]}">\n'
            f'        <h2 class="post-title">{attr(post["title"])}</h2>\n'
            f'        <div class="post-meta">{meta}</div>\n'
            f'        <div class="post-description">{attr(post["description"])}</div>\n'
            f'      </a></li>'
        )
        items.append(item)
    return "\n".join(items)


def build_feed(posts):
    updated = f"{posts[0]['date']}T00:00:00Z" if posts else "1970-01-01T00:00:00Z"
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{xml_escape(TITLE)}</title>",
        f"  <subtitle>{xml_escape(SUBTITLE)}</subtitle>",
        f'  <link rel="self" type="application/atom+xml" href="{SITE}/feed.xml"/>',
        f'  <link rel="alternate" type="text/html" href="{SITE}/"/>',
        f"  <id>{SITE}/</id>",
        f"  <updated>{updated}</updated>",
        f"  <author><name>{xml_escape(AUTHOR)}</name></author>",
    ]
    for post in posts:
        url = f"{SITE}/posts/{post['file']}"
        lines += [
            "  <entry>",
            f"    <title>{xml_escape(post['title'])}</title>",
            f'    <link rel="alternate" type="text/html" href="{url}"/>',
            f"    <id>{url}</id>",
            f"    <updated>{post['date']}T00:00:00Z</updated>",
            f"    <published>{post['date']}T00:00:00Z</published>",
            f'    <category term="{xml_escape(post["category"])}"/>',
            f"    <summary>{xml_escape(post['description'])}</summary>",
            "  </entry>",
        ]
    lines.append("</feed>")
    write("feed.xml", "\n".join(lines) + "\n")


def build_sitemap(posts):
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f"  <url><loc>{SITE}/</loc></url>",
    ]
    for post in posts:
        lines.append(f"  <url><loc>{SITE}/posts/{post['file']}</loc>"
                     f"<lastmod>{post['date']}</lastmod></url>")
    lines.append("</urlset>")
    write("sitemap.xml", "\n".join(lines) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")


def prune_orphans(posts):
    """Delete generated posts/*.html that no longer have a posts.json entry,
    so a renamed or removed post can't linger on the live site. Redirect
    stubs (files with a meta refresh) are left in place on purpose."""
    keep = {post["file"] for post in posts}
    for path in (ROOT / "posts").glob("*.html"):
        if path.name in keep:
            continue
        if 'http-equiv="refresh"' in path.read_text():
            continue
        path.unlink()
        print(f"pruned stale posts/{path.name}")


def main():
    posts = json.loads(read("posts.json"))
    for post in posts:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", post.get("date", "")):
            raise SystemExit(f"build: {post.get('file', '?')} has a malformed "
                             f"date {post.get('date')!r} (expected YYYY-MM-DD)")
    posts.sort(key=lambda p: p["date"], reverse=True)
    build_pages(posts)
    prune_orphans(posts)
    build_feed(posts)
    build_sitemap(posts)
    print(f"built index + {len(posts)} posts, feed.xml, sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
