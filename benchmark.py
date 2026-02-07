# benchmark.py
"""
Network Builder Testing Harness

Usage:
1. Configure TEST_TOPICS, TEST_PLATFORMS, MAX_PAGES_PER_BUNDLE below
2. Run: python benchmark.py
3. Results output to terminal + JSON file

Features:
- Caches SerpAPI responses to avoid redundant API calls
- Configurable pagination (important for Deep vs Wide testing)
- Clean comparison tables + full JSON dump

Requirements:
- All platform files must have a search_[platform]_bundle(keywords, start) function
  Example: search_twitter_bundle(), search_reddit_bundle(), etc.
- These functions should return a list of identifiers (with duplicates OK)
"""

import json
import hashlib
import os
import time
from datetime import datetime
from pathlib import Path

# Import existing modules
from keyword_generator import generate_search_strategy
from aggregator import aggregate_and_filter
from config import TOP_N_RESULTS, SEARCH_DELAY

# Platform imports
from platforms.twitter import search_twitter_bundle
from platforms.facebook import search_facebook_bundle
from platforms.instagram import search_instagram_bundle
from platforms.tiktok import search_tiktok_bundle
from platforms.youtube import search_youtube_bundle
from platforms.reddit import search_reddit_bundle
from platforms.telegram import search_telegram_bundle


# ============================================================================
# CONFIGURATION - EDIT THESE
# ============================================================================

TEST_TOPICS = [
    # "Kendrick Lamar",
    "South China Sea",
    # "news in China",  # Uncomment to add more
]

# Platforms to test: ["twitter", "reddit", "instagram", "tiktok", "youtube", "facebook", "telegram"]
# Or use ["all"] to test all platforms
TEST_PLATFORMS = ["twitter", "reddit"]

# Max pages per bundle (for testing - keeps API calls low)
# Deep searches might need 4-6, Wide searches might need 2-3
MAX_PAGES_PER_BUNDLE = 5

# Scope: "A" (Deep), "B" (Wide), or "auto"
SCOPE = "auto"

# Cache directory
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


# ============================================================================
# PLATFORM MAPPING
# ============================================================================

PLATFORM_SEARCH_FUNCTIONS = {
    "twitter": search_twitter_bundle,
    "facebook": search_facebook_bundle,
    "instagram": search_instagram_bundle,
    "tiktok": search_tiktok_bundle,
    "youtube": search_youtube_bundle,
    "reddit": search_reddit_bundle,
    "telegram": search_telegram_bundle,
}


# ============================================================================
# CACHING LOGIC
# ============================================================================

def get_cache_key(platform, keywords, page):
    """Generate cache key from search parameters."""
    key_string = f"{platform}|{keywords}|{page}"
    return hashlib.md5(key_string.encode()).hexdigest()


