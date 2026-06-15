# Writing content

Markdown sources for the **Writing** section. `build.py` turns these into styled
HTML pages and refreshes the index listings + the Writing-hub entry counts.

## Add a post

1. Create a Markdown file in the right section folder:
   - `content/musings/<slug>.md`   → published to `musings/<slug>.html`
   - `content/learning/<slug>.md`  → published to `learning/<slug>.html`

   The filename (minus `.md`) becomes the URL slug, e.g. `fsdp-vs-ddp.md` → `musings/fsdp-vs-ddp.html`.

2. Start the file with frontmatter, then write Markdown:

   ```markdown
   ---
   title: FSDP vs DDP at Scale
   date: 2026-06-21
   summary: When sharding actually beats replication, from real cluster runs.
   ---

   ## Body starts here

   Normal Markdown — **bold**, lists, `code`, fenced ```code blocks```, tables, links.
   ```

   `title` and `date` are required; `summary` shows on the index card. `date` is `YYYY-MM-DD`
   (posts sort newest-first by it).

3. Build:

   ```bash
   uv run build.py
   ```

   This regenerates the post page, the section index listing, and the hub badge
   ("3 entries" / "Coming soon" when empty). Then commit the `.md` **and** the generated `.html`.

## Unpublish a post

Delete both the `content/<section>/<slug>.md` and the generated `<section>/<slug>.html`
(or move the `.md` into `private/` to keep it as a draft), then re-run `uv run build.py`.

## Drafts

Anything under `private/` is local-only (gitignored) and never built or deployed.
Move a draft into `content/<section>/` when it's ready to publish.
