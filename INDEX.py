import streamlit as st
import requests
from streamlit_player import st_player
import random
import threading

# Set up page configuration with an updated theme
st.set_page_config(
    page_title="DESHIINDIA IPTV Streams",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for a modern, immersive look
st.markdown("""
    <style>
        .stApp { background-color: #fafbfc; font-family: Arial, sans-serif; }
        .title { font-size: 2.7em; font-weight: bold; color: #272c35; margin-top: 0.3em; }
        .header { font-size: 1.5em; font-weight: 600; color: #5e6470; margin: 1em 0 0.6em; }
        .channel-card {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1em;
            margin: 0.5em 0;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
            color: #1d72b8;
        }
        .channel-card:hover {
            transform: translateY(-4px);
            background-color: #e9f5ff;
        }
        .channel-name { font-size: 1.2em; font-weight: 500; }
        .controls .stSlider > div { font-size: 1.1em; color: #3a3a3a; }
    </style>
""", unsafe_allow_html=True)

# Page Title
st.markdown("<div class='title'>📺 Global IPTV Streams</div>", unsafe_allow_html=True)

# URLs for different playlist categories
MAIN_M3U_URL = "https://raw.githubusercontent.com/Deshiindia/DESIINDIA/refs/heads/main/iPTV-Free-List_XXX.m3u"
LIVE_M3U_URL = "https://ip-tv.app/XXX"
STREAM_M3U_URL = "https://raw.githubusercontent.com/AAAAAEXQOSyIpN2JZ0ehUQ/iPTV-FREE-LIST/master/iPTV-Free-List_XXX.m3u"

# Cache channel loading with a time-to-live
@st.cache_data(ttl=600)
def load_channels(url):
    channels = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1].strip()
                url = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if url.startswith("http"):
                    channels.append({"name": name, "url": url})
    except Exception as e:
        st.error(f"Error loading channels from {url}: {e}")
    return channels

# Load all channels concurrently
main_channels = live_channels = stream_channels = []

def load_all_channels():
    global main_channels, live_channels, stream_channels
    main_channels = load_channels(MAIN_M3U_URL)
    live_channels = load_channels(LIVE_M3U_URL)
    stream_channels = load_channels(STREAM_M3U_URL)

threading.Thread(target=load_all_channels).start()

# Sidebar controls with icons for an interactive experience
st.sidebar.title("📋 Channel Controls")
search_query = st.sidebar.text_input("🔍 Search Channels")
volume = st.sidebar.slider("🔊 Volume", 0, 100, 50)
playback_speed = st.sidebar.selectbox("⏩ Playback Speed", [0.5, 1.0, 1.5, 2.0], index=1)
is_playing = st.sidebar.checkbox("▶️ Play", value=True)

# Filter channels based on search query
def filter_channels(channels, search_query):
    return [ch for ch in channels if search_query.lower() in ch["name"].lower()]

# Filtered channel lists
filtered_main_channels = filter_channels(main_channels, search_query)
filtered_live_channels = filter_channels(live_channels, search_query)
filtered_stream_channels = filter_channels(stream_channels, search_query)

# Initialize session state variables
if 'selected_channel' not in st.session_state:
    st.session_state.selected_channel = random.choice(filtered_main_channels) if filtered_main_channels else None
    st.session_state.selected_channel_index = 0  # Index of selected channel

if 'main_visible_count' not in st.session_state:
    st.session_state.main_visible_count = 4  # Reduced count for faster initial load

if 'live_visible_count' not in st.session_state:
    st.session_state.live_visible_count = 4

if 'stream_visible_count' not in st.session_state:
    st.session_state.stream_visible_count = 4

# Navigation function for next and previous channels
def change_channel(direction, channels):
    current_index = st.session_state.selected_channel_index
    if direction == "next":
        new_index = (current_index + 1) % len(channels)
    elif direction == "prev":
        new_index = (current_index - 1) % len(channels)
    else:
        return
    st.session_state.selected_channel = channels[new_index]
    st.session_state.selected_channel_index = new_index

# Display selected channel with playback controls
st.markdown("<div class='header'>🎬 Now Streaming</div>", unsafe_allow_html=True)
if st.session_state.selected_channel:
    st.subheader(f"Now Playing: {st.session_state.selected_channel['name']}")
    with st.spinner("Loading video..."):
        st_player(st.session_state.selected_channel['url'], playing=is_playing, volume=volume / 100.0, playback_rate=playback_speed)

    # Navigation controls for previous and next channel
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous Channel"):
            change_channel("prev", filtered_main_channels)
    with col3:
        if st.button("➡️ Next Channel"):
            change_channel("next", filtered_main_channels)
else:
    st.warning("No channel selected. Try adjusting your search.")

# Tabbed interface with custom icons for Main, Live, and Stream sections
tabs = st.tabs(["🏠 Main Channels", "🔴 Live Channels", "🌐 Stream Channels"])

# Function to display channel list with expandable view
def display_channel_list(channels, visible_count_key, section_key):
    visible_count = st.session_state[visible_count_key]
    channels_to_display = channels[:visible_count]

    if channels_to_display:
        st.markdown("### Available Channels")
        for i, channel in enumerate(channels_to_display):
            if st.button(f"▶️ {channel['name']}", key=f"{section_key}_channel_{i}"):
                st.session_state.selected_channel = channel
                st.session_state.selected_channel_index = i

        # Expand list with "Show More"
        if visible_count < len(channels):
            if st.button("Show More", key=f"{section_key}_show_more"):
                st.session_state[visible_count_key] += 4  # Load 4 channels at a time
    else:
        st.warning(f"No channels available in {section_key.capitalize()} Channels.")

# Main Channels Tab
with tabs[0]:
    st.header("📺 Main Channels")
    display_channel_list(filtered_main_channels, "main_visible_count", "main")

# Live Channels Tab
with tabs[1]:
    st.header("🔴 Live Channels")
    display_channel_list(filtered_live_channels, "live_visible_count", "live")

# Stream Channels Tab
with tabs[2]:
    st.header("🌐 Stream Channels")
    display_channel_list(filtered_stream_channels, "stream_visible_count", "stream")
