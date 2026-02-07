# keyword_generator.py
# Generate keyword bundles using Claude

from anthropic import Anthropic
from config import CLAUDE_KEY
import json

def generate_search_strategy(topic, scope="auto", user_keywords=None):
    """Generate adaptive search strategy based on topic scope and user hints."""
    print(f"\n🔄 Generating search strategy for: {topic}")
    
    client = Anthropic(api_key=CLAUDE_KEY)
    
    # Build prompt based on scope
    if scope == "auto":
        prompt = _build_auto_prompt(topic, user_keywords)
    elif scope.upper() == "A":
        prompt = _build_deep_prompt(topic, user_keywords)
    else:  # scope == "B"
        prompt = _build_wide_prompt(topic, user_keywords)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = message.content[0].text.strip()
    
    # Parse JSON response with fallback
    try:
        strategy = _parse_strategy_response(response_text)
        strategy = _normalize_strategy(strategy, scope)  # NEW: Normalize before validation
        _validate_and_clamp_strategy(strategy)
    except Exception as e:
        print(f"⚠️  Error parsing LLM response, using safe defaults: {e}")
        print(f"Raw response: {response_text[:200]}...")
        strategy = _get_fallback_strategy(topic, scope)
    
    # Display generated strategy
    print(f"✅ Generated {len(strategy['bundles'])} keyword bundles")
    for i, bundle in enumerate(strategy['bundles'], 1):
        print(f"   Bundle {i}: {bundle['keywords']} ({bundle['pages']} pages)")
    print(f"   Threshold: {strategy['threshold']}+ appearances")
    if strategy.get('apply_news_filter', False):
        print(f"   🔇 News filter: ACTIVE (event-based query detected)")
    
    return strategy


