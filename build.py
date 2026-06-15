#!/usr/bin/env python3
"""Build Markdown posts into styled HTML pages and refresh Writing indexes.
Also processes project notes and injects them into project detail pages.

Usage:
    uv run build.py

Reads:
  - content/musings/*.md  and  content/learning/*.md  → full article pages
  - content/projects/<project>/notes.md  → injects into projects/<project>/index.html

Writes:
  - musings/<slug>.html   and  learning/<slug>.html
  - refreshes post listings in musings/index.html & learning/index.html
  - injects project notes into project detail pages

Writing posts start with frontmatter:

    ---
    title: My Post Title
    date: 2026-06-21
    summary: One-line preview shown on the Writing index.
    ---

    # Body in Markdown...

Project notes are free-form Markdown with sections marked by ## headings:

    ## What I built
    Your content here...

    ## What I learned
    Your content here...
"""
from __future__ import annotations

import html
import sys
from pathlib import Path
from string import Template

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"

# Each section: where drafts live, where pages are written, and labels.
SECTIONS = {
    "musings": {"label": "Musings", "back": "Back to Musings"},
    "learning": {"label": "Learning Log", "back": "Back to Learning Log"},
}

GITHUB_ICON = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 '
    '0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 '
    '1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 '
    '0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 '
    '1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 '
    '0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.745 0 .268.18.58.688.482A10.019 '
    '10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>'
)

# Article page template. Posts live one level deep (e.g. musings/foo.html),
# so every site path is prefixed with ../  . $-placeholders are filled per post;
# CSS braces are left untouched by string.Template.
PAGE = Template(
    """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>$title_attr — Andres Gonzalez</title>
  <meta name="description" content="$summary_attr"/>
  <link rel="stylesheet" href="../style.css"/>
  <style>
    .article-section { min-height: calc(100vh - 56px); padding: 5rem 0 4rem; }
    .article {
      position: relative; overflow: hidden;
      background: var(--glass-bg-light);
      backdrop-filter: var(--glass-blur-light);
      -webkit-backdrop-filter: var(--glass-blur-light);
      border: 1px solid var(--glass-border-light);
      border-radius: var(--radius);
      box-shadow: var(--glass-shadow);
      padding: 2.5rem 2.75rem; margin-top: 2rem; max-width: 760px;
    }
    .article::before {
      content: ''; position: absolute; inset: 0; pointer-events: none; border-radius: inherit;
      background: radial-gradient(ellipse at 18% 0%, rgba(255,255,255,0.5) 0%, transparent 52%);
    }
    .article > * { position: relative; z-index: 1; }
    .article h2 { font-size: 1.15rem; font-weight: 700; color: var(--text); margin: 2rem 0 0.85rem; }
    .article h3 { font-size: 1rem; font-weight: 700; color: var(--text); margin: 1.5rem 0 0.6rem; }
    .article p { font-size: 0.95rem; line-height: 1.75; color: var(--text); margin-bottom: 1rem; }
    .article ol, .article ul { margin: 0 0 1rem 1.25rem; display: flex; flex-direction: column; gap: 0.5rem; }
    .article li { font-size: 0.95rem; line-height: 1.7; color: var(--text); }
    .article a { color: var(--accent-dark); text-decoration: none; border-bottom: 1px solid rgba(0,113,227,0.3); transition: border-color 0.2s; }
    .article a:hover { border-bottom-color: var(--accent-dark); }
    .article code { font-family: var(--mono); font-size: 0.82rem; background: rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.08); border-radius: 5px; padding: 0.1rem 0.4rem; color: var(--text); }
    .article pre { background: #0c1322; border: 1px solid rgba(255,255,255,0.08); border-radius: var(--radius); padding: 1.25rem 1.4rem; overflow-x: auto; margin: 0 0 1.25rem; box-shadow: 0 8px 24px rgba(0,0,0,0.18); }
    .article pre code { background: none; border: none; padding: 0; color: #c8d4e6; font-size: 0.82rem; line-height: 1.6; }
    .article blockquote { border-left: 3px solid var(--accent-dark); margin: 0 0 1rem; padding: 0.25rem 0 0.25rem 1rem; color: var(--muted); }
    .article-back { display: inline-block; margin-top: 1.75rem; font-size: 0.88rem; color: var(--muted); text-decoration: none; border: none; }
    .article-back:hover { color: var(--accent-dark); }
    .article-meta { font-size: 0.78rem; color: var(--muted); font-family: var(--mono); margin-top: 0.5rem; }
  </style>
</head>
<body>

  <nav id="nav">
    <a href="../index.html" class="nav-brand">Andres Gonzalez</a>
    <ul class="nav-links">
      <li class="hide-mobile"><a href="../index.html#work" data-tab-target="experience">Experience</a></li>
      <li class="hide-mobile"><a href="../index.html#work" data-tab-target="research">Research</a></li>
      <li class="hide-mobile"><a href="../writing/index.html" style="color:var(--accent-dark); font-weight:600;">Writing</a></li>
      <li>
        <a href="https://github.com/Zappandy" class="nav-icon" target="_blank" rel="noopener" aria-label="GitHub">$github_icon</a>
      </li>
    </ul>
  </nav>

  <section class="article-section" style="background: radial-gradient(ellipse at 75% 15%, rgba(99,179,237,0.2) 0%, transparent 50%), linear-gradient(135deg, #dfeeff 0%, #ead6ff 100%);">
    <div class="container">
      <p class="section-label">$breadcrumb</p>
      <h1 class="section-title">$title</h1>
      <p class="article-meta">$date</p>

      <article class="article">
$body
        <a href="index.html" class="article-back">← $back</a>
      </article>
    </div>
  </section>

  <footer>
    <div class="container footer-inner">
      <span class="footer-copy">&#169; 2026 Andres Gonzalez</span>
      <div class="footer-links">
        <a href="https://github.com/Zappandy" target="_blank" rel="noopener">GitHub</a>
        <a href="https://www.linkedin.com/in/andres-gonzalez-gongora-4b428613b/">LinkedIn</a>
        <a href="mailto:nanoandres24@hotmail.com">Email</a>
      </div>
    </div>
  </footer>

  <script>
    const nav = document.getElementById('nav');
    window.addEventListener('scroll', () => { nav.classList.toggle('scrolled', window.scrollY > 10); });
  </script>

</body>
</html>
"""
)

