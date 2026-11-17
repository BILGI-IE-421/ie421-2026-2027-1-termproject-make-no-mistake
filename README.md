# IE 421 - Data Science for Engineers Term Project (Please keep this main title in Readme as it is)

## Your Project Title Goes Here
Project abstract. Should be around 180-200 words. No visuals here.

## Student Names
Ada Güner Nohut (122203012)
Canberk Doğruoğlu (122202090)
Tümer Kaan Mutlu (122203046)
Yağız Efe (122203062)

## Files (Explain each of them with a sentence)
- `data/`: Contains the datasets used. (Define your datasets here. The full description goes in the data card, `data/README.md`. Raw downloads stay in `data/raw/` and are not committed.)
- `scripts/`: Scripts for downloading, cleaning and plotting the data. `download_data.py` downloads the raw files into `data/raw/`; `preprocess.py` cleans them and writes the daily, monthly and yearly tables to `data/processed/`; `q1_days_below.py` counts the days per year below the 1980s September average (question 1); `q1_method_check.py` tests how question 1 fills the missing early days; `q1_onset.py` tests when the climb started (straight line vs. flat-then-rise, with detection and threshold checks).
- `visuals/`: Includes the generated figures. `q1_days_below.png` shows the days per year below the 1980s September average, with a 5-year moving average; `q1_onset.png` shows the same counts with the straight-line and best flat-then-rise fits.
- `index.html` and `css/`: Main webpage for GitHub Pages hosting.
- `PROPOSAL.md`, `AI_USAGE.md`: Your proposal and your AI usage statement.
- `requirements.txt`: Python libraries your scripts need.
- `.github/`: The automatic repository check. Leave it as it is.

## How to run (from the repository root)
List the commands that reproduce your results, in the order they must be run.
```
pip install -r requirements.txt
python scripts/download_data.py
python scripts/preprocess.py
python scripts/q1_days_below.py
python scripts/q1_method_check.py
python scripts/q1_onset.py
```

## Key findings
Write your three main findings, one sentence each. Put the numbers in context. No visuals here.

## Hosting
The project is hosted using GitHub Pages (https://bilgi-ie-421.github.io/demo-repository).
Your page should be available as (https://bilgi-ie-421.github.io/ie421-2026-2027-1-termproject-yourteamname)
