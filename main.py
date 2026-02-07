# main.py
# Main CLI application

from keyword_generator import generate_search_strategy
from aggregator import aggregate_and_filter, display_results
from config import TOP_N_RESULTS

# Import all platform modules
from platforms.twitter import discover_twitter
from platforms.facebook import discover_facebook
from platforms.instagram import discover_instagram
from platforms.tiktok import discover_tiktok
from platforms.youtube import discover_youtube
from platforms.reddit import discover_reddit
from platforms.telegram import discover_telegram

def main():
    print("="*80)
    print("NETWORK BUILDER v2.0 - Multi-Platform Discovery")
    print("="*80)
    
    # Get user input - Step 1: Topic
    topic = input("\n📝 What topic or issue do you want to track?\n   (e.g., 'electric vehicle policy', 'teacher strikes', 'AI safety')\n   > ").strip()
    if not topic:
        topic = "South China Sea territorial disputes"
        print(f"   (Using default: {topic})")
    
    # Get user input - Step 2: Scope
    print("\nHow should we search for this community?")
    print("  A) Deep - specific term for a niche issue, brand, product, or clear subject")
    print("  B) Wide - cast a net across multiple angles, perspectives, or dimensions")
    scope = input("  [leave blank to auto-detect]\n  > ").strip()
    if not scope:
        scope = "auto"
        print("  (Auto-detecting search strategy...)")
    
    # Get user input - Step 3: Optional keywords
    user_keywords = input("\n(Optional) Any specific keywords or terms to prioritize?\n  Examples: alternate names, phrases, hashtags\n  > ").strip()
    if not user_keywords:
        user_keywords = None
    
    # Step 1: Generate search strategy (once for all platforms)
    strategy = generate_search_strategy(topic, scope, user_keywords)
    
    # Step 2: Discover across all platforms
    results = {}
    keyword_bundles = strategy["bundles"]
    threshold = strategy["threshold"]
    apply_filter = strategy.get("apply_news_filter", False)
    
    # Accounts (using dynamic threshold)
    print("\n" + "="*80)
    print("DISCOVERING ACCOUNTS")
    print("="*80)
    
    twitter_data = discover_twitter(keyword_bundles, apply_filter=apply_filter)
    results['Twitter'] = aggregate_and_filter(twitter_data, threshold, TOP_N_RESULTS)
    
    facebook_data = discover_facebook(keyword_bundles, apply_filter=apply_filter)
    results['Facebook'] = aggregate_and_filter(facebook_data, threshold, TOP_N_RESULTS)
    
    instagram_data = discover_instagram(keyword_bundles, apply_filter=apply_filter)
    results['Instagram'] = aggregate_and_filter(instagram_data, threshold, TOP_N_RESULTS)
    
    tiktok_data = discover_tiktok(keyword_bundles, apply_filter=apply_filter)
    results['TikTok'] = aggregate_and_filter(tiktok_data, threshold, TOP_N_RESULTS)
    
    youtube_data = discover_youtube(keyword_bundles, apply_filter=apply_filter)
    results['YouTube'] = aggregate_and_filter(youtube_data, threshold, TOP_N_RESULTS)
    
    # Communities (using dynamic threshold)
    print("\n" + "="*80)
    print("DISCOVERING COMMUNITIES")
    print("="*80)
    
    reddit_data = discover_reddit(keyword_bundles, apply_filter=apply_filter)
    results['Reddit'] = aggregate_and_filter(reddit_data, threshold, TOP_N_RESULTS)
    
    telegram_data = discover_telegram(keyword_bundles, apply_filter=apply_filter)
    results['Telegram'] = aggregate_and_filter(telegram_data, threshold, TOP_N_RESULTS)
    
    # Step 3: Display all results
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    for platform, data in results.items():
        display_results(platform, data)
    
    # Summary
    total_sources = sum(len(data) for data in results.values())
    print(f"\n✅ Done! Found {total_sources} total sources across {len(results)} platforms.")
    
    # Optional: Save to CSV
    save = input("\n💾 Save all results to CSV? (y/n): ").strip().lower()
    if save == 'y':
        import csv
        filename = f"network_{topic[:30].replace(' ', '_')}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Platform', 'Identifier', 'Appearances', 'Notes'])
            for platform, data in results.items():
                for identifier, count in data:
                    writer.writerow([platform, identifier, count, f"Appeared {count}x in last 30 days"])
        print(f"   ✅ Saved to {filename}")

if __name__ == "__main__":
    main()