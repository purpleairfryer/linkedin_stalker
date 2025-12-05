"""
Debug script to analyze LinkedIn HTML structure and identify posts.
This will scrape with debug mode enabled and save the HTML structure.
"""

from linkedin_agent import get_linkedin_updates
import json

def debug_scrape():
    """
    Run scraping with debug mode to see what's happening
    """
    # Read company data from JSON file
    try:
        with open('linkedin_urls.json', 'r') as f:
            companies = json.load(f)
    except FileNotFoundError:
        print("Error: linkedin_urls.json not found!")
        return
    
    if not companies:
        print("Error: No companies in linkedin_urls.json")
        return
    
    # Take the first company for debugging
    if isinstance(companies[0], list) and len(companies[0]) == 2:
        company_name, url = companies[0]
    else:
        print("Error: linkedin_urls.json should have format: [[\"Company Name\", \"URL\"], ...]")
        return
    print("=" * 60)
    print("LinkedIn Scraper - DEBUG MODE")
    print("=" * 60)
    print(f"\nCompany: {company_name}")
    print(f"URL: {url}\n")
    
    # Run with debug mode
    posts = get_linkedin_updates(url, max_posts=10, debug=True)
    
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    print(f"Total posts extracted: {len(posts)}")
    print(f"HTML structure saved to: debug.html")
    print("\nPosts found:")
    for i, post in enumerate(posts, 1):
        preview = post['text'][:80].replace('\n', ' ') + '...' if len(post['text']) > 80 else post['text'].replace('\n', ' ')
        print(f"{i}. {preview}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS TIPS")
    print("=" * 60)
    print("1. Open debug.html in a browser to see the page structure")
    print("2. Look for repeating patterns in the HTML")
    print("3. Check for data-urn or data-id attributes on post containers")
    print("4. Look for class names like:")
    print("   - feed-shared-update-v2")
    print("   - profile-creator-shared-feed-update__container")
    print("   - occludable-update")
    print("\nCommon LinkedIn Post Container Patterns:")
    print("  <div class=\"feed-shared-update-v2\" data-urn=\"urn:li:activity:...\">")
    print("  <li class=\"profile-creator-shared-feed-update__container\">")
    print("  <div class=\"occludable-update\" data-id=\"...\">")

if __name__ == "__main__":
    debug_scrape()

