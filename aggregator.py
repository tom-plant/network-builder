# aggregator.py
# Count appearances and filter results

from collections import Counter

def aggregate_and_filter(identifiers, threshold, top_n):
    """Count appearances and filter by threshold.
    
    Args:
        identifiers: List of account identifiers (with duplicates)
        threshold: Minimum appearances required
        top_n: Maximum results to return (None = no limit)
    """
    counter = Counter(identifiers)
    filtered = {id: count for id, count in counter.items() if count >= threshold}
    sorted_results = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
    
    # If top_n is None, return all results
    if top_n is None:
        return sorted_results
    else:
        return sorted_results[:top_n]

def display_results(platform_name, results):
    """Pretty print results for a platform."""
    print(f"\n{'='*80}")
    print(f"🎯 {platform_name.upper()}: {len(results)} results")
    print('='*80)
    
    if not results:
        print("No results found matching the threshold.")
        return
    
    print(f"\n{'Rank':<6} {'Identifier':<35} {'Appearances':<12} {'Notes'}")
    print("-" * 80)
    
    for rank, (identifier, count) in enumerate(results, 1):
        notes = f"Appeared {count}x in last 30 days"
        print(f"{rank:<6} {identifier:<35} {count:<12} {notes}")