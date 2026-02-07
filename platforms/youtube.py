# platforms/youtube.py
# YouTube discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_youtube_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for YouTube."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:youtube.com/shorts ({keywords}){exclusions}',
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
    
    channels = []
    for result in results:
        # Extract from source field (e.g., "YouTube · ChannelName")
        source = result.get("source", "")
        if "YouTube" in source and "·" in source:
            try:
                channel = source.split("·")[1].strip()
                if channel:
                    channels.append(channel)
            except:
                pass
    
    return channels

def discover_youtube(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full YouTube discovery."""

    if output_handler:
        output_handler.write(f"\n🔍 Discovering YouTube channels...\n")
    else:
        print(f"\n🔍 Discovering YouTube channels...")
    
    all_channels = []
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
            
            channels = search_youtube_bundle(keywords, start, apply_filter)
            all_channels.extend(channels)

            if output_handler:
                output_handler.write(f"found {len(channels)} handles\n")
            else:
                print(f"found {len(channels)} channels")
            
            time.sleep(SEARCH_DELAY)
    
    return all_channels