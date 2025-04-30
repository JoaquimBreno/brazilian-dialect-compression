# Ariano Suassuna Book Scraper for LibGen

This script automatically scrapes and downloads books by Ariano Suassuna from Library Genesis (LibGen).

## Features

- Automatically finds and downloads all available books by Ariano Suassuna from LibGen
- Handles direct downloading from mirror sites
- Skips already downloaded books
- Preserves original file formats (PDF, EPUB, MOBI, etc.)
- Uses Playwright for reliable browser automation

## Requirements

- Python 3.7+
- Playwright virtual environment

## Installation

1. Clone or download this repository
2. Activate your Playwright environment:

```bash
# If you already have a Playwright environment
source playwright_env/bin/activate  # On Unix/MacOS
# or
playwright_env\Scripts\activate     # On Windows
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:

```bash
playwright install chromium
```

## Usage

Run the script with:

```bash
python suassuna_scraper.py
```

The script will:
1. Search for Ariano Suassuna's books on LibGen
2. Process each book one by one
3. Download the files in their original format (PDF, EPUB, MOBI, etc.)
4. Save the files to the current directory

## Notes

- The script uses a visible browser instance so you can monitor the progress
- Downloaded files are saved with cleaned filenames in the same directory as the script
- If a file with the same name already exists, it will be skipped

## Legal Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the website's terms of service when using this script. 