# platforms/tiktok.py
# TikTok discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_tiktok_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for TikTok."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:tiktok.com inurl:/@ inurl:/video/ -inurl:/discover/ ({keywords}){exclusions}',
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
        if "tiktok.com/@" in link and "/video/" in link:
            try:
                # Extract: https://www.tiktok.com/@username/video/123 -> username
                parts = link.split("/@")[1].split("/")
                if parts[0]:
                    handles.append(parts[0])
            except:
                pass
    
    return handles

def discover_tiktok(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full TikTok discovery."""

    if output_handler:
        output_handler.write(f"\n🔍 Discovering TikTok accounts...\n")
    else:
        print(f"\n🔍 Discovering TikTok accounts...")
    
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
            
            handles = search_tiktok_bundle(keywords, start, apply_filter)
            all_handles.extend(handles)

            if output_handler:
                output_handler.write(f"found {len(handles)} handles\n")
            else:
                print(f"found {len(handles)} handles")
            
            time.sleep(SEARCH_DELAY)
    
    return all_handles