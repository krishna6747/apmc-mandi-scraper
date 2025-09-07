[README.md](https://github.com/user-attachments/files/22194783/README.md)
# eNAM APMC Mandi Scraper · End‑to‑End Pipeline

> Extracts India APMC mandi contact details from the official eNAM portal with an automated, repeatable Selenium pipeline. Cleaned data lands as CSV — perfect for analysis and open-data projects.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Selenium](https://img.shields.io/badge/selenium-automated-green)
![PRs welcome](https://img.shields.io/badge/PRs-welcome-orange)

## ✨ What this does
- Navigates to the official eNAM APMC contact page
- Selects a **state → district → all mandis** (no artificial cap)
- Extracts contact information from **tables + page text**
- Cleans and de-duplicates records
- Saves a timestamped CSV like `enam_clean_data_{epoch}.csv`

> **Heads-up:** The full state scrape can take time. Use `--max_districts` to run quick tests.

## 🧠 How it works (pipeline)
```mermaid
flowchart LR
    A[Start] --> B[Load eNAM APMC page]
    B --> C[Select language: English]
    C --> D[Select State]
    D --> E[Loop Districts]
    E --> F[Loop Mandis in District]
    F --> G[Extract from tables + text]
    G --> H[Clean + de-duplicate]
    H --> I[Save CSV]
```

## 🛠 Tech
- **Selenium** (headless Chrome), **pandas**
- Tested as a **Jupyter notebook** and **CLI script**

## 🚀 Quickstart
```bash
# 1) Create & activate a virtualenv (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Make sure Chrome/Chromedriver are available on PATH
#    (or install with your OS package manager)
#    On Linux, verify: which google-chrome || which chromium-browser

# 4) Run the scraper (example: Maharashtra)
python scripts/run_scraper.py --state "Maharashtra"
# For a quick smoke test
python scripts/run_scraper.py --state "Maharashtra" --max_districts 1
```

The script will save a cleaned CSV in the **current working directory** and print a quick summary.

## 📦 Project structure
```
enam-apmc-mandi-scraper/
├─ src/enam_scraper/scraper.py     # Selenium scraper (logic preserved from notebook)
├─ scripts/run_scraper.py          # CLI wrapper
├─ notebooks/mandi_address.ipynb   # Original notebook
├─ data/
│  ├─ raw/                         # (optional) raw dumps
│  └─ processed/                   # (optional) cleaned data
├─ .github/workflows/ci.yml        # Lint + smoke test
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

## 📑 Output schema (CSV)
- `state` · `district` · `mandi_name` · `address` · `contact_details`

##  GitHub
- Add **topics**: `apmc`, `india`, `enam`, `mandi`, `web-scraping`, `selenium`, `data-pipeline`, `open-data`
- Pin the repo to your profile and add a clear **one‑line tagline**
- Upload a **social preview image** (Settings → General → Social preview)
- Open a few good **starter issues** (e.g., “Add Dockerfile”, “Publish dataset to release”)
- Add a short **demo GIF** of the scraper running (optional)

## 🧪 CI (optional but recommended)
This repo ships with a simple GitHub Actions workflow that runs lint checks and a **non-network** smoke test so your PRs stay green.

## 🤝 Responsible use
Scrapes public contact details from the official portal with delays and reasonable navigation. Please respect the website’s terms and avoid overwhelming their servers. This project is for educational and open‑data purposes.

## 📜 License
MIT © 2025 Krishna Vishwakarma
