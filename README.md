# wilma-ects-summary
some interesting things

# Wilma ECTS Tracker

Scrapes ECTS credits for courses from the Wilma catalog (Helsinki) and sums
credits for the courses you've selected.

Two scripts:

| Script | What it does |
|---|---|
| `parser_test.py` | Crawls the catalog and builds a DB of course code → ECTS |
| `main.py` | Reads `trays` (selected courses) → sums credits, reports missing codes |

## Requirements

- Python 3.10+
- A Wilma account
- `pip install requests beautifulsoup4 python-dotenv`

## Setup

Create a `.env` file in the repo root:
WILMA_ID is the number in your Wilma URL (/!123456/trays).

```env
WILMA_BASE_URL=https://helsinki.inschool.fi
WILMA_LOGIN=your_username
WILMA_PASSWORD=your_password
WILMA_ID=!123456
