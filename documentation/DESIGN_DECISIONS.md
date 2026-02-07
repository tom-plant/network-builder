# Network Builder Design Decisions & Assumptions

This document captures the key design decisions, assumptions, and rationale behind Network Builder's architecture. Understanding these principles is essential for future optimization and feature development.

---

## Core Approach

### 30-day time window
We only search for posts from the last 30 days to identify active accounts and communities.

**Rationale:** Recent activity indicates current relevance and active community participation. Older posts may represent abandoned accounts or outdated discussions.

### Post frequency as community membership proxy
If an account appears multiple times in search results from the last 30 days, we assume it's a consistent member of that topic's community.

**Rationale:** Repeated appearances across different searches indicate genuine engagement with the topic, not just one-off mentions.

### Appearance threshold determines inclusion
- Deep searches require **2+ appearances**
- Wide searches require **3+ appearances** to be included in final results

**Rationale:** Deep searches are more focused so lower threshold is acceptable. Wide searches cast a broader net so higher threshold filters out noise.

---

## Search Strategy Classification

### Deep vs Wide search classification
Topics are categorized as either:
- **Deep:** Specific entities with dedicated followings (brands, people, products, niche topics)
- **Wide:** Multifaceted issues discussed from multiple angles (policy issues, social movements, complex topics)

Each receives different search strategies optimized for their characteristics.

### Deep search strategy: funnel pagination
For specific topics, we start with many pages on the core term and progressively fewer pages on variants.

**Example:** 6 pages → 4 pages → 2 pages

**Rationale:** The core term captures most relevant accounts. Variants catch edge cases but need less depth to avoid noise.

### Wide search strategy: balanced multi-angle approach
For complex topics, we create 3-5 keyword bundles representing different discussion contexts, with balanced pagination (2-4 pages each).

**Rationale:** Complex topics require exploring multiple perspectives. Each angle needs similar depth to capture diverse viewpoints.

### OR operators for Wide searches
Wide searches use OR operators to create flexible matching across different perspectives and terminology.

**Rationale:** Complex topics have varied terminology. OR operators cast a wide net to capture all relevant discussions.

---

## Multi-Platform Architecture

### Same strategy across all platforms
All social media platforms (Twitter, Facebook, Instagram, TikTok, YouTube, Reddit, Telegram) receive identical keyword bundles and search strategies.

**Rationale:** Discussion patterns are consistent across platforms. Different pagination per platform would add complexity without clear benefit.

### Discovery through posts, not profiles
We find accounts by searching for posts about the topic, not by searching for profile descriptions or bios.

**Rationale:** Bio keywords may be outdated or misleading. Recent posts prove current engagement with the topic.

### Account extraction from URLs
We identify accounts by parsing social media URLs in search results.

**Example:** `x.com/USERNAME/status/123` → `USERNAME`

**Rationale:** URL structure is consistent and reliable. Alternative methods (scraping, APIs) are more complex and costly.

---

## Filtering & Aggregation

### Aggregation counts all appearances equally
Each time an account appears in any search result, it counts as one appearance regardless of post engagement, followers, or other metrics.

**Rationale:** Simplifies logic and avoids bias toward large accounts. Frequency of posting is the signal we care about.

### Top 30 results per platform
We return the top 30 accounts/communities per platform, ranked by appearance count.

**Rationale:** Balances comprehensiveness with usability. 30 accounts provides good coverage without overwhelming users.

### No deduplication across platforms
The same account appearing on multiple platforms (e.g., @account on Twitter and Instagram) is treated as separate entities.

**Rationale:** Cross-platform matching is unreliable and complex. Users may want to track accounts on specific platforms differently.

### No temporal weighting
A post from 1 day ago counts the same as a post from 29 days ago.

**Rationale:** All recent activity matters. Temporal weighting adds complexity without clear improvement.

---

## News Filtering

### News outlet exclusions applied by default
Major mainstream news outlets (CNN, Reuters, BBC, Bloomberg, NYTimes, etc.) are excluded from searches unless the query explicitly requests news coverage.

**Rationale:** News outlets cover many topics but aren't "community members." They skew results toward professional media rather than organic communities.

### LLM determines when news filter applies
Claude decides whether to apply news outlet exclusions based on query analysis (defaults to true).