def _build_auto_prompt(topic, user_keywords):
    """Build prompt that asks LLM to classify and generate."""
    user_hint = f"\n\n**USER-PROVIDED KEYWORDS:** {user_keywords}\nInclude these in at least one bundle, but do not let them replace the core topic or violate post-language rules." if user_keywords else ""
    
    return f"""You are designing a search strategy to discover social media accounts that CONSISTENTLY POST about a specific topic.

**THE MISSION:**
Find accounts posting frequently enough about "{topic}" that they appear 2-3+ times in search results from the last 30 days. These accounts are worth tracking because they reliably create content about this topic.

**HOW IT WORKS:**
We search Google for social media posts (Twitter, Reddit, Instagram, TikTok, YouTube, Facebook, Telegram) from the past 30 days using keyword queries. When an account appears multiple times across search results, it signals consistent posting behavior.{user_hint}

---

## STEP 1: CLASSIFY THE TOPIC

**YOU MUST set "classification" to either "DEEP" or "WIDE" in your JSON output.**

Use this decision rubric:

**DEEP →** Specific person/team/product/show with dedicated following
- Clear primary term people explicitly mention
- Dedicated accounts exist that focus mainly on this
- Examples: "Kendrick Lamar", "Denver Broncos", "Tesla Model 3", "Joe Rogan podcast"

**WIDE →** Multifaceted issue discussed from many different angles  
- No single term fully captures the discussion
- Multiple communities approach from different perspectives
- Examples: "South China Sea disputes", "remote work culture", "AI safety concerns"

**Edge case rule:** If fewer than 5-10 dedicated accounts would exist for this exact phrase → WIDE
- Example: "climate anxiety" SEEMS specific but needs WIDE (few accounts focus solely on this phrase; sentiment appears across activism, mental health, eco-grief discussions)

---

## STEP 2: GENERATE KEYWORD BUNDLES

**CRITICAL PRINCIPLE: Use words that appear IN ACTUAL SOCIAL MEDIA POSTS**

Think like a social media user searching for content. What keywords would you SEE in:
- Twitter posts and replies
- Reddit thread titles
- Instagram captions
- TikTok video descriptions

❌ **BAD (Analytical meta-language):**
- "South China Sea regional perspectives territorial claims"
- "climate change policy implications and stakeholder views"  
- "technology adoption challenges and opportunities"

Why bad? Words like "perspectives," "implications," "stakeholders" are ANALYTICAL. People don't post these words. They're how researchers DESCRIBE discussions, not how people HAVE discussions.

✅ **GOOD (Conversational post language):**
- "South China Sea China Philippines military disputed islands"
- "climate change anxiety fear future generations"
- "remote work productivity collaboration tools burnout"

Why good? These are words that actually appear in posts about these topics.

---

## DEEP STRATEGY OUTPUT (2-3 bundles)

**Funnel Approach:** Start tight, expand gradually

**Bundle 1 - Primary Term (Deep Dive):**
- Use the EXACT main term people post
- This is the bulls-eye
- Paginate heavily (12-15 pages)
- Example: "Kendrick Lamar"

**Bundle 2 - Variants (Medium Depth):**
- Primary term + common nicknames/abbreviations/alternate names
- Still focused, just catching variant usage
- Paginate moderately (6-8 pages)
- Example: "Kendrick Lamar OR Kendrick OR K.Dot"

**Bundle 3 - Broader Context (Optional, Light Depth):**
- **CRITICAL CONSTRAINT:** Bundle 3 must still target accounts whose PRIMARY FOCUS is the original topic
- Do NOT center on adjacent entities (labels, companies, related shows) that have their own separate communities
- Only include if it meaningfully captures accounts focused on the core topic
- Paginate lightly (3-5 pages)
- Example for "Kendrick Lamar": Could add "Kendrick Lamar OR pgLang" ONLY if pgLang accounts primarily post about Kendrick
- Often NOT needed - if topic is specific enough, 2 bundles suffice

**Bad Bundle 3 examples:**
- For "Kendrick Lamar": "TDE OR Top Dawg Entertainment" → catches label-focused accounts posting about OTHER artists
- For "Denver Broncos": "Russell Wilson OR Sean Payton" → catches fans of these individuals from OTHER teams

**Rules:**
- 2-3 bundles maximum (often 2 is best)
- Pagination decreases: Bundle 1 > Bundle 2 > Bundle 3
- Total pages: ~20-25 across all bundles
- Threshold: 2 (accounts need 2+ appearances)

**Examples:**

Topic: "Kendrick Lamar"
```
Bundle 1: "Kendrick Lamar" (15 pages)
Bundle 2: "Kendrick Lamar OR Kendrick OR K.Dot" (8 pages)
```

Topic: "Denver Broncos"  
```
Bundle 1: "Denver Broncos" (15 pages)
Bundle 2: "Denver Broncos OR Broncos" (8 pages)
```
(No Bundle 3 needed - specific enough already)

Topic: "Tesla Cybertruck"
```
Bundle 1: "Tesla Cybertruck" (15 pages)
Bundle 2: "Tesla Cybertruck OR Cybertruck" (8 pages)
Bundle 3: "Tesla Cybertruck OR Elon Musk truck" (4 pages)
```

---

## WIDE STRATEGY OUTPUT (3-5 bundles)

**Multi-Angle Approach:** Capture different discussion contexts

Each bundle represents a different realistic way people discuss this topic:
- Use conversational language from actual posts
- Include core topic in EVERY bundle (don't drift away from the topic)
- Balance pagination (3-5 pages per bundle)

**Ask yourself:** "What are the different CONTEXTS in which people post about this?"
- Different communities (activists, industry, consumers)
- Different dimensions (military, economic, environmental)
- Different emotions/attitudes (worried, hopeful, critical)

**Rules:**
- 3-5 bundles (capture diverse angles)
- **Use OR operators for flexible matching** (see examples below)
- Balanced pagination: 3-5 pages per bundle
- Total pages: ~15-20 across all bundles
- Threshold: 3 (accounts need 3+ appearances)
- Core topic term appears in EVERY bundle
- **Include foreign language bundle if topic is regional/geopolitical**

**Examples:**

Topic: "South China Sea"
```
Bundle 1: "South China Sea (China OR Philippines OR Vietnam) (military OR navy)" (5 pages)
Bundle 2: "South China Sea (Spratly OR Paracel OR Scarborough) (disputed OR claimed)" (4 pages)
Bundle 3: "South China Sea (fishing OR oil OR gas OR resources)" (4 pages)
Bundle 4: "南海 OR 南中国海 OR South China Sea (中国 OR 菲律宾 OR 越南)" (3 pages)
```
Note: OR operators create flexibility, multilingual bundle captures regional voices

Topic: "climate anxiety"
```
Bundle 1: "climate (anxiety OR stress OR worry OR fear) (mental health OR therapy)" (5 pages)
Bundle 2: "climate crisis (doom OR hopeless OR dread) (future OR generation)" (4 pages)
Bundle 3: "climate action (activism OR hope OR solutions OR community)" (4 pages)
Bundle 4: "eco anxiety (young people OR youth OR gen z) (coping OR therapy)" (4 pages)
```

Topic: "remote work culture"
```
Bundle 1: "remote work (productivity OR collaboration OR tools OR zoom)" (5 pages)
Bundle 2: "remote work (burnout OR isolation OR loneliness OR mental health)" (4 pages)
Bundle 3: "remote work (office return OR hybrid OR policy)" (4 pages)
Bundle 4: "remote work (digital nomad OR travel OR lifestyle)" (3 pages)
```

---

## OUTPUT FORMAT

**REQUIRED: You MUST return valid JSON with "classification" set to "DEEP" or "WIDE".**

Return ONLY valid JSON (no markdown code blocks):

```
{{
  "classification": "DEEP" or "WIDE",
  "reasoning": "1-2 sentences explaining why this classification and strategy",
  "bundles": [
    {{"keywords": "term1 OR term2 OR term3", "pages": 8}},
    {{"keywords": "term1 OR term4 OR term5", "pages": 6}}
  ],
  "threshold": 2
}}
```

**Final checklist before responding:**
✓ "classification" field is set to "DEEP" or "WIDE"
✓ Keywords sound like actual post language (not analytical jargon)
✓ DEEP: Pagination decreases across bundles (funnel)
✓ DEEP: Bundle 3 (if present) still focuses on core topic, not adjacent entities
✓ WIDE: Core topic appears in every bundle
✓ WIDE: Bundles use OR operators for flexible matching
✓ WIDE: Foreign language bundle included if topic is regional/geopolitical
✓ Total pages ≤ 30
✓ Threshold: 2 for DEEP, 3 for WIDE
✓ Valid JSON only (no markdown)

Now generate the strategy for: "{topic}"
"""


