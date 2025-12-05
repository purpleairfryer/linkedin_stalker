"""
LinkedIn Agent Module
Scrapes latest posts from Company Pages and User Activity feeds using Playwright.
"""

import json
import time
import random
import re
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def parse_relative_date(date_text):
    """
    Parse relative date text (e.g., "2d", "3h", "1w") into a datetime object.
    
    Args:
        date_text: String like "2d", "3h ago", "1w", "edited 5m", etc.
    
    Returns:
        datetime object representing the parsed date, or None if invalid/too old
    """
    if not date_text:
        return None
    
    # Clean the text: remove "edited", "•", extra whitespace
    cleaned = date_text.lower()
    cleaned = re.sub(r'edited\s*', '', cleaned)
    cleaned = re.sub(r'•', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r'\s*ago\s*', '', cleaned)
    
    # Extract number and unit
    match = re.search(r'(\d+)\s*([a-z]+)', cleaned)
    if not match:
        return None
    
    number = int(match.group(1))
    unit = match.group(2).lower()
    
    # Calculate timedelta based on unit
    now = datetime.now()
    
    if unit in ['m', 'min', 'mins', 'minute', 'minutes']:
        delta = timedelta(minutes=number)
    elif unit in ['h', 'hr', 'hrs', 'hour', 'hours']:
        delta = timedelta(hours=number)
    elif unit in ['d', 'day', 'days']:
        delta = timedelta(days=number)
    elif unit in ['w', 'wk', 'week', 'weeks']:
        delta = timedelta(days=number * 7)
    elif unit in ['mo', 'month', 'months']:
        delta = timedelta(days=number * 30)
    elif unit in ['y', 'yr', 'year', 'years']:
        # Years are too old for our use case (max 30 days)
        return None
    else:
        return None
    
    return now - delta