START, END = "<!-- POSTS:START -->", "<!-- POSTS:END -->"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a `--- key: value --- body` document into (meta, body)."""
    if not text.startswith("---"):
        raise ValueError("missing frontmatter (file must start with '---')")
    _, fm, body = text.split("---", 2)
    meta: dict[str, str] = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip().lower()] = val.strip()
    return meta, body.strip()


def collect(section: str) -> list[dict]:
    """Read every post in a section, newest first."""
    src_dir = CONTENT / section
    posts = []
    if not src_dir.exists():
        return posts
    for md_path in sorted(src_dir.glob("*.md")):
        meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
        missing = {"title", "date"} - meta.keys()
        if missing:
            raise ValueError(f"{md_path}: missing frontmatter key(s): {', '.join(sorted(missing))}")
        posts.append(
            {
                "slug": md_path.stem,
                "title": meta["title"],
                "date": meta["date"],
                "summary": meta.get("summary", ""),
                "body_md": body,
            }
        )
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def write_page(section: str, post: dict) -> Path:
    info = SECTIONS[section]
    title_esc = html.escape(post["title"])
    summary_esc = html.escape(post["summary"], quote=True)
    breadcrumb = (
        '<a href="../writing/index.html" style="color:inherit; text-decoration:none;">Writing</a> / '
        f'<a href="../{section}/index.html" style="color:inherit; text-decoration:none;">{info["label"]}</a> / '
        f"{title_esc}"
    )
    body_html = markdown.markdown(
        post["body_md"],
        extensions=["fenced_code", "tables", "sane_lists", "smarty"],
        output_format="html5",
    )
    page = PAGE.substitute(
        title=title_esc,
        title_attr=title_esc,
        summary_attr=summary_esc,
        github_icon=GITHUB_ICON,
        breadcrumb=breadcrumb,
        date=html.escape(post["date"]),
        back=info["back"],
        body=body_html,
    )
    out = ROOT / section / f"{post['slug']}.html"
    out.write_text(page, encoding="utf-8")
    return out


def listing_html(posts: list[dict]) -> str:
    if not posts:
        return '        <p class="empty-state">Coming soon!</p>'
    cards = []
    for p in posts:
        cards.append(
            f'        <a href="{p["slug"]}.html" class="post-card">\n'
            f'          <span class="post-date">{html.escape(p["date"])}</span>\n'
            f'          <span class="post-title">{html.escape(p["title"])}</span>\n'
            f'          <p class="post-preview">{html.escape(p["summary"])}</p>\n'
            f"        </a>"
        )
    return "\n".join(cards)


def refresh_index(section: str, posts: list[dict]) -> None:
    index_path = ROOT / section / "index.html"
    text = index_path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError(f"{index_path}: missing {START} / {END} markers")
    before, _, rest = text.partition(START)
    _, _, after = rest.partition(END)
    new = f"{before}{START}\n{listing_html(posts)}\n        {END}{after}"
    index_path.write_text(new, encoding="utf-8")


def badge_html(count: int) -> str:
    if count == 0:
        return '<span class="writing-card-badge soon">Coming soon</span>'
    noun = "entry" if count == 1 else "entries"
    return f'<span class="writing-card-badge">{count} {noun}</span>'


def refresh_writing_hub(counts: dict[str, int]) -> None:
    """Update each section's entry-count badge on the Writing hub page."""
    hub = ROOT / "writing" / "index.html"
    text = hub.read_text(encoding="utf-8")
    for section, count in counts.items():
        start, end = f"<!-- COUNT:{section} -->", f"<!-- /COUNT:{section} -->"
        if start not in text or end not in text:
            print(f"  (writing hub: no {start} marker, skipping {section})")
            continue
        before, _, rest = text.partition(start)
        _, _, after = rest.partition(end)
        text = f"{before}{start}{badge_html(count)}{end}{after}"
    hub.write_text(text, encoding="utf-8")
    print("writing hub: badges updated")