def _build_deep_prompt(topic, user_keywords):
    """Build prompt for deep/focused search."""
    user_hint = f"\n\n**USER-PROVIDED KEYWORDS:** {user_keywords}\nInclude these in at least one bundle, but do not let them replace the core topic or violate post-language rules." if user_keywords else ""
    
    return f"""Generate a DEEP search strategy to find accounts that consistently post about: "{topic}"{user_hint}

**CONTEXT:**
This is a focused topic (specific person/brand/product/entity) that likely has dedicated fan accounts, enthusiast communities, or focused creators. We need tight, high-signal keywords with deep pagination to find accounts posting frequently enough to appear multiple times in search results.

**YOUR TASK:**
Create 2-3 keyword bundles using the FUNNEL APPROACH:
1. Start with the tightest, most specific primary term
2. Expand to include common variants
3. Optionally add broader related terms (only if they still focus on the core topic)

---

## BUNDLE DESIGN PRINCIPLES

**Bundle 1 - Primary Term (The Bulls-Eye):**
- Use the EXACT term people post when discussing this topic
- This is the most direct, high-signal keyword
- Paginate deeply (12-15 pages) to find frequent posters
- Example: "Kendrick Lamar", "Denver Broncos", "Tesla Cybertruck"

**Bundle 2 - Variants (The Near Circle):**
- Primary term + nicknames, abbreviations, alternate names
- These are just different ways to reference the same thing
- Still tight and focused, not different angles
- Paginate moderately (6-8 pages)
- Examples:
  - "Kendrick Lamar OR Kendrick OR K.Dot"
  - "Denver Broncos OR Broncos"
  - "Joe Rogan podcast OR JRE"

**Bundle 3 - Broader Context (Optional, The Outer Ring):**
- **CRITICAL CONSTRAINT:** This bundle must STILL target accounts whose PRIMARY FOCUS is the original topic
- Do NOT include adjacent entities (labels, companies, related people) that have separate fan communities
- Only create if it captures accounts genuinely focused on the core topic, just using broader language
- Paginate lightly (3-5 pages)

**Why this constraint matters:**
- Bad: "TDE OR Top Dawg Entertainment" for Kendrick → catches label accounts posting about Schoolboy Q, Jay Rock, etc.
- Bad: "Russell Wilson OR Sean Payton" for Broncos → catches Seahawks fans, Saints fans
- Good: "Tesla Cybertruck OR Elon Musk truck" → still specifically about the Cybertruck

**Often Bundle 3 is NOT needed** - if the topic is specific enough, 2 bundles are sufficient.

---

## KEYWORD QUALITY RULES

✓ **Use post language, not analytical language:**
- Good: "Kendrick Lamar", "K.Dot", "Kendrick"
- Bad: "hip hop artist perspectives", "rap music discourse"

✓ **Avoid different angles in DEEP searches:**
- Bad example for "Kendrick Lamar":
  - Bundle 1: "Kendrick Lamar"
  - Bundle 2: "To Pimp a Butterfly OR DAMN OR good kid"
  - Why bad? These are different ASPECTS (albums vs artist name), not variants
- Albums might be discussed by music critics who don't focus on Kendrick
- Keep it tight: variants of the same core concept

✓ **Think about who would post this:**
- Dedicated fan accounts → will use the primary term frequently
- Casual fans → might use nicknames
- News/media → will use official name

---

## OUTPUT RULES

- **2-3 bundles maximum** (often 2 is enough)
- **Decreasing pagination:** Bundle 1 > Bundle 2 > Bundle 3
- **Total pages: ~20-25** across all bundles
- **Threshold: 2** (account needs 2+ appearances)
- **Output valid JSON only** (no markdown code blocks)

```
{{
  "bundles": [
    {{"keywords": "primary exact term", "pages": 15}},
    {{"keywords": "primary exact term OR variant1 OR variant2", "pages": 8}}
  ],
  "threshold": 2,
  "reasoning": "Brief explanation of keyword choices",
  "apply_news_filter": false
}}
```

**Examples:**

For "Kendrick Lamar":
```
{{
  "bundles": [
    {{"keywords": "Kendrick Lamar", "pages": 15}},
    {{"keywords": "Kendrick Lamar OR Kendrick OR K.Dot", "pages": 8}}
  ],
  "threshold": 2,
  "reasoning": "Funnel from exact name to common variants used by fans",
  "apply_news_filter": false
}}
```

For "Denver Broncos":
```
{{
  "bundles": [
    {{"keywords": "Denver Broncos", "pages": 15}},
    {{"keywords": "Denver Broncos OR Broncos", "pages": 8}}
  ],
  "threshold": 2,
  "reasoning": "Team name and shortened version, specific enough without broader context",
  "apply_news_filter": false
}}
```

**Final checklist:**
✓ 2-3 bundles max
✓ Pagination decreases (funnel)
✓ Bundle 3 (if present) still focuses on core topic, not adjacent entities
✓ Post language, not analytical jargon
✓ Threshold: 2
✓ Valid JSON only

Now generate the DEEP strategy for: "{topic}"
"""


