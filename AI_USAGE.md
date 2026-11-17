# AI usage statement

List every use of an AI assistant (ChatGPT, Claude, Copilot, Gemini, etc.) in this project. Every member must be able to explain all submitted code and figures.

| Date | Tool | Task (what you asked) | Where it is used (file/section) | What you verified and how |
|---|---|---|---|---|
| 2026-11-17 | Claude Code (Claude Opus 5.5) | Write a simple script that downloads the three raw datasets; add an empty `visuals/` folder and a placeholder `index.html` so the repository check passes | `scripts/download_data.py`, `index.html`, `visuals/.gitkeep` | Ran the script: all 4 files downloaded; opened each file's first and last lines (NSIDC daily up to 2026-11-16, CO2 monthly up to 2026-09, GISTEMP up to 2026-10). Re-ran the repository check commands locally: all passed. |
| 2026-11-17 | Claude Code (Claude Opus 5.5) | Write a simple cleaning script: daily sea ice to monthly means, reshape GISTEMP to one row per month, join ice, temperature and CO2 on year and month from 1979, and build a yearly table; add one sentence per script to the README file list | `scripts/preprocess.py`, `data/processed/*.csv`, `README.md` (Files section) | Ran the script. Recomputed September 2012 mean extent from the raw daily file with a separate command (3.566, same as the script; NSIDC's published value is 3.57). Checked the 2012 NH spring anomaly (0.900) against GISTEMP's own MAM column (.90). Checked that December 1987 shows only 2 days and that the unfinished year 2026 is left out of `yearly.csv`. |

Sections written entirely in our own words: data card, limitations, conclusions.
