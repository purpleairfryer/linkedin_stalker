# LinkedIn Stalker - LinkedIn Post Scraper

A Python tool to scrape LinkedIn company page posts and user activity feeds using Playwright. Extract and organize posts from multiple companies for competitive analysis, market research, or content monitoring.

> ⚠️ **Disclaimer**: This tool is for educational and research purposes only. Users must comply with LinkedIn's Terms of Service and applicable laws.

## Features

- ✅ Extracts top N posts from LinkedIn feeds (default: 10)
- ✅ Cookie-based authentication
- ✅ Duplicate detection
- ✅ Repost filtering
- ✅ Multiple URL support
- ✅ Text output format

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Setup

### Step 1: Extract LinkedIn Cookies

Run the cookie extractor to save your LinkedIn session:

```bash
python get_linkedin_cookies.py
```

This will:
1. Open a browser window
2. Navigate to LinkedIn
3. Wait for you to log in manually
4. Save your cookies to `linkedin_cookies.json`

### Step 2: Configure Companies and URLs

Edit `linkedin_urls.json` to add company names and their LinkedIn URLs:

```json
[
  ["OpenAI", "https://www.linkedin.com/company/openai/posts/"],
  ["Anthropic", "https://www.linkedin.com/company/anthropic/posts/"],
  ["Google DeepMind", "https://www.linkedin.com/company/google-deepmind/posts/"]
]
```

**Format:** Each entry is an array with two elements:
1. Company/Person name (string)
2. LinkedIn URL (string)

## Usage

### Scrape Multiple URLs

Run the main scraper to process all URLs from `linkedin_urls.json`:

```bash
python scrape_linkedin.py
```

Results will be saved to `linkedin_output.txt`, organized by company with clear section separators.

### Scrape Single URL (Manual)

Use the agent module directly in Python:

```python
from linkedin_agent import get_linkedin_updates

# Get top 10 posts
posts = get_linkedin_updates("https://www.linkedin.com/company/openai/posts/", max_posts=10)

for post in posts:
    print(f"Position: {post['position']}")
    print(f"Content: {post['text']}")
    print(f"URL: {post['url']}")
    print()
```

## Configuration

### Number of Posts

Change the number of posts to extract by editing `scrape_linkedin.py`:

```python
posts = get_linkedin_updates(url, max_posts=20)  # Get 20 posts instead of 10
```

### Date Filtering (Optional)

If you want to filter by date (experimental, disabled by default):

```python
posts = get_linkedin_updates(url, max_posts=10, max_days=30)
```

## Output Format

The output file (`linkedin_output.txt`) is organized by company:

```
================================================================================
LINKEDIN SCRAPING RESULTS
Generated: 2024-12-05 10:30:00
Total Companies: 2
================================================================================

████████████████████████████████████████████████████████████████████████████████
COMPANY: COMPANY NAME 1
████████████████████████████████████████████████████████████████████████████████
URL: https://www.linkedin.com/company/...
Scraped: 2024-12-05 10:30:15
────────────────────────────────────────────────────────────────────────────────

📊 Total Posts Found: 10

┌─ POST #1 ──────────────────────────────────────────────────────────────────
│ Position in feed: 1
│
│ Content:
│ [Post content here...]
└───────────────────────────────────────────────────────────────────────────

[Additional posts...]

████████████████████████████████████████████████████████████████████████████████
COMPANY: COMPANY NAME 2
████████████████████████████████████████████████████████████████████████████████
[...]
```

## Project Structure

```
linkedin_stalker/
├── linkedin_agent.py              # Core scraping module
├── scrape_linkedin.py             # Batch scraper for multiple companies
├── get_linkedin_cookies.py        # Cookie extraction helper
├── debug_linkedin.py              # Debug mode scraper
├── linkedin_urls.json             # List of companies and URLs to scrape
├── linkedin_cookies.json.example  # Example cookie file structure
├── requirements.txt               # Python dependencies
├── LINKEDIN_STRUCTURE.md          # LinkedIn HTML structure documentation
├── README.md                      # This file
├── LICENSE                        # MIT License
└── .gitignore                     # Git ignore rules

# Generated files (gitignored):
├── linkedin_cookies.json          # Your session cookies
├── linkedin_output.txt            # Scraping results
└── debug.html                     # Debug output
```

## Troubleshooting

### Browser doesn't open

Make sure Playwright browsers are installed:
```bash
playwright install chromium
```

### No posts found

1. Check that `linkedin_cookies.json` exists and has valid cookies
2. Try running `get_linkedin_cookies.py` again to refresh cookies
3. Make sure you're logged into LinkedIn in the browser when extracting cookies

### Duplicates or missing content

The script includes deduplication logic and filters out:
- Reposts
- Image placeholders
- Action buttons (Like, Comment, Share)
- Metadata text

If posts are still being missed, try increasing `max_posts` parameter.

## Notes

- **Legal & Ethical Use**: This tool is for educational purposes and personal research. LinkedIn may rate-limit or block automated access. Always respect LinkedIn's Terms of Service and robots.txt.
- **Cookie Expiration**: Session cookies expire after some time. Re-run `get_linkedin_cookies.py` if scraping fails.
- **Detection Avoidance**: The script uses non-headless mode by default to reduce detection risk.
- **Rate Limiting**: Add delays between requests when scraping multiple companies to avoid rate limits.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for ensuring their use complies with LinkedIn's Terms of Service and applicable laws. The authors are not responsible for any misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT - see [LICENSE](LICENSE) file for details