def _build_wide_prompt(topic, user_keywords):
    """Build prompt for wide/multifaceted search."""
    user_hint = f"\n\n**USER-PROVIDED KEYWORDS:** {user_keywords}\nInclude these in at least one bundle, but do not let them replace the core topic or violate post-language rules." if user_keywords else ""
    
    return f"""Generate a WIDE search strategy to find accounts discussing different aspects of: "{topic}"{user_hint}

**CONTEXT:**  
This is a multifaceted topic discussed by diverse communities from different perspectives. We need multiple realistic discussion angles to capture the full conversation landscape. No single keyword bundle will capture all the accounts worth tracking.

**YOUR TASK:**
Create 3-5 keyword bundles, where each bundle represents a different REALISTIC way people naturally discuss this topic on social media.

---

## THE MULTI-ANGLE APPROACH

Think about:
- **Different communities:** Who talks about this? (activists, professionals, consumers, enthusiasts)
- **Different dimensions:** What aspects exist? (political, economic, environmental, social)
- **Different contexts:** When/why do people post? (news events, personal experiences, debates)

**ASK YOURSELF:**
"If I searched Twitter/Reddit right now for this topic, what different TYPES of posts would I see?"

---

## BUNDLE DESIGN PRINCIPLES

Each bundle should:
1. **Represent a distinct discussion context** - not just random keyword variations
2. **Use conversational post language** - words that appear in actual posts
3. **Include the core topic** - don't drift into tangential areas
4. **Feel like a realistic search** - something a human would actually search

**Balanced pagination:**
- 3-5 pages per bundle
- Total ~15-20 pages across all bundles
- Captures breadth without going too shallow

---

## KEYWORD QUALITY RULES

❌ **AVOID Analytical Meta-Language:**

Bad examples:
- "South China Sea regional perspectives territorial claims"
  - Why? "Perspectives" and "claims" are analytical framing words
  - Nobody posts: "Here's my perspective on territorial claims"
  
- "climate change policy implications stakeholder engagement"
  - Why? "Implications" and "stakeholder" are academic jargon
  - People don't talk like policy briefs

- "technology adoption challenges and opportunities"
  - Why? "Adoption challenges and opportunities" is consultant-speak
  - Real people say: "I tried this app and it's confusing"

✅ **USE Conversational Post Language:**

Good examples:
- "South China Sea China Philippines military disputed islands"
  - These words appear in actual posts about SCS tensions
  
- "climate change anxiety fear future generations young people"
  - This is how people express climate anxiety in posts
  
- "remote work burnout isolation mental health tired"
  - Real language people use discussing remote work struggles

**The test:** Would you see these exact words in a Twitter post, Reddit title, or Instagram caption?

---

## USING OR OPERATORS FOR FLEXIBLE SEARCHES

**CRITICAL:** WIDE bundles must use OR operators to create flexible, high-yield searches.

**Why this matters:**
Without OR operators, Google requires ALL terms to appear in a single post. This is extremely restrictive and causes pagination to exhaust quickly (you'll see "0 results" after page 1-2).

❌ **Bad (AND logic - too restrictive):**
```
South China Sea China Philippines Vietnam military tensions
```
Problem: Post must contain ALL 6+ terms → Very few posts qualify → Pagination exhausts

✅ **Good (OR logic - flexible):**
```
South China Sea (China OR Philippines OR Vietnam) (military OR navy OR defense)
```
Benefit: Post needs core topic + any country + any military term → Many posts qualify → Pagination works

**Pattern to follow:**
```
[core_topic] ([option1] OR [option2] OR [option3]) [dimension]
```

**More examples:**

Topic: "South China Sea"
- ✅ "South China Sea (Spratly OR Paracel OR Scarborough) (disputed OR claimed OR territory)"
- ✅ "South China Sea (fishing OR oil OR gas OR resources) (China OR Philippines)"
- ❌ "South China Sea Spratly Paracel islands disputed territory claims" (no ORs)

Topic: "climate anxiety"
- ✅ "climate (anxiety OR stress OR worry OR fear) (young people OR generation OR youth)"
- ✅ "climate crisis (doom OR hopeless OR dread OR despair) future"
- ❌ "climate anxiety stress worry fear young people" (no ORs)

Topic: "remote work culture"
- ✅ "remote work (burnout OR isolation OR loneliness OR mental health)"
- ✅ "remote work (productivity OR collaboration OR tools OR zoom OR slack)"
- ❌ "remote work burnout isolation mental health wellbeing" (no ORs)

**When to use OR:**
- When listing alternative entities (countries, companies, people)
- When listing related concepts (military/navy/defense, anxiety/stress/worry)
- When listing related actions (disputed/claimed/contested)

---

## FOREIGN LANGUAGE SUPPORT FOR REGIONAL TOPICS

**For geopolitical, regional, or culturally-specific topics:** Include at least one bundle with relevant local languages to capture regional voices and communities.

**When to add foreign language bundles:**
- Geopolitical issues involving specific countries/regions
- Cultural topics with strong non-English speaking communities
- Regional conflicts, policies, or movements
- Topics where local perspectives are essential

**How to structure multilingual bundles:**
```
[native_terms] OR [native_terms] OR [english_equivalent]
```

**Examples:**

Topic: "South China Sea"
```
Bundle: "南海 OR 南中国海 OR South China Sea (中国 OR 菲律宾 OR 越南)"
```
Captures: Chinese-language discussions from China, Taiwan, regional communities

Topic: "Brazil climate policy"
```
Bundle: "Brasil clima (política OR Amazônia OR desmatamento) OR Brazil climate policy"
```
Captures: Portuguese-language Brazilian discussions + English coverage

Topic: "Ukraine war"
```
Bundle: "Україна війна OR Ukraine war (Росія OR Russia)"
```
Captures: Ukrainian and Russian-language discussions

**Guidelines:**
- Use native scripts (Chinese characters, Cyrillic, etc.)
- Include OR with English equivalent for cross-language coverage
- Place these bundles later in sequence (3-5 pages pagination)
- Only add if topic has clear regional/cultural dimension

---

## ENSURING DIVERSE ANGLES

**Don't just split synonyms:**
Bad: All bundles say the same thing with different words
```
Bundle 1: "South China Sea disputes conflicts tensions"
Bundle 2: "South China Sea disagreements issues problems"  
Bundle 3: "South China Sea controversy debate arguments"
```
This is just thesaurus swapping - not different angles.

**Do capture different discussion contexts:**
Good: Each bundle targets a distinct aspect people discuss
```
Bundle 1: "South China Sea China Philippines Vietnam military"
Bundle 2: "South China Sea Spratly Paracel islands disputed territory"  
Bundle 3: "South China Sea fishing resources oil gas"
Bundle 4: "South China Sea navy coast guard vessels tensions"
```
These represent: military dimension, territorial specifics, economic resources, naval operations.

---

## CORE TOPIC REQUIREMENT

**CRITICAL:** The core topic must appear in EVERY bundle.

Why? Without it, bundles drift into tangential discussions.

❌ **Bad example** for "South China Sea":
```
Bundle 3: "trade routes shipping lanes economic importance"
```
Problem: No mention of "South China Sea" or "China" - this would return generic trade discussions.

✅ **Good example:**
```
Bundle 3: "South China Sea fishing resources oil gas"
```
Core topic present + specific dimension = stays focused.

---

## OUTPUT RULES

- **3-5 bundles** (capture multiple angles without fragmenting)
- **Balanced pagination:** 3-5 pages per bundle
- **Total pages: ~15-20** across all bundles
- **Threshold: 3** (account needs 3+ appearances - higher bar for wide nets)
- **Output valid JSON only** (no markdown code blocks)

```
{{
  "bundles": [
    {{"keywords": "core_topic angle1_terms", "pages": 5}},
    {{"keywords": "core_topic angle2_terms", "pages": 4}},
    {{"keywords": "core_topic angle3_terms", "pages": 4}},
    {{"keywords": "core_topic angle4_terms", "pages": 3}}
  ],
  "threshold": 3,
  "reasoning": "Brief explanation of the different angles",
  "apply_news_filter": false
}}
```

---

## EXAMPLES

**Topic: "South China Sea"**
```
{{
  "bundles": [
    {{"keywords": "South China Sea (China OR Philippines OR Vietnam OR Malaysia) (military OR navy OR defense)", "pages": 5}},
    {{"keywords": "South China Sea (Spratly OR Paracel OR Scarborough) (disputed OR claimed OR territory)", "pages": 4}},
    {{"keywords": "South China Sea (fishing OR oil OR gas OR resources)", "pages": 4}},
    {{"keywords": "南海 OR 南中国海 OR South China Sea (中国 OR 菲律宾 OR 越南)", "pages": 3}}
  ],
  "threshold": 3,
  "reasoning": "Four angles: military dimension with country options, territorial specifics, economic resources, Chinese-language regional discussions",
  "apply_news_filter": true
}}
```

**Topic: "climate anxiety"**
```
{{
  "bundles": [
    {{"keywords": "climate (anxiety OR stress OR worry OR fear) (mental health OR therapy)", "pages": 5}},
    {{"keywords": "climate crisis (doom OR hopeless OR dread OR despair) (future OR generation)", "pages": 4}},
    {{"keywords": "climate action (activism OR hope OR solutions OR community)", "pages": 4}},
    {{"keywords": "eco anxiety (young people OR youth OR gen z OR millennials) (coping OR therapy)", "pages": 4}}
  ],
  "threshold": 3,
  "reasoning": "Four contexts: mental health dimension, existential feelings, action-oriented responses, youth-specific experience",
  "apply_news_filter": true
}}
```

**Topic: "remote work culture"**
```
{{
  "bundles": [
    {{"keywords": "remote work (productivity OR collaboration OR tools OR zoom OR slack)", "pages": 5}},
    {{"keywords": "remote work (burnout OR isolation OR loneliness OR mental health)", "pages": 4}},
    {{"keywords": "remote work (office return OR hybrid OR policy OR debate)", "pages": 4}},
    {{"keywords": "remote work (digital nomad OR travel OR living OR lifestyle)", "pages": 3}}
  ],
  "threshold": 3,
  "reasoning": "Four discussions: work effectiveness tools, wellbeing challenges, return-to-office debate, lifestyle aspects",
  "apply_news_filter": true
}}
```

---

## FILTER MAJOR NEWS OUTLETS (apply_news_filter)

**DEFAULT: true** - We almost always want to filter out major news outlets (CNN, Reuters, BBC, Bloomberg, NYTimes, etc.) to find community voices instead.

Your JSON output must include "apply_news_filter": true or false.

**Set to TRUE (default for almost all topics):**
- Geopolitical topics: "South China Sea", "Middle East politics", "Venezuela crisis"
- Social issues: "climate anxiety", "remote work culture", "teacher strikes"
- Breaking events: "Venezuela since Maduro removed", "Capitol riot response"
- Any topic where mainstream outlets would dominate results

**Set to FALSE (rare exceptions only):**
- User explicitly wants comprehensive news: "news in China", "global news coverage", "CNN BBC Reuters coverage of X"
- Topic specifically about news outlets themselves: "media coverage of elections"

If unsure, default to **true**. Our exclusion list only blocks major mainstream outlets - niche/regional/specialist news sources will still appear.

---

**Final checklist before responding:**
✓ 3-5 bundles with distinct angles
✓ Bundles use OR operators for flexible matching
✓ Core topic in every bundle
✓ Conversational language (no meta-analytical jargon)
✓ Each bundle feels like a realistic search query
✓ Foreign language bundle included if topic is regional/geopolitical
✓ Balanced pagination (3-5 pages each)
✓ Threshold: 3
✓ "apply_news_filter" field set correctly (true/false)
✓ Valid JSON only

Now generate the WIDE strategy for: "{topic}"
"""


