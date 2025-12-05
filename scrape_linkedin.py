"""
Script to scrape LinkedIn posts from multiple companies and save results to a text file.
Reads company names and URLs from linkedin_urls.json and outputs results to linkedin_output.txt
"""

import json
from datetime import datetime
from linkedin_agent import get_linkedin_updates

def scrape_and_save():
    """
    Read company data from linkedin_urls.json, scrape each one, and save results to linkedin_output.txt
    Format: [["Company Name", "URL"], ["Company Name 2", "URL2"], ...]
    """
    # Read company data from JSON file
    try:
        with open('linkedin_urls.json', 'r') as f:
            companies = json.load(f)
    except FileNotFoundError:
        print("Error: linkedin_urls.json not found!")
        print("Please create linkedin_urls.json with format: [[\"Company Name\", \"URL\"], ...]")
        return
    except json.JSONDecodeError:
        print("Error: linkedin_urls.json is not valid JSON!")
        return
    
    if not companies:
        print("Error: linkedin_urls.json is empty!")
        return
    
    if not isinstance(companies, list):
        print("Error: linkedin_urls.json should contain a list of [company_name, url] pairs!")
        return
    
    # Validate format
    for item in companies:
        if not isinstance(item, list) or len(item) != 2:
            print("Error: Each entry should be [\"Company Name\", \"URL\"]")
            print(f"Invalid entry: {item}")
            return
    
    print(f"Found {len(companies)} compan{'y' if len(companies) == 1 else 'ies'} to scrape")
    print("=" * 80)
    
    # Prepare output
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("LINKEDIN SCRAPING RESULTS")
    output_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Total Companies: {len(companies)}")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # Process each company
    for idx, (company_name, url) in enumerate(companies, 1):
        print(f"\n[{idx}/{len(companies)}] Scraping: {company_name}")
        print(f"  URL: {url}")
        
        output_lines.append("")
        output_lines.append("█" * 80)
        output_lines.append(f"COMPANY: {company_name.upper()}")
        output_lines.append("█" * 80)
        output_lines.append(f"URL: {url}")
        output_lines.append(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("─" * 80)
        output_lines.append("")
        
        try:
            posts = get_linkedin_updates(url, max_posts=10)
            
            if posts:
                output_lines.append(f"📊 Total Posts Found: {len(posts)}")
                output_lines.append("")
                
                for post_idx, post in enumerate(posts, 1):
                    output_lines.append(f"┌─ POST #{post_idx} " + "─" * 66)
                    output_lines.append(f"│ Position in feed: {post.get('position', post_idx)}")
                    if post.get('url') and post['url'] != url:
                        output_lines.append(f"│ Post URL: {post['url']}")
                    output_lines.append("│")
                    output_lines.append("│ Content:")
                    # Indent the content
                    content_lines = post.get('text', 'N/A').split('\n')
                    for line in content_lines:
                        output_lines.append(f"│ {line}")
                    output_lines.append("└" + "─" * 79)
                    output_lines.append("")
                
                print(f"  ✓ Extracted {len(posts)} posts from {company_name}")
            else:
                output_lines.append("⚠️  No posts found.")
                output_lines.append("")
                print(f"  ⚠️  No posts found for {company_name}")
        
        except Exception as e:
            error_msg = f"Error scraping {company_name}: {str(e)}"
            print(f"  ✗ {error_msg}")
            output_lines.append(f"❌ ERROR: {error_msg}")
            output_lines.append("")
    
    # Add summary at the end
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("END OF REPORT")
    output_lines.append("=" * 80)
    
    # Write to output file
    output_file = 'linkedin_output.txt'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"\n{'=' * 80}")
        print(f"✓ Results saved to {output_file}")
        print(f"{'=' * 80}")
    except Exception as e:
        print(f"\n✗ Error saving to file: {e}")

if __name__ == "__main__":
    scrape_and_save()

