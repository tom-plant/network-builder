# platforms/reddit.py
# Reddit discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_reddit_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for Reddit."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:reddit.com/r ({keywords}){exclusions}',
        "tbs": "qdr:m",
        "num": "100",
        "start": start,
        "api_key": SERPAPI_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    
    data = response.json()
    results = data.get("organic_results", [])
    
    subreddits = []
    for result in results:
        link = result.get("link", "")
        if "reddit.com/r/" in link:
            try:
                # Extract: https://www.reddit.com/r/subreddit/... -> subreddit
                parts = link.split("/r/")[1].split("/")
                if parts[0]:
                    subreddits.append(parts[0])
            except:
                pass
    
    return subreddits

def discover_reddit(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full Reddit discovery."""

    if output_handler:
        output_handler.write(f"\n🔍 Discovering Reddit subreddits...\n")
    else:
        print(f"\n🔍 Discovering Reddit subreddits...")
    
    all_subreddits = []
    total_searches = sum(bundle["pages"] for bundle in keyword_bundles)
    search_count = 0
    
    for i, bundle_config in enumerate(keyword_bundles, 1):
        keywords = bundle_config["keywords"]
        pages = bundle_config["pages"]

        if output_handler:
            output_handler.write(f"\n   Bundle {i}/{len(keyword_bundles)}: {keywords}\n")
        else:
            print(f"\n   Bundle {i}/{len(keyword_bundles)}: {keywords}")
        
        for page in range(pages):
            search_count += 1
            start = page * 10

            if output_handler:
                output_handler.write(f"      Page {page + 1}/{pages} ({search_count}/{total_searches})...", end=" ")
            else:
                print(f"      Page {page + 1}/{pages} ({search_count}/{total_searches})...", end=" ")
            
            subreddits = search_reddit_bundle(keywords, start, apply_filter)
            all_subreddits.extend(subreddits)

            if output_handler:
                output_handler.write(f"found {len(subreddits)} subreddits\n")
            else:
                print(f"found {len(subreddits)} subreddits")
            
            time.sleep(SEARCH_DELAY)
    
    return all_subreddits