def _parse_strategy_response(response_text):
    """Parse JSON from LLM response, handling markdown code blocks."""
    # Remove markdown code blocks if present
    text = response_text.strip()
    if text.startswith("```"):
        # Extract content between ``` markers
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        text = text.replace("```json", "").replace("```", "").strip()
    
    return json.loads(text)


def _normalize_strategy(strategy, scope):
    """
    Normalize and validate strategy structure before using it.
    
    This function ensures:
    - Required fields exist
    - Types are correct (pages is int, keywords is str)
    - Malformed bundles are dropped
    - Missing fields have sensible defaults
    
    Args:
        strategy: Raw parsed strategy dict
        scope: The scope used ("auto", "A", "B")
    
    Returns:
        Normalized strategy dict
    """
    normalized = {}
    
    # Ensure classification exists (for auto mode)
    if scope == "auto":
        if "classification" not in strategy:
            # Try to infer from threshold or bundle count
            threshold = strategy.get("threshold", 2)
            bundle_count = len(strategy.get("bundles", []))
            if threshold == 2 or bundle_count <= 2:
                normalized["classification"] = "DEEP"
            else:
                normalized["classification"] = "WIDE"
        else:
            normalized["classification"] = strategy["classification"]
    
    # Ensure reasoning exists
    normalized["reasoning"] = strategy.get("reasoning", "No reasoning provided")
    
    # Normalize bundles
    raw_bundles = strategy.get("bundles", [])
    valid_bundles = []
    
    for i, bundle in enumerate(raw_bundles):
        try:
            # Extract and validate keywords (must be string)
            keywords = bundle.get("keywords", "")
            if not isinstance(keywords, str):
                keywords = str(keywords)
            if not keywords.strip():
                print(f"   ⚠️  Skipping bundle {i+1}: empty keywords")
                continue
            
            # Extract and validate pages (must be int)
            pages = bundle.get("pages", 1)
            if isinstance(pages, str):
                pages = int(pages)
            elif not isinstance(pages, int):
                pages = int(pages)
            
            if pages < 1:
                print(f"   ⚠️  Bundle {i+1}: pages < 1, setting to 1")
                pages = 1
            
            valid_bundles.append({
                "keywords": keywords,
                "pages": pages
            })
            
        except (ValueError, TypeError) as e:
            print(f"   ⚠️  Skipping malformed bundle {i+1}: {e}")
            continue
    
    if not valid_bundles:
        raise ValueError("No valid bundles after normalization")
    
    normalized["bundles"] = valid_bundles
    
    # Normalize threshold
    threshold = strategy.get("threshold", 2)
    try:
        if isinstance(threshold, str):
            threshold = int(threshold)
        elif not isinstance(threshold, int):
            threshold = int(threshold)
    except (ValueError, TypeError):
        # Default based on scope
        if scope.upper() == "A":
            threshold = 2
        elif scope.upper() == "B":
            threshold = 3
        else:
            # Auto mode: infer from bundle count
            threshold = 2 if len(valid_bundles) <= 2 else 3
        print(f"   ⚠️  Invalid threshold, defaulting to {threshold}")
    
    normalized["threshold"] = threshold
    
    # Normalize apply_news_filter (defaults to True - we almost always want to exclude major news outlets)
    normalized["apply_news_filter"] = strategy.get("apply_news_filter", True)
    if not isinstance(normalized["apply_news_filter"], bool):
        normalized["apply_news_filter"] = False
    
    return normalized


