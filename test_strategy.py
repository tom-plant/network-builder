#!/usr/bin/env python3
# test_strategy.py
"""
Test keyword generation strategies WITHOUT calling SerpAPI

Usage:
1. Edit TEST_TOPICS below
2. Run: python test_strategy.py
3. Review the generated strategies
4. Only run full benchmark.py once strategies look good
"""

import json
from datetime import datetime

# Import the NEW keyword generator (rename file first or update import)
from keyword_generator import generate_search_strategy

# ============================================================================
# CONFIGURATION - EDIT THESE
# ============================================================================

TEST_TOPICS = [
    # "Kendrick Lamar",
    "Middle East Politics",
    "Venezuela Migrant Crisis",
    "South China Sea",
    "climate anxiety",
    "Denver Broncos",
    "news in China",
]

# Test each with different scopes if you want
# Options: "auto", "A" (Deep), "B" (Wide)
SCOPE = "auto"

# ============================================================================
# STRATEGY TESTER
# ============================================================================

def test_strategies():
    """Test LLM strategy generation without SerpAPI calls."""
    
    print("=" * 80)
    print("STRATEGY GENERATION TEST")
    print("=" * 80)
    print(f"Testing {len(TEST_TOPICS)} topics")
    print(f"Scope: {SCOPE}")
    print("=" * 80)
    
    all_results = []
    
    for i, topic in enumerate(TEST_TOPICS, 1):
        print(f"\n\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_TOPICS)}: {topic}")
        print('=' * 80)
        
        try:
            # Generate strategy (this calls Claude API but not SerpAPI)
            strategy = generate_search_strategy(topic, SCOPE, user_keywords=None)
            
            # Pretty print the strategy
            print(f"\n📋 GENERATED STRATEGY:")
            print(f"   Classification: {strategy.get('classification', 'N/A')}")
            print(f"   Reasoning: {strategy.get('reasoning', 'N/A')}")
            print(f"   Threshold: {strategy['threshold']}")
            print(f"   Total Bundles: {len(strategy['bundles'])}")
            
            total_pages = sum(b['pages'] for b in strategy['bundles'])
            print(f"   Total Pages: {total_pages}")
            print(f"   News Filter: {'🔇 ACTIVE' if strategy.get('apply_news_filter', False) else '✓ Inactive'}")
            
            print(f"\n   BUNDLES:")
            for j, bundle in enumerate(strategy['bundles'], 1):
                print(f"      {j}. [{bundle['pages']} pages] {bundle['keywords']}")
            
            # Validation checks
            print(f"\n✅ VALIDATION CHECKS:")
            
            issues = validate_strategy(strategy, topic, SCOPE)
            if not issues:
                print("   ✓ All checks passed!")
            else:
                print("   ⚠️  Issues found:")
                for issue in issues:
                    print(f"      - {issue}")
            
            # Store for JSON output
            all_results.append({
                "topic": topic,
                "scope": SCOPE,
                "strategy": strategy,
                "validation_issues": issues,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"\n❌ ERROR generating strategy: {e}")
            all_results.append({
                "topic": topic,
                "scope": SCOPE,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    # Save to JSON for review
    output_file = f"strategy_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in all_results if 'strategy' in r)
    failed = len(all_results) - successful
    
    print(f"   Successful: {successful}/{len(TEST_TOPICS)}")
    print(f"   Failed: {failed}/{len(TEST_TOPICS)}")
    print(f"\n   Saved to: {output_file}")
    print("=" * 80)


def validate_strategy(strategy, topic, scope):
    """Validate strategy against our requirements."""
    issues = []
    
    # Check basic structure
    if 'bundles' not in strategy or not strategy['bundles']:
        issues.append("No bundles generated")
        return issues
    
    if 'threshold' not in strategy:
        issues.append("No threshold specified")
    
    # Get classification (might be in strategy or need to infer from scope)
    classification = strategy.get('classification', scope.upper() if scope != "auto" else None)
    
    # Deep-specific checks
    if classification == "DEEP" or scope.upper() == "A":
        if len(strategy['bundles']) > 3:
            issues.append(f"Deep should have 2-3 bundles max (has {len(strategy['bundles'])})")
        
        # Check funnel pagination (pages should decrease)
        pages = [b['pages'] for b in strategy['bundles']]
        if pages != sorted(pages, reverse=True):
            issues.append(f"Pagination should decrease (funnel): got {pages}")
        
        # Check threshold
        if strategy['threshold'] != 2:
            issues.append(f"Deep threshold should be 2 (got {strategy['threshold']})")
    
    # Wide-specific checks
    elif classification == "WIDE" or scope.upper() == "B":
        if not (3 <= len(strategy['bundles']) <= 5):
            issues.append(f"Wide should have 3-5 bundles (has {len(strategy['bundles'])})")
        
        # Check threshold
        if strategy['threshold'] != 3:
            issues.append(f"Wide threshold should be 3 (got {strategy['threshold']})")
        
        # Check if core topic appears in all bundles
        # Extract likely core terms from topic
        core_terms = extract_core_terms(topic)
        for i, bundle in enumerate(strategy['bundles'], 1):
            keywords_lower = bundle['keywords'].lower()
            if not any(term.lower() in keywords_lower for term in core_terms):
                issues.append(f"Bundle {i} missing core topic: {bundle['keywords'][:50]}...")
    
    # General checks
    total_pages = sum(b['pages'] for b in strategy['bundles'])
    if total_pages > 30:
        issues.append(f"Total pages exceeds 30 (got {total_pages})")
    
    # Check news filter logic
    apply_filter = strategy.get('apply_news_filter', False)
    topic_lower = topic.lower()
    event_keywords = ['since', 'after', 'following', 'removal', 'removed', 'arrest', 'was', 'got']
    has_event_language = any(keyword in topic_lower for keyword in event_keywords)
    
    if apply_filter and not has_event_language:
        issues.append(f"News filter applied but no event language detected in topic")
    if not apply_filter and has_event_language and classification == "WIDE":
        issues.append(f"Event language detected but news filter NOT applied (may be intentional)")
        
    # Check for analytical jargon (red flags)
    jargon_words = ['perspective', 'implication', 'stakeholder', 'framework', 
                    'paradigm', 'discourse', 'narrative', 'engagement']
    for i, bundle in enumerate(strategy['bundles'], 1):
        keywords_lower = bundle['keywords'].lower()
        found_jargon = [w for w in jargon_words if w in keywords_lower]
        if found_jargon:
            issues.append(f"Bundle {i} contains analytical jargon: {found_jargon}")
    
    return issues


def extract_core_terms(topic):
    """Extract core terms from topic for validation."""
    # Simple extraction - split on spaces and take meaningful words
    words = topic.lower().split()
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'}
    core_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Also keep full phrases for multi-word topics
    return [topic] + core_words


if __name__ == "__main__":
    test_strategies()