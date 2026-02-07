# Network Builder

Automated tool for discovering social media accounts and communities where target audiences actively discuss topics of interest. Built for Accrete's audience intelligence platform.

## What It Does

Network Builder solves a core product challenge: helping users influence specific audiences by discovering where those audiences congregate and discuss relevant topics online. Instead of manually searching for accounts, this tool automates discovery across 7 major platforms:

- **Twitter/X** - Active accounts discussing your topic
- **Instagram** - Relevant Instagram accounts
- **TikTok** - Content creators posting about your topic
- **YouTube** - Channels creating content (focuses on Shorts)
- **Facebook** - Active pages and profiles
- **Reddit** - Active subreddits and discussions
- **Telegram** - Active channels

## How It Works

1. **Smart Keyword Generation**: Uses Claude AI to generate adaptive search strategies
   - **Deep Search**: For specific topics (brands, people, niche issues) - searches deeply with fewer keyword variations
   - **Wide Search**: For complex topics (policy issues, social movements) - casts a wider net across multiple perspectives

2. **Multi-Platform Discovery**: Searches across all 7 platforms using SerpAPI
   - Runs 4 keyword bundles per platform
   - Paginated searches (2-6 pages per bundle depending on strategy)
   - Approximately 112 API calls per full discovery run

3. **Quality Filtering**: Counts appearances across search results
   - Accounts appearing 2+ times (Deep) or 3+ times (Wide) are kept
   - Filters for active accounts (posts in last 30 days)
   - Returns top 30 results per platform

## Prerequisites

- Python 3.8 or higher
- API Keys:
  - [SerpAPI](https://serpapi.com/) - For search results
  - [Anthropic API](https://console.anthropic.com/) - For Claude AI keyword generation

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd network-builder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys
   nano .env  # or use your preferred editor
   ```

   Your `.env` file should look like:
   ```
   SERPAPI_KEY=your_actual_serpapi_key_here
   CLAUDE_KEY=sk-ant-api03-your_actual_key_here
   ```

## Usage

### Web Interface (Recommended)

Run the Streamlit web app:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Interface Flow:**
1. Enter your topic (e.g., "climate anxiety", "Kendrick Lamar")
2. Choose search strategy:
   - `A` = Deep search (specific topics)
   - `B` = Wide search (complex topics)
   - Leave blank for auto-detection
3. Watch real-time progress as it searches
4. Download results as CSV

### Command Line Interface

Run the CLI version:

```bash
python main.py
```

**CLI Flow:**
1. Enter topic when prompted
2. Choose scope (A/B/auto)
3. Optionally add specific keywords
4. Results display in terminal
5. Option to save as CSV

### Testing Tools

**Test Strategy Generation** (no API calls to SerpAPI):
```bash
python test_strategy.py
```
Edit `TEST_TOPICS` in the file to test different topics. This only uses Claude API to generate strategies - useful for validating keyword generation before running full searches.

**Benchmark Mode** (with caching):
```bash
python benchmark.py
```
Edit `TEST_TOPICS` and `TEST_PLATFORMS` to test specific combinations. Results are cached to avoid redundant API calls during testing.

## Project Structure

```
network-builder/
├── app.py                  # Streamlit web interface
├── main.py                 # CLI interface
├── config.py               # Configuration and API keys
├── keyword_generator.py    # Claude-powered strategy generation
├── aggregator.py          # Results filtering and display
├── benchmark.py           # Testing harness with caching
├── test_strategy.py       # Strategy validation (no SerpAPI)
├── requirements.txt       # Python dependencies
├── .env                   # API keys (DO NOT COMMIT)
├── .env.example          # Template for API keys
└── platforms/            # Platform-specific search logic
    ├── twitter.py
    ├── instagram.py
    ├── tiktok.py
    ├── youtube.py
    ├── facebook.py
    ├── reddit.py
    └── telegram.py
```

## Configuration

Edit `config.py` to adjust:

- `ACCOUNT_THRESHOLD` - Minimum appearances for accounts (default: 2)
- `COMMUNITY_THRESHOLD` - Minimum appearances for communities (default: 2)
- `TOP_N_RESULTS` - Number of results per platform (default: 30)
- `SEARCH_DELAY` - Delay between API calls in seconds (default: 0.5)
- `MAX_PAGES_PER_BUNDLE` - Maximum pages per keyword bundle (default: 10)

## How the Algorithm Works

### Adaptive Search Strategy

The tool intelligently adapts its search approach based on topic type:

**Deep Search** (for specific topics like "Kendrick Lamar"):
- 2-3 keyword bundles with subtle variations
- More pagination per bundle (4-6 pages)
- Lower threshold (2+ appearances)
- Focus: depth over breadth

**Wide Search** (for complex topics like "climate anxiety"):
- 3-5 keyword bundles from different angles
- Less pagination per bundle (2-3 pages)
- Higher threshold (3+ appearances)
- Focus: breadth over depth

### Appearance Counting

Key insight: Instead of separate discovery + vetting steps, we **merge them** by counting appearances:

1. Run 4 keyword bundles × multiple pages = 40-60 search results
2. Extract all account identifiers from all results
3. Count how many times each account appears across all results
4. Keep only accounts appearing ≥ threshold times

**Why this works:** Accounts that appear multiple times across different keyword variations are more likely to be:
- Genuinely active on the topic
- Central to the community
- Worth tracking

### Platform-Specific Logic

Each platform has custom extraction rules:

- **Twitter**: Extract handle from status URLs
- **Instagram**: Extract handle from profile links
- **TikTok**: Extract handle from video URLs
- **YouTube**: Extract channel name from Shorts pages
- **Reddit**: Count subreddit appearances
- **Facebook**: Extract page/profile identifiers
- **Telegram**: Extract channel names

## Cost Estimates

**Per discovery run (all 7 platforms):**
- SerpAPI calls: ~112 searches × $0.005 = **~$0.56**
- Claude API: 1 strategy generation call = **~$0.03**
- **Total per run: ~$0.60**

## Troubleshooting

**"API key not set" error:**
- Make sure you copied `.env.example` to `.env`
- Verify your API keys are correctly set in `.env`
- Try running: `python -c "from config import SERPAPI_KEY; print(SERPAPI_KEY[:10])"`

**"Module not found" errors:**
- Run: `pip install -r requirements.txt`
- Make sure you're in the correct directory

**No results found:**
- Try a different search scope (Deep vs Wide)
- Check if your topic is too niche or too broad
- Verify API keys are valid and have credits

**Streamlit shows blank screen:**
- Check terminal for error messages
- Try: `streamlit run app.py --server.headless=true`

## Development

**Adding a new platform:**

1. Create `platforms/newplatform.py`
2. Implement `search_newplatform_bundle(keywords, start)` function
3. Implement `discover_newplatform(keyword_bundles, output_handler)` function
4. Import and add to `app.py` and `main.py`

**Modifying search strategy:**

Edit the prompt in `keyword_generator.py` to change how Claude generates keyword bundles.

## Contributing

When contributing:

1. Never commit API keys or `.env` files
2. Test with `test_strategy.py` before running full searches
3. Use `benchmark.py` for systematic testing
4. Keep platform logic isolated in `platforms/` directory

## License

Internal tool for Accrete. Not for external distribution.

## Support

For questions or issues, contact the Accrete engineering team.