**Rationale:** Some queries specifically seek news coverage (e.g., "news in China"). LLM can detect these cases.

### News exclusion list is hardcoded
The specific news outlets to exclude are maintained in a static list in `config.py`.

**Rationale:** News outlet names are stable. Dynamic detection would be more complex and error-prone.

---

## Keyword Generation

### Foreign language bundles for regional topics
Geopolitical or regional topics automatically get search bundles in relevant languages (e.g., Chinese for South China Sea).

**Rationale:** Regional topics are discussed in local languages. English-only searches miss significant community activity.

### Conversational post language over analytical jargon
Keywords are chosen to match how people actually write posts, avoiding meta-analytical terms like "perspectives," "implications," "stakeholders."

**Rationale:** Social media posts use conversational language. Analytical terms appear in research papers, not posts.

### User-provided keywords are optional enhancement
Users can provide specific keywords to prioritize, but the LLM still generates the full strategy and may incorporate them selectively.

**Rationale:** Users know their domain but may not know optimal search strategies. LLM balances user input with best practices.

### Bundle 3 constraint for Deep searches
If a third bundle exists in Deep searches, it must still focus on the core topic, not adjacent entities that have separate communities.

**Rationale:** Deep searches should stay focused on the specific entity. Searching for "similar artists" dilutes signal.

---

## Technical Implementation

### SerpAPI as discovery mechanism
We use Google search results (via SerpAPI) rather than native platform APIs to discover accounts.

**Rationale:** Google indexes all public social media content. Native APIs have rate limits, authentication complexity, and inconsistent coverage.

### No vetting beyond appearance threshold
Once an account meets the appearance threshold, it's included without checking follower count, engagement rate, or post quality.

**Rationale:** Appearance frequency is the signal. Additional vetting would require expensive API calls or scraping.

### Platform-specific URL parsing rules
Each platform has custom logic for extracting account identifiers from URLs (handles specific URL structures and edge cases per platform).

**Rationale:** Each platform has unique URL patterns. Generic parsing would miss edge cases and fail on URL variants.

### Single search query per bundle per page
Each keyword bundle generates one search query per pagination page, not multiple variations.

**Rationale:** Keeps API costs predictable. Multiple queries per bundle would increase costs without proportional benefit.

---

## Safety Limits

### Max pagination limits
Safety limits prevent runaway LLM-generated strategies:
- Max 10 pages per bundle
- Max 30 total pages across all bundles (as configured)

**Rationale:** LLM could theoretically generate expensive strategies. Hard limits prevent cost overruns.

### Threshold clamped to 2-5 range
LLM-generated thresholds are constrained between 2 (minimum) and 5 (maximum).

**Rationale:** Threshold below 2 produces too much noise. Threshold above 5 misses valid accounts.

### Classification influences all strategy parameters
The Deep vs Wide classification determines bundle count, pagination style, and appearance threshold as a package, not independently.

**Rationale:** These parameters work together as a cohesive strategy. Independent tuning would create inconsistent approaches.

---

## Future Optimization Opportunities

Based on these design decisions, potential areas for improvement:

1. **Temporal weighting:** Weight recent posts higher than older posts within the 30-day window
2. **Engagement filtering:** Add optional post engagement thresholds (likes, comments, shares)
3. **Cross-platform deduplication:** Attempt to match accounts across platforms using heuristics
4. **Dynamic news filters:** Generate exclusion lists dynamically based on topic
5. **Adaptive pagination:** Adjust pages per bundle based on result quality, not just fixed strategy
6. **Multi-language auto-detection:** Automatically detect and search in all relevant languages for a topic
7. **Account vetting:** Optional post-discovery vetting step for follower counts, account age, etc.
8. **Iterative refinement:** Allow users to adjust strategy after seeing initial results

---

## Validation & Testing

Key assumptions to validate through testing:

- Does appearance count correlate with topic relevance?
- Is 30 days the optimal time window?
- Are thresholds (2 for Deep, 3 for Wide) correctly calibrated?
- Does LLM classification match human judgment?
- Are news exclusions improving or hurting results?

Use `test_strategy.py` and `benchmark.py` to systematically test these assumptions.

---

*Last updated: February 2025*
