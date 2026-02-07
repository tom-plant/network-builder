# Quick Start Guide

Get Network Builder running in 5 minutes.

## Setup (First Time Only)

```bash
# 1. Clone the repository
git clone <repository-url>
cd network-builder

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp .env.example .env
nano .env  # Add your API keys here

# 4. Test it works
python main.py
```

## Your .env File Should Look Like:

```bash
SERPAPI_KEY=abc123your_actual_serpapi_key
CLAUDE_KEY=sk-ant-api03-your_actual_anthropic_key
```

**Get API Keys:**
- SerpAPI: https://serpapi.com/manage-api-key
- Anthropic: https://console.anthropic.com/

## Run It

**Web Interface (Recommended):**
```bash
streamlit run app.py
```
Open browser to http://localhost:8501

**Command Line:**
```bash
python main.py
```

## Example Topics to Try

- `Kendrick Lamar` (Deep search - specific person)
- `climate anxiety` (Wide search - complex issue)
- `South China Sea` (Wide search - geopolitical topic)
- `teacher strikes` (Wide search - social issue)

## Common Issues

**"API key not set"**
→ Make sure you created `.env` file and added your keys

**"Module not found"**
→ Run: `pip install -r requirements.txt`

**No results found**
→ Try a different topic or switch Deep/Wide search mode

## Architecture Overview

```
User Input → Claude AI (generates search strategy)
          ↓
     4 keyword bundles × 7 platforms
          ↓
     SerpAPI searches (~112 calls)
          ↓
     Count appearances across results
          ↓
     Filter by threshold (2-3+ appearances)
          ↓
     Return top 30 per platform
```

## Cost per Run

- ~112 SerpAPI calls × $0.005 = **$0.56**
- 1 Claude API call = **$0.03**
- **Total: ~$0.60 per discovery**

## Need Help?

1. Read the full [README.md](README.md)
2. Test strategy generation without API costs: `python test_strategy.py`
3. Contact the team
