"""
Helper script to extract LinkedIn cookies after manual login.
This will open a browser, let you log in manually, then save cookies to linkedin_cookies.json
"""

import json
import sys
import traceback
from playwright.sync_api import sync_playwright

# Ensure output is flushed immediately
def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()

def save_linkedin_cookies():
    """
    Opens a browser, navigates to LinkedIn, waits for manual login,
    then saves cookies to linkedin_cookies.json
    """
    print_flush("=" * 60)
    print_flush("LinkedIn Cookie Extractor")
    print_flush("=" * 60)
    print_flush("\nThis script will:")
    print_flush("1. Open a browser window")
    print_flush("2. Navigate to LinkedIn")
    print_flush("3. Wait for you to log in manually")
    print_flush("4. Save your cookies to linkedin_cookies.json")
    print_flush("\nPress Enter to launch the browser...")
    input()
    
    try:
        print_flush("\nInitializing Playwright...")
        with sync_playwright() as p:
            print_flush("Launching Chromium browser...")
            try:
                browser = p.chromium.launch(headless=False)
                print_flush("✓ Browser launched successfully!")
            except Exception as e:
                print("\n" + "=" * 60)
                print("ERROR: Could not launch browser!")
                print("=" * 60)
                print(f"\nError: {e}")
                print("\nThis usually means Playwright browsers are not installed.")
                print("Please run the following command:")
                print("  playwright install chromium")
                print("\nOr install all browsers:")
                print("  playwright install")
                sys.exit(1)
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print_flush("\nOpening LinkedIn...")
            page.goto("https://www.linkedin.com", wait_until="networkidle", timeout=60000)
            
            print_flush("\n" + "=" * 60)
            print_flush("Browser is now open!")
            print_flush("=" * 60)
            print_flush("\nPlease log in to LinkedIn in the browser window.")
            print_flush("Once you're logged in and see your feed, come back here and press Enter...")
            input()
            
            # Get cookies from the context
            cookies = context.cookies()
            
            # Filter for LinkedIn cookies
            linkedin_cookies = [
                cookie for cookie in cookies
                if 'linkedin.com' in cookie.get('domain', '')
            ]
            
            if not linkedin_cookies:
                print("\nWarning: No LinkedIn cookies found. Make sure you're logged in.")
                browser.close()
                return
            
            # Ensure we have the essential cookies with correct format
            formatted_cookies = []
            for cookie in linkedin_cookies:
                formatted_cookie = {
                    "name": cookie.get("name"),
                    "value": cookie.get("value"),
                    "domain": cookie.get("domain", ".linkedin.com"),
                    "path": cookie.get("path", "/"),
                    "expires": cookie.get("expires", -1),
                    "httpOnly": cookie.get("httpOnly", True),
                    "secure": cookie.get("secure", True),
                    "sameSite": cookie.get("sameSite", "None")
                }
                formatted_cookies.append(formatted_cookie)
            
            # Save to file
            with open('linkedin_cookies.json', 'w') as f:
                json.dump(formatted_cookies, f, indent=2)
            
            print(f"\n✓ Successfully saved {len(formatted_cookies)} cookies to linkedin_cookies.json")
            
            # Check for essential cookies
            cookie_names = [c["name"] for c in formatted_cookies]
            if "li_at" in cookie_names:
                print("✓ Found 'li_at' cookie (essential for authentication)")
            else:
                print("⚠ Warning: 'li_at' cookie not found. You may need to log in again.")
            
            browser.close()
            print("\nDone! You can now use linkedin_agent.py with these cookies.")
    
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR occurred while running the script!")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        print("\nCommon issues:")
        print("1. Playwright browsers not installed - run: playwright install chromium")
        print("2. Browser already open - close any existing browser windows")
        print("3. Permission issues - try running as administrator")
        sys.exit(1)

if __name__ == "__main__":
    save_linkedin_cookies()
