# platforms/instagram.py
# Instagram discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_instagram_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for Instagram."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""
    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:instagram.com ({keywords}){exclusions}',
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
        # Try to extract from link
        link = result.get("link", "")
        if "instagram.com/" in link:
            try:
                parts = link.split("instagram.com/")[1].split("/")
                if parts[0] and parts[0] not in ["p", "reel", "tv", "explore"]:
                    handles.append(parts[0])
            except:
                pass
        
        # Also try from source field (e.g., "Instagram · username")
        source = result.get("source", "")
        if "Instagram" in source and "·" in source:
            try:
                handle = source.split("·")[1].strip()
                if handle:
                    handles.append(handle)
            except:
                pass
    
    return handles

def discover_instagram(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full Instagram discovery."""
    if output_handler:
        output_handler.write("\n🔍 Discovering Instagram accounts...\n")
    else:
        print(f"\n🔍 Discovering Instagram accounts...")
    
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
                output_handler.write(f"      Page {page + 1}/{pages} ({search_count}/{total_searches})... ", end=" ")
            else:
                print(f"      Page {page + 1}/{pages} ({search_count}/{total_searches})...", end=" ")
            
            handles = search_instagram_bundle(keywords, start, apply_filter)
            all_handles.extend(handles)
            
            if output_handler:
                output_handler.write(f"found {len(handles)} handles\n")
            else:
                print(f"found {len(handles)} handles")
            
            time.sleep(SEARCH_DELAY)
    
    return all_handles