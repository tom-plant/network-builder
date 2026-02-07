# platforms/twitter.py
# Twitter discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_twitter_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for Twitter."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:x.com inurl:status ({keywords}){exclusions}',
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
    
    handles = []
    for result in results:
        link = result.get("link", "")
        if "x.com/" in link and "/status/" in link:
            parts = link.split("x.com/")[1].split("/")
            if len(parts) >= 3 and parts[1] == "status":
                handle = parts[0]
                if handle not in ["hashtag", "search", "i", "home", "explore", "intent", "share", "tos", "privacy"]:
                    handles.append(handle)
    
    return handles

def discover_twitter(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full Twitter discovery."""

    if output_handler:
        output_handler.write(f"\n🔍 Discovering Twitter accounts...\n")
    else:
        print(f"\n🔍 Discovering Twitter accounts...")
    
    all_handles = []
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
            
            handles = search_twitter_bundle(keywords, start, apply_filter)
            all_handles.extend(handles)

            if output_handler:
                output_handler.write(f"found {len(handles)} handles\n")
            else:
                print(f"found {len(handles)} handles")
            
            time.sleep(SEARCH_DELAY)
    
    return all_handles