def process_project_notes(project: str, notes_md: str) -> dict[str, str]:
    """Parse project notes by ## heading (e.g. '## What I built') and render to HTML."""
    sections = {}
    lines = notes_md.strip().split("\n")
    current_section = None
    current_content = []

    for line in lines:
        if line.startswith("## "):
            # New section heading
            if current_section:
                # Save previous section
                body_html = markdown.markdown(
                    "\n".join(current_content).strip(),
                    extensions=["fenced_code", "tables", "sane_lists", "smarty"],
                    output_format="html5",
                )
                sections[current_section] = body_html
            # Extract the section name and normalize it
            heading = line[3:].strip()  # Remove "## "
            current_section = heading.lower().replace(" ", "-")
            current_content = []
        elif current_section is not None:
            current_content.append(line)

    # Save the last section
    if current_section:
        body_html = markdown.markdown(
            "\n".join(current_content).strip(),
            extensions=["fenced_code", "tables", "sane_lists", "smarty"],
            output_format="html5",
        )
        sections[current_section] = body_html

    return sections


def inject_project_notes(project: str, sections: dict[str, str]) -> None:
    """Inject rendered project notes into the project detail page."""
    detail_page = ROOT / "projects" / project / "index.html"
    if not detail_page.exists():
        print(f"  (project detail page not found: {detail_page})")
        return

    text = detail_page.read_text(encoding="utf-8")
    # Map section names to the markers in the HTML
    marker_map = {
        "what-i-built": "BUILT",
        "what-i-learned": "LEARNED",
    }

    for section_name, html_content in sections.items():
        marker_key = marker_map.get(section_name)
        if not marker_key:
            continue
        start = f"<!-- NOTES:{marker_key}:START -->"
        end = f"<!-- NOTES:{marker_key}:END -->"
        if start not in text or end not in text:
            print(f"  (project {project}: no {start} marker)")
            continue
        before, _, rest = text.partition(start)
        _, _, after = rest.partition(end)
        text = f"{before}{start}\n          {html_content}\n          {end}{after}"

    detail_page.write_text(text, encoding="utf-8")
    print(f"  · projects/{project}: notes injected")


def main() -> None:
    total = 0
    counts: dict[str, int] = {}
    for section in SECTIONS:
        posts = collect(section)
        counts[section] = len(posts)
        for post in posts:
            out = write_page(section, post)
            print(f"  · {out.relative_to(ROOT)}")
            total += 1
        refresh_index(section, posts)
        print(f"{section}: {len(posts)} post(s) → refreshed {section}/index.html")
    refresh_writing_hub(counts)

    # Process project notes
    projects_dir = CONTENT / "projects"
    if projects_dir.exists():
        for project_dir in sorted(projects_dir.iterdir()):
            if not project_dir.is_dir():
                continue
            notes_path = project_dir / "notes.md"
            if notes_path.exists():
                notes_text = notes_path.read_text(encoding="utf-8")
                sections = process_project_notes(project_dir.name, notes_text)
                inject_project_notes(project_dir.name, sections)
                total += 1

    print(f"Done. {total} page(s) built.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 — surface a clean message to the user
        sys.exit(f"build error: {exc}")
