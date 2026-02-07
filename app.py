import streamlit as st
import time
from keyword_generator import generate_search_strategy
from aggregator import aggregate_and_filter
from config import TOP_N_RESULTS
import json

# Import platform modules
from platforms.twitter import discover_twitter
from platforms.facebook import discover_facebook
from platforms.instagram import discover_instagram
from platforms.tiktok import discover_tiktok
from platforms.youtube import discover_youtube
from platforms.reddit import discover_reddit
from platforms.telegram import discover_telegram

# Page config
st.set_page_config(
    page_title="Network Builder",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS matching Accrete's minimal dark theme
st.markdown("""
<style>
    /* Dark theme - match Accrete exactly */
    .stApp {
        background-color: #0a0e27;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat messages - minimal like Accrete */
    .stChatMessage {
        background-color: transparent !important;
        padding: 0.5rem 0;
    }
    
    [data-testid="stChatMessageContent"] {
        color: #e0e0e0;
        background-color: transparent;
    }
    
    /* Input styling - match Accrete bottom bar */
    .stChatInputContainer {
        background-color: #151b3d;
        border-radius: 24px;
        border: 1px solid #2a2e4d;
    }
    
    /* Buttons - inline pill style */
    .stButton button {
        background-color: #2a2e4d;
        color: #a0a0e0;
        border-radius: 20px;
        border: none;
        padding: 0.4rem 1.2rem;
        font-size: 0.9rem;
        font-weight: 400;
        margin: 0.25rem;
    }
    
    .stButton button:hover {
        background-color: #6c5ce7;
        color: white;
    }
    
    /* Terminal-style output */
    .terminal-output {
        background-color: #0d1117;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'SF Mono', Monaco, 'Courier New', monospace;
        font-size: 0.85rem;
        color: #c9d1d9;
        line-height: 1.6;
        margin: 1rem 0;
        border: 1px solid #21262d;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .terminal-line {
        margin: 0.2rem 0;
    }
    
    /* Results table - compact single column layout */
    .results-table {
        width: 100%;
        margin: 1rem 0;
    }
    
    .result-row {
        display: flex;
        align-items: center;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem 0;
        background-color: #151b3d;
        border-radius: 6px;
        border-left: 2px solid #6c5ce7;
    }
    
    .result-rank {
        color: #666;
        font-size: 0.85rem;
        width: 2rem;
        flex-shrink: 0;
    }
    
    .result-identifier {
        color: #e0e0e0;
        flex-grow: 1;
        font-weight: 500;
    }
    
    .result-count {
        color: #6c5ce7;
        font-size: 0.9rem;
        font-weight: 600;
        margin-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_scope" not in st.session_state:
    st.session_state.awaiting_scope = False
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "scope_choice" not in st.session_state:
    st.session_state.scope_choice = None


class StreamlitOutputHandler:
    """Handles real-time output streaming to Streamlit."""
    
    def __init__(self, display_container):
        self.display_container = display_container
        self.output_text = ""
        # Log to current directory instead of /home/claude/
        self.log_file = open('discovery_log.txt', 'a')
    
    def write(self, text, end="\n"):
        """Write text and update display immediately."""
        # Simply append text as-is
        if end == " ":
            self.output_text += text
        else:
            self.output_text += text + end
        
        # Log to file
        self.log_file.write(text)
        if end != " ":
            self.log_file.write(end)
        self.log_file.flush()
        
        # Update display immediately
        self.display_container.markdown(
            f"<div class='terminal-output'><pre>{self.output_text}</pre></div>",
            unsafe_allow_html=True
        )
    
    def flush(self):
        """Compatibility method for file-like interface."""
        self.log_file.flush()
    
    def close(self):
        """Close the log file."""
        self.log_file.close()


def run_discovery_with_streaming(topic, scope):
    """Run discovery with true real-time line-by-line updates."""
    
    # Generate strategy
    strategy_display = st.empty()
    
    import io
    from contextlib import redirect_stdout
    
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        strategy = generate_search_strategy(topic, scope, user_keywords=None)
    
    strategy_output = buffer.getvalue()
    strategy_display.markdown(f"<div class='terminal-output'><pre>{strategy_output}</pre></div>", unsafe_allow_html=True)
    
    time.sleep(0.5)
    
    # Now run each platform with real-time updates
    keyword_bundles = strategy["bundles"]
    threshold = strategy["threshold"]
    results = {}
    
    platforms = [
        ('Twitter', discover_twitter),
        ('Instagram', discover_instagram),
        ('TikTok', discover_tiktok),
        ('YouTube', discover_youtube),
        ('Reddit', discover_reddit),
        ('Facebook', discover_facebook),
        ('Telegram', discover_telegram)
    ]
    
    for platform_name, discover_func in platforms:
        platform_display = st.empty()
        
        # Create output handler for this platform
        output_handler = StreamlitOutputHandler(platform_display)
        
        try:
            # Run discovery with streaming output
            raw_data = discover_func(keyword_bundles, output_handler)
            
            # Filter results
            filtered_data = aggregate_and_filter(raw_data, threshold, TOP_N_RESULTS)
            results[platform_name] = filtered_data
            
        except Exception as e:
            # Log error to both file and display
            error_msg = f"\n❌ ERROR in {platform_name}: {str(e)}\n"
            output_handler.write(error_msg)
            results[platform_name] = []
            
            # Also log full traceback to file
            import traceback
            with open('error_log.txt', 'a') as f:
                f.write(f"\n\n{'='*80}\n")
                f.write(f"ERROR in {platform_name}:\n")
                f.write(traceback.format_exc())
                f.write(f"{'='*80}\n")
        finally:
            output_handler.close()
        
        time.sleep(0.2)
    
    return results, strategy


def display_results(results):
    """Display results in compact single-column layout."""
    
    total_sources = sum(len(data) for data in results.values())
    
    st.markdown(f"### ✅ Found {total_sources} total sources across {len(results)} platforms\n")
    
    # Show each platform's results
    for platform_name, data in results.items():
        if len(data) == 0:
            continue
        
        st.markdown(f"#### {platform_name}: {len(data)} results")
        
        # Simple table layout
        for rank, (identifier, count) in enumerate(data, 1):
            st.markdown(f"""
            <div class='result-row'>
                <span class='result-rank'>{rank}</span>
                <span class='result-identifier'>{identifier}</span>
                <span class='result-count'>{count}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing

def generate_csv(results):
    """Generate CSV export data."""
    lines = ["Platform,Identifier,Appearances,Notes\n"]
    for platform, data in results.items():
        for identifier, count in data:
            lines.append(f"{platform},{identifier},{count},Appeared {count}x in last 30 days\n")
    return "".join(lines)


# Main UI - clean and minimal
st.markdown("<h1 style='text-align: center; color: #ffffff; padding: 2rem 0;'>🔍 Network Builder</h1>", unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Welcome screen
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("What topic or issue do you want to track?")

# Handle chat input
user_input = st.chat_input("Describe your audience...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if not st.session_state.current_topic:
        # This is the topic
        st.session_state.current_topic = user_input
        st.session_state.awaiting_scope = True
        
        # Ask scope question with EXACT wording from terminal
        scope_question = """How should we search for this community?
  A) Deep - specific term for a niche issue, brand, product, or clear subject
  B) Wide - cast a net across multiple angles, perspectives, or dimensions
  [leave blank to auto-detect]"""
        
        st.session_state.messages.append({"role": "assistant", "content": scope_question})
        st.rerun()
        
    elif st.session_state.awaiting_scope:
        # User answered scope - store it and rerun to display the message first
        choice = user_input.strip().upper()
        
        if choice == "A":
            st.session_state.scope_choice = "A"
        elif choice == "B":
            st.session_state.scope_choice = "B"
        elif choice == "":
            st.session_state.scope_choice = "auto"
        else:
            # Assume auto if unclear
            st.session_state.scope_choice = "auto"
        
        st.session_state.awaiting_scope = False
        st.rerun()

# Run discovery if we have all the info and haven't shown results yet
if (st.session_state.current_topic and 
    st.session_state.scope_choice is not None and
    not st.session_state.awaiting_scope):
    
    # Check if we already have results in messages
    has_results = any("results" in str(msg.get("content", "")).lower() for msg in st.session_state.messages if msg["role"] == "assistant")
    
    if not has_results:
        # Start discovery
        with st.chat_message("assistant"):
            results, strategy = run_discovery_with_streaming(
                st.session_state.current_topic,
                st.session_state.scope_choice
            )
            
            # Show results
            st.markdown("---")
            display_results(results)
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv_data = generate_csv(results)
                st.download_button(
                    label="💾 Save to CSV",
                    data=csv_data,
                    file_name=f"network_{st.session_state.current_topic[:30].replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                if st.button("🔄 New Search", use_container_width=True):
                    # Clear ALL session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()