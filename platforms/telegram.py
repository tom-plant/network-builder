# platforms/telegram.py
# Telegram discovery logic

import requests
import time
from config import SERPAPI_KEY, SEARCH_DELAY

def search_telegram_bundle(keywords, start=0, apply_filter=False):
    """Run a single SerpAPI search for Telegram."""
    from config import NEWS_OUTLET_EXCLUSIONS
    
    exclusions = f" {NEWS_OUTLET_EXCLUSIONS}" if apply_filter else ""

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f'site:t.me/s ({keywords}) (channel OR group OR community){exclusions}',
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
        link = result.get("link", "")
        if "t.me/s/" in link:
            try:
                # Extract: https://t.me/s/channelname -> channelname
                channel = link.split("/s/")[1].split("/")[0]
                channel = channel.split("?")[0]
                if channel[0]:
                    channels.append(channel)
            except:
                pass
    
    return channels

def discover_telegram(keyword_bundles, output_handler=None, apply_filter=False):
    """Run full Telegram discovery."""

    if output_handler:
        output_handler.write(f"\n🔍 Discovering Telegram channels...\n")
    else:
        print(f"\n🔍 Discovering Telegram channels...")
    
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
            
            channels = search_telegram_bundle(keywords, start, apply_filter)
            all_channels.extend(channels)

            if output_handler:
                output_handler.write(f"found {len(channels)} channels\n")
            else:
                print(f"found {len(channels)} channels")
            
            time.sleep(SEARCH_DELAY)
    
    return all_channels