def _validate_and_clamp_strategy(strategy):
    """Ensure strategy values are within safe limits."""
    from config import MAX_PAGES_PER_BUNDLE, MAX_TOTAL_PAGES, MIN_THRESHOLD, MAX_THRESHOLD
    
    # Clamp threshold
    if "threshold" not in strategy:
        strategy["threshold"] = 2
    strategy["threshold"] = max(MIN_THRESHOLD, min(MAX_THRESHOLD, strategy["threshold"]))
    
    # Clamp pages per bundle
    total_pages = 0
    for bundle in strategy["bundles"]:
        bundle["pages"] = max(1, min(MAX_PAGES_PER_BUNDLE, bundle["pages"]))
        total_pages += bundle["pages"]
    
    # If total exceeds limit, scale down proportionally
    if total_pages > MAX_TOTAL_PAGES:
        scale = MAX_TOTAL_PAGES / total_pages
        for bundle in strategy["bundles"]:
            bundle["pages"] = max(1, int(bundle["pages"] * scale))


def _get_fallback_strategy(topic, scope):
    """Return safe default strategy if LLM fails."""
    if scope.upper() == "A":
        # Deep search fallback
        return {
            "classification": "DEEP",
            "bundles": [
                {"keywords": topic, "pages": 15},
                {"keywords": topic, "pages": 8}
            ],
            "threshold": 2,
            "reasoning": "Fallback: using topic as primary term with funnel pagination"
        }
    else:
        # Wide search fallback (also used for auto mode failures)
        return {
            "classification": "WIDE",
            "bundles": [
                {"keywords": topic, "pages": 5},
                {"keywords": topic, "pages": 4},
                {"keywords": topic, "pages": 4},
                {"keywords": topic, "pages": 3}
            ],
            "threshold": 3,
            "reasoning": "Fallback: using topic across multiple balanced bundles"
        }


# Legacy function for backwards compatibility (if needed elsewhere)
def generate_keyword_bundles(topic):
    """DEPRECATED: Use generate_search_strategy() instead."""
    strategy = generate_search_strategy(topic, scope="B")
    return [bundle["keywords"] for bundle in strategy["bundles"]]