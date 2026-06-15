# Personal Portfolio — Andres Gonzalez

Live at: **[zappandy.github.io](https://zappandy.github.io)** *(update once deployed)*

---

## Running locally

No build step. Pure HTML/CSS/JS.

```bash
# From the repo root
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

---

## Project structure

```
.
├── index.html          # Single-page portfolio (hero, about, research, experience, skills)
├── style.css           # All styles — design tokens, Liquid Glass, layout, responsive
├── learning/
│   └── index.html      # Learning log index (links to setup notes etc.)
└── README.md
```

---

## Design decisions

### Stack
Vanilla HTML/CSS/JS — no framework, no build step, no dependencies. Chosen deliberately: instant load, deployable anywhere (GitHub Pages, Netlify, a USB stick), and fully auditable by anyone reading the source. The complexity budget is visual, not technical.

### Liquid Glass
Follows Apple's iOS 26 / macOS 26 design language. Key properties applied throughout:

| Element | Treatment |
|---|---|
| Navigation | `backdrop-filter: blur(40px) saturate(180%)` + inset top-edge highlight |
| Cards (pubs, exp, projects) | `rgba(255,255,255,0.58)` bg + blur + specular `::before` radial gradient |
| Interest tags / skill pills | Frosted glass pills with inset highlight |
| Ghost buttons | Semi-transparent with blur, white border |
| Tab bar | Glass pill container, active tab is opaque glass capsule |

The hero uses a deep navy-teal gradient (`#060d1a` base + four layered radial blobs) so the glass has a rich background to refract against. Light sections (About, Research, Skills) use subtle blue-tinted gradients for the same reason.

### Layout
- **Hero**: Two-column — pitch left, swappable code card right. Collapses to single column on mobile.
- **Content**: Tabbed between "Research & Projects" (default) and "Where I've Worked". Publications are the primary showcase; experience is supporting context. This mirrors how ML researchers at top labs present themselves.
- **About**: Centered, with three stat cards (publications / pipeline speedup / years in ML) below the bio.
- **Code card**: Two snippets toggled by `FSDP` / `HuggingFace` tabs. Both firmly NLP/ML — one shows distributed training at scale, one shows LoRA fine-tuning from the ACL 2024 work.

### Typography
System font stack (`-apple-system, BlinkMacSystemFont…`) for native rendering on Apple hardware. Monospace (`SF Mono, Fira Code`) for skill tags and the code card.

### Tone
Research-first, not resume-first. The site leads with research identity, publications, and engineering impact metrics (numbers in bold). Experience is one click away but not the headline.

---

## Things to fix before sharing

- [ ] EGU 2026 paper link is a `#` placeholder — update when the abstract URL is live
- [ ] Confirm which email to show publicly (currently `nanoandres24@hotmail.com` from resume — switch to `hagonzalez@technosylva.com` if preferred)
- [ ] Add a 3rd hackathon card once you're ready to share details
- [ ] Deploy to GitHub Pages (`Settings > Pages > Deploy from branch: main`)

---

## Writing workflow (Markdown → HTML)

The **Writing** section (Musings + Learning Log) is generated from Markdown by `build.py`,
in an isolated env managed by [uv](https://docs.astral.sh/uv/).

```bash
# one-time: provision the env (downloads Python + markdown)
uv sync

# write a post: content/musings/<slug>.md  (see content/README.md for frontmatter)
uv run build.py        # → musings/<slug>.html + refreshed index + hub badge counts
```

`build.py` writes the styled HTML pages, regenerates the index listings (between the
`POSTS:START/END` markers), and updates the Writing-hub entry counts ("3 entries" /
"Coming soon"). Commit the `.md` **and** the generated `.html`. Full guide: `content/README.md`.

Drafts and private notes live in `private/` (gitignored — never built or deployed).

**Suggested first posts:**
- A technical explainer on FSDP vs DDP (you've run both at scale)
- A write-up on the climate LLM paper
- "What I learned building on MareNostrum5"

## Roadmap

If Writing grows past ~30 posts and `build.py` starts feeling limiting, the natural next
step is a static site generator (Eleventy / Hugo) using the same `style.css`.

### Learning section
Expand `learning/index.html` into a proper log. Each entry is a short note: what you read, what you built, what surprised you. Group entries by topic (e.g. "Distributed Systems", "NLP Architecture", "Scientific ML"). The learning log doubles as evidence of continuous growth — useful for hiring managers and your own reference.

### Project / hackathon evidence images
Each project card should open a detail view (or link to a dedicated page) with:
- A screenshot or diagram of what you built
- A short "what I did / what I learned" paragraph
- Links to the repo, a demo (if any), and any write-up

To add images: create a `projects/` directory, add a subfolder per project with an `index.html` and image assets. Make the project card's entire surface area a link (`<a>` wrapping the card) pointing to that page. The detail page inherits `style.css` and the nav/footer pattern.

**For the Preply hackathon**, a screenshot of the agent routing flow or API response would work well. **For the HuggingFace hackathon**, a diagram of the inventory agent pipeline or a demo GIF.

### Additional future work
- **Dark/light mode toggle** — the site is currently dark-hero + light-content. A full dark mode toggle is a small JS addition and looks impressive on Apple hardware.
- **CV/PDF download** — add a "Download CV" button in the hero CTA row linking to a PDF export of your resume.
- **Google Scholar / ORCID link** — once you have more papers, link your Scholar profile from the publications section header.
- **Animations** — subtle scroll-triggered fade-in for cards (`IntersectionObserver` + a CSS class). Adds polish without breaking the clean aesthetic.
