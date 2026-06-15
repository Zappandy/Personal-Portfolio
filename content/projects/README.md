# Project notes

Markdown sources for your project detail pages. `build.py` reads these, renders them, and injects them into the project pages.

## Add or update project notes

Each project folder has a `notes.md` file:

```
content/projects/preply/notes.md
content/projects/inventory-agent/notes.md
```

The Markdown is organized by `##` headings:

```markdown
## What I built

Describe the systems and core responsibilities...

## What I learned

Reflect on the most interesting technical or product insight...
```

**Both headings are required** — the build script uses them to know where to inject the content.

Build:

```bash
uv run build.py
```

This regenerates the project detail pages with your updated notes. Commit the `.md` **and** the generated `.html`.

## Add a new project

1. Create `content/projects/<project-name>/notes.md` with the sections above.
2. Create `projects/<project-name>/index.html` (project detail page) with the markers:
   ```html
   <!-- NOTES:BUILT:START -->
   <!-- NOTES:BUILT:END -->
   
   <!-- NOTES:LEARNED:START -->
   <!-- NOTES:LEARNED:END -->
   ```
3. Run `uv run build.py` to inject the content.
