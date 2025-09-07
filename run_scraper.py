#!/usr/bin/env python3
import argparse
from datetime import datetime
from enam_scraper.scraper import run_focused_scraper

def main():
    parser = argparse.ArgumentParser(
        description="Extract India APMC mandi contact details from eNAM (https://enam.gov.in/web/apmc-contact-details)."
    )
    parser.add_argument("--state", default="Gujarat", help="State name as it appears on eNAM (e.g., 'Maharashtra')")
    parser.add_argument("--max_districts", type=int, default=None, help="Limit number of districts processed (debug)")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat(timespec='seconds')}] Starting scrape for state: {args.state}")
    df = run_focused_scraper(state=args.state, max_districts=args.max_districts)
    if df is None:
        print("No data saved. Check logs above.")
    else:
        print("Done. See the CSV saved in the current directory.")

if __name__ == "__main__":
    main()
