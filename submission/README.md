# SIH idea submission

Files for the SIH 2026 idea submission (SIH26006, team Vector66).

| File | What it is |
|---|---|
| `SIH2026_NauPlan_Vector66.pdf` / `.pptx` | The 6-slide deck on the official SIH 2026 template |
| `fields.py` | Portal text: title, abstract, description (run it to check lengths); copy also in `docs/submission.md` |
| `content_freight.py` | All slide text, references, flow chart and screenshot layout |
| `build_freight.py` | Fills `template.pptx` without changing its format (pointers verbatim, bold) |
| `export_pdf.py` | Renders the slides with macOS Quick Look into an image-based PDF |
| `render.py` | Writes per-slide PNG previews to `qa/` for checking |
| `dash_hero.png`, `dash_gauge.png` | Screenshots of the running dashboard used on slide 3 |

Rebuild (macOS, from this folder):

```bash
uv run python build_freight.py && uv run python export_pdf.py
```

Rules followed: template pointers word for word, headings bold, 6 slides, no long dashes in our copy, money figures from the synthetic programme labelled as such.
