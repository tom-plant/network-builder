# platforms/facebook.py
# Facebook discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_facebook_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for Facebook."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""
    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:facebook.com ({keywords}) (inurl:/posts/ OR inurl:/?) -groups -group -hashtag -albums -album -photos -photo -videos -video -watch -reel -reels -events -event -marketplace{exclusions}',
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
    
    identifiers = []
    for result in results:
        link = result.get("link", "")
        if "facebook.com/" in link:
            try:
                parts = link.split("facebook.com/")[1].split("/")
                if len(parts) >= 2 and parts[0]:
                    identifier = parts[0]
                    if identifier not in ["groups", "hashtag", "events", "marketplace", "watch", "reel", "reels"]:
                        identifiers.append(identifier)
            except:
                pass
    
    return identifiers

def discover_facebook(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full Facebook discovery."""
    if output_handler:
        output_handler.write(f"\n🔍 Discovering Facebook pages...\n")
    else:
        print(f"\n🔍 Discovering Facebook pages...")
    
    all_identifiers = []
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
            
            identifiers = search_facebook_bundle(keywords, start, apply_filter)
            all_identifiers.extend(identifiers)

            if output_handler:
                output_handler.write(f"found {len(identifiers)} pages\n")
            else:
                print(f"found {len(identifiers)} pages")
            
            time.sleep(SEARCH_DELAY)
    
    return all_identifiers