def get_linkedin_updates(url, max_posts=10, max_days=None, debug=False):
    """
    Scrape LinkedIn posts from a Company Page or User Activity feed.
    
    Args:
        url: LinkedIn URL (company page or user activity feed)
        max_posts: Maximum number of posts to extract (default: 10)
        max_days: Optional - Maximum age of posts to include (default: None, disabled)
        debug: If True, saves HTML structure to debug.html (default: False)
    
    Returns:
        List of dictionaries with keys: 'position', 'text', 'url'
    """
    posts = []
    seen_content = set()  # Track seen content to avoid duplicates
    seen_urns = set()  # Track unique post URNs to avoid processing same post twice
    cutoff_date = datetime.now() - timedelta(days=max_days) if max_days else None
    
    try:
        with sync_playwright() as p:
            # Launch browser (headless=False recommended for LinkedIn)
            browser = p.chromium.launch(headless=False)
            
            # Create context with realistic user agent
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # Load cookies
            try:
                with open('linkedin_cookies.json', 'r') as f:
                    cookies = json.load(f)
                    context.add_cookies(cookies)
            except FileNotFoundError:
                print("Warning: linkedin_cookies.json not found. Scraping may fail without authentication.")
                return []
            except json.JSONDecodeError:
                print("Warning: linkedin_cookies.json is not valid JSON. Scraping may fail.")
                return []
            
            page = context.new_page()
            
            # Navigate to URL
            print(f"Navigating to {url}...")
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(2)  # Wait for page to fully load
            
            # Sort by Recent
            print("Attempting to sort by Recent...")
            try:
                # Try multiple selector strategies for the sort dropdown
                sort_selectors = [
                    'button:has-text("Sort by")',
                    'button:has-text("Top")',
                    '[aria-label*="Sort"]',
                    'button[aria-label*="sort"]',
                    '.feed-sort-dropdown button',
                    'button:has([class*="sort"])',
                ]
                
                sort_button = None
                for selector in sort_selectors:
                    try:
                        sort_button = page.query_selector(selector)
                        if sort_button:
                            break
                    except:
                        continue
                
                if sort_button:
                    sort_button.click()
                    time.sleep(1)
                    
                    # Click "Recent" option
                    recent_selectors = [
                        'button:has-text("Recent")',
                        'button:has-text("Latest")',
                        '[role="menuitem"]:has-text("Recent")',
                        '[role="menuitem"]:has-text("Latest")',
                        'li:has-text("Recent")',
                        'li:has-text("Latest")',
                    ]
                    
                    for selector in recent_selectors:
                        try:
                            recent_option = page.query_selector(selector)
                            if recent_option:
                                recent_option.click()
                                print("Sorted by Recent")
                                time.sleep(3)  # Wait for feed to refresh
                                break
                        except:
                            continue
                else:
                    print("Sort dropdown not found, continuing with default sort...")
            except Exception as e:
                print(f"Could not sort by Recent: {e}. Continuing with default sort...")
            
            # Scrolling loop - scroll enough to load the posts we need
            print(f"Scrolling to load posts (target: {max_posts} posts)...")
            scroll_count = 3  # Reduced scrolling since we only need top posts
            for i in range(scroll_count):
                page.mouse.wheel(0, 600)
                time.sleep(random.uniform(1.0, 1.5))
                print(f"  Scroll {i+1}/{scroll_count}...")
            
            # Expand "see more" buttons
            print("Expanding 'see more' buttons...")
            see_more_selectors = [
                'button:has-text("see more")',
                'button:has-text("See more")',
                'button:has-text("see less")',  # Sometimes already expanded
                '[aria-label*="see more"]',
                'button[class*="see-more"]',
                'span:has-text("see more")',
            ]
            
            for selector in see_more_selectors:
                try:
                    buttons = page.query_selector_all(selector)
                    for button in buttons:
                        try:
                            if button.is_visible():
                                button.scroll_into_view_if_needed()
                                button.click()
                                time.sleep(0.5)
                        except:
                            continue
                except:
                    continue
            
            time.sleep(2)  # Wait for content to expand
            
            # Debug mode: save HTML structure
            if debug:
                html_content = page.content()
                with open('debug.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("Debug: Saved page HTML to debug.html")
            
            # Find all post containers using the most specific selector
            print("Extracting posts...")
            
            # LinkedIn typically uses:
            # - <div class="feed-shared-update-v2" data-urn="urn:li:activity:..."> for each post
            # OR
            # - <li> elements with data-occludable-job-id or similar attributes
            
            # Try to find posts with URN identifiers first (most reliable)
            post_elements = page.query_selector_all('[data-urn*="urn:li:activity"]')
            if post_elements:
                print(f"Found {len(post_elements)} posts using data-urn selector")
            else:
                # Fallback: try other selectors
                post_selectors = [
                    'div.feed-shared-update-v2',
                    '[class*="feed-shared-update-v2"]',
                    'li.profile-creator-shared-feed-update__container',
                    'div[data-id*="urn:li:activity"]',
                ]
                
                for selector in post_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            post_elements = elements
                            print(f"Found {len(elements)} posts using selector: {selector}")
                            break
                    except:
                        continue
            
            if not post_elements:
                print("Warning: No posts found with any selector strategy")
                browser.close()
                return []
            
            # Process each post
            for idx, post_element in enumerate(post_elements):
                # Stop if we've reached our target
                if len(posts) >= max_posts:
                    print(f"\nReached target of {max_posts} posts. Stopping.")
                    break
                
                try:
                    # Check if we've already processed this post by URN
                    post_urn = None
                    try:
                        post_urn = post_element.get_attribute('data-urn')
                        if not post_urn:
                            post_urn = post_element.get_attribute('data-id')
                        
                        if post_urn and post_urn in seen_urns:
                            if debug:
                                print(f"  Skipping post {idx + 1}: already processed (URN: {post_urn[:50]}...)")
                            continue
                        
                        if post_urn:
                            seen_urns.add(post_urn)
                    except:
                        pass
                    
                    # Check for repost
                    post_text_content = post_element.inner_text().lower()
                    if 'reposted this' in post_text_content[:200]:  # Check first 200 chars for repost indicator
                        if debug:
                            print(f"  Skipping post {idx + 1}: repost")
                        continue
                    
                    # Skip date extraction - just get posts in order
                    post_date = None
                    
                    # Extract text content - try to get main post content
                    text_content = None
                    
                    # Try to get the description/commentary section specifically
                    description_selectors = [
                        '.feed-shared-update-v2__description',
                        '.update-components-text',
                        '[class*="commentary"]',
                    ]
                    
                    for selector in description_selectors:
                        try:
                            text_elem = post_element.query_selector(selector)
                            if text_elem:
                                text_content = text_elem.inner_text()
                                if text_content and len(text_content.strip()) > 20:
                                    break
                        except:
                            continue
                    
                    # If still no content, get full post text and clean it
                    if not text_content or len(text_content.strip()) < 20:
                        full_text = post_element.inner_text()
                        lines = full_text.split('\n')
                        
                        # More aggressive filtering
                        filtered_lines = []
                        skip_patterns = [
                            r'^\d+\s*(?:tuần|tháng|ngày|giờ|phút)',  # Vietnamese dates
                            r'^\d+\s*(?:week|month|day|hour|minute|min|hr|d|h|m|w)',  # English dates
                            r'^(?:Like|Comment|Share|Send|Follow|Repost)',  # Action buttons
                            r'^\d+[,\d]*$',  # Pure numbers
                            r'^Hiển thị với',  # Vietnamese metadata
                            r'Kích hoạt để xem',  # Image activation text
                        ]
                        
                        for line in lines:
                            line_clean = line.strip()
                            if len(line_clean) < 3:
                                continue
                            
                            # Check if line matches any skip pattern
                            should_skip = False
                            for pattern in skip_patterns:
                                if re.match(pattern, line_clean, re.IGNORECASE):
                                    should_skip = True
                                    break
                            
                            if not should_skip:
                                filtered_lines.append(line)
                        
                        text_content = '\n'.join(filtered_lines)
                    
                    # Clean up text
                    if text_content:
                        text_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', text_content)
                        text_content = text_content.strip()
                    
                    # Check for duplicates using first 100 characters
                    if text_content:
                        content_signature = text_content[:100].lower().strip()
                        if content_signature in seen_content:
                            if debug:
                                print(f"  Skipping post {idx + 1}: duplicate content")
                            continue
                        seen_content.add(content_signature)
                    
                    # Debug: Show what we found
                    if debug:
                        print(f"\nPost {idx + 1} analysis:")
                        print(f"  URN: {post_urn[:80] if post_urn else 'N/A'}")
                        print(f"  Content length: {len(text_content) if text_content else 0}")
                        print(f"  First 100 chars: {text_content[:100] if text_content else 'N/A'}")
                    
                    # Extract permalink/URL with improved selectors
                    post_url = None
                    url_selectors = [
                        'a[href*="/feed/update/"]',
                        'a[href*="/activity-"]',
                        'a[href*="/posts/"]',
                        'a.feed-shared-update-v2__content-wrapper',
                        '[data-id*="urn:li:activity"] a',
                    ]
                    
                    for selector in url_selectors:
                        try:
                            url_elem = post_element.query_selector(selector)
                            if url_elem:
                                href = url_elem.get_attribute('href')
                                if href and ('/feed/update/' in href or '/activity-' in href or '/posts/' in href):
                                    if href.startswith('/'):
                                        post_url = f"https://www.linkedin.com{href}"
                                    elif href.startswith('http'):
                                        post_url = href.split('?')[0]  # Remove query params
                                    break
                        except:
                            continue
                    
                    # If we have valid content, add to posts
                    if text_content and len(text_content.strip()) > 20:
                        posts.append({
                            'position': len(posts) + 1,
                            'text': text_content,
                            'url': post_url or url
                        })
                        # Show first 60 chars of content
                        content_preview = text_content[:60].replace('\n', ' ') + '...' if len(text_content) > 60 else text_content.replace('\n', ' ')
                        print(f"✓ Post {len(posts)}: {content_preview}")
                
                except Exception as e:
                    print(f"Error processing post {idx + 1}: {e}")
                    continue
            
            browser.close()
    
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []
    
    print(f"\nTotal posts extracted: {len(posts)}")
    return posts


if __name__ == "__main__":
    # Example usage
    print("LinkedIn Agent Module")
    print("=" * 60)
    print("Make sure linkedin_cookies.json exists with valid cookies.")
    print("\nUsage:")
    print("  from linkedin_agent import get_linkedin_updates")
    print("  posts = get_linkedin_updates('https://www.linkedin.com/company/openai/posts/', max_posts=10)")
    print("\nOr use scrape_linkedin.py to scrape multiple URLs from linkedin_urls.json")