def load_from_cache(cache_key):
    """Load cached results if they exist."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    return None


def save_to_cache(cache_key, data):
    """Save results to cache."""
    cache_file = CACHE_DIR / f"{cache_key}.json"
    with open(cache_file, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# DISCOVERY WITH CACHING
# ============================================================================

def discover_platform_with_cache(platform_name, keyword_bundles, max_pages):
    """Run discovery for a platform with caching."""
    print(f"\n📊 {platform_name.upper()}")
    print("─" * 80)
    
    search_func = PLATFORM_SEARCH_FUNCTIONS[platform_name]
    all_identifiers = []
    cache_hits = 0
    cache_misses = 0
    
    for i, bundle_config in enumerate(keyword_bundles, 1):
        keywords = bundle_config["keywords"]
        # Clamp pages to our test maximum
        pages = min(bundle_config["pages"], max_pages)
        
        print(f"  Bundle {i}/{len(keyword_bundles)}: {keywords[:60]}...")
        
        for page in range(pages):
            cache_key = get_cache_key(platform_name, keywords, page)
            
            # Try cache first
            cached_data = load_from_cache(cache_key)
            if cached_data is not None:
                identifiers = cached_data
                cache_hits += 1
                print(f"    Page {page + 1}/{pages} [CACHED] → {len(identifiers)} results")
            else:
                # Make API call
                start = page * 10
                identifiers = search_func(keywords, start)
                save_to_cache(cache_key, identifiers)
                cache_misses += 1
                print(f"    Page {page + 1}/{pages} [API CALL] → {len(identifiers)} results")
                time.sleep(SEARCH_DELAY)
            
            all_identifiers.extend(identifiers)
    
    print(f"  Cache: {cache_hits} hits, {cache_misses} misses")
    print(f"  Total raw results: {len(all_identifiers)}")
    
    return all_identifiers


# ============================================================================
# MAIN BENCHMARK RUNNER
# ============================================================================

def run_benchmark():
    """Run benchmark tests and output results."""
    print("=" * 80)
    print("NETWORK BUILDER - BENCHMARK MODE")
    print("=" * 80)
    print(f"Topics: {TEST_TOPICS}")
    print(f"Platforms: {TEST_PLATFORMS}")
    print(f"Max pages per bundle: {MAX_PAGES_PER_BUNDLE}")
    print(f"Scope: {SCOPE}")
    print("=" * 80)
    
    all_results = []
    
    for topic in TEST_TOPICS:
        print(f"\n\n{'='*80}")
        print(f"🎯 TOPIC: {topic}")
        print(f"{'='*80}")
        
        # Generate search strategy
        print(f"\n📝 Generating search strategy...")
        strategy = generate_search_strategy(topic, SCOPE, user_keywords=None)
        
        print(f"   Strategy: {strategy.get('classification', 'N/A')}")
        print(f"   Bundles: {len(strategy['bundles'])}")
        print(f"   Threshold: {strategy['threshold']}")
        
        keyword_bundles = strategy["bundles"]
        threshold = strategy["threshold"]
        
        # Determine platforms
        platforms_to_test = TEST_PLATFORMS
        if "all" in [p.lower() for p in TEST_PLATFORMS]:
            platforms_to_test = list(PLATFORM_SEARCH_FUNCTIONS.keys())
        
        # Run discovery for each platform
        topic_results = {
            "topic": topic,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform_name in platforms_to_test:
            raw_identifiers = discover_platform_with_cache(
                platform_name, 
                keyword_bundles, 
                MAX_PAGES_PER_BUNDLE
            )
            
            # Apply threshold filtering
            filtered_results = aggregate_and_filter(
                raw_identifiers, 
                threshold, 
                TOP_N_RESULTS
            )
            
            # Store results
            topic_results["platforms"][platform_name] = {
                "raw_count": len(raw_identifiers),
                "unique_count": len(set(raw_identifiers)),
                "filtered_count": len(filtered_results),
                "threshold": threshold,
                "results": [
                    {"identifier": id, "count": count} 
                    for id, count in filtered_results
                ]
            }
            
            # Print summary
            print(f"  ✅ Filtered: {len(filtered_results)} accounts (threshold={threshold})")
        
        all_results.append(topic_results)
    
    # ========================================================================
    # OUTPUT RESULTS
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("📊 BENCHMARK RESULTS")
    print("="*80)
    
    # Terminal table output
    for result in all_results:
        topic = result["topic"]
        print(f"\n\n🎯 {topic}")
        print("─" * 80)
        
        for platform_name, platform_data in result["platforms"].items():
            print(f"\n  {platform_name.upper()}: {platform_data['filtered_count']} results (threshold={platform_data['threshold']})")
            print("  " + "─" * 76)
            
            if platform_data["results"]:
                print(f"  {'Rank':<6} {'Identifier':<50} {'Count':<8}")
                print("  " + "─" * 76)
                
                for rank, item in enumerate(platform_data["results"][:10], 1):  # Show top 10
                    identifier = item["identifier"][:48]  # Truncate long identifiers
                    count = item["count"]
                    print(f"  {rank:<6} {identifier:<50} {count:<8}")
                
                if len(platform_data["results"]) > 10:
                    print(f"  ... and {len(platform_data['results']) - 10} more")
            else:
                print("  No results found.")
    
    # JSON dump
    output_filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_filename, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n\n" + "="*80)
    print(f"✅ Full results saved to: {output_filename}")
    print("="*80)
    
    # Summary stats
    total_platforms = sum(len(r["platforms"]) for r in all_results)
    total_accounts = sum(
        p["filtered_count"] 
        for r in all_results 
        for p in r["platforms"].values()
    )
    
    print(f"\n📈 Summary:")
    print(f"   Topics tested: {len(all_results)}")
    print(f"   Platform searches: {total_platforms}")
    print(f"   Total accounts found: {total_accounts}")
    print(f"   Cache directory: {CACHE_DIR.absolute()}")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    run_benchmark()