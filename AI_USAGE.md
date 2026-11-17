# AI usage statement

List every use of an AI assistant (ChatGPT, Claude, Copilot, Gemini, etc.) in this project. Every member must be able to explain all submitted code and figures.

| Date | Tool | Task (what you asked) | Where it is used (file/section) | What you verified and how |
|---|---|---|---|---|
| 2026-11-17 | Claude Code (Claude Opus 5.5) | Write a simple script that downloads the three raw datasets; add an empty `visuals/` folder and a placeholder `index.html` so the repository check passes | `scripts/download_data.py`, `index.html`, `visuals/.gitkeep` | Ran the script: all 4 files downloaded; opened each file's first and last lines (NSIDC daily up to 2026-11-16, CO2 monthly up to 2026-09, GISTEMP up to 2026-10). Re-ran the repository check commands locally: all passed. |

Sections written entirely in our own words: data card, limitations, conclusions.
