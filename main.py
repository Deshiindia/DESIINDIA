from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from html import escape

import requests
import streamlit as st
from streamlit_player import st_player


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="World IPTV",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PLAYLIST URLS
# REPLACE THESE WITH YOUR REAL M3U/M3U8 PLAYLIST URLS
# ============================================================

MAIN_M3U_URL = (
    "https://raw.githubusercontent.com/"
    "Deshiindia/DESIINDIA/refs/heads/main/"
    "iPTV-Free-List_XXX.m3u"
)

LIVE_M3U_URL = "https://ip-tv.app/XXX"

STREAM_M3U_URL = (
    "https://raw.githubusercontent.com/"
    "AAAAAEXQOSyIpN2JZ0ehUQ/iPTV-FREE-LIST/master/"
    "iPTV-Free-List_XXX.m3u"
)


# ============================================================
# SETTINGS
# ============================================================

REQUEST_TIMEOUT = 20
CHANNELS_PER_PAGE = 24


# ============================================================
# DATA MODEL
# ============================================================

@dataclass(frozen=True)
class Channel:
    name: str
    url: str
    logo: Optional[str] = None
    group: Optional[str] = None


# ============================================================
# SESSION STATE
# ============================================================

if "selected_channel" not in st.session_state:
    st.session_state.selected_channel = None

if "search_query" not in st.session_state:
    st.session_state.search_query = ""

if "main_limit" not in st.session_state:
    st.session_state.main_limit = CHANNELS_PER_PAGE

if "live_limit" not in st.session_state:
    st.session_state.live_limit = CHANNELS_PER_PAGE

if "stream_limit" not in st.session_state:
    st.session_state.stream_limit = CHANNELS_PER_PAGE

if "favorites" not in st.session_state:
    st.session_state.favorites = set()

if "volume" not in st.session_state:
    st.session_state.volume = 60

if "speed" not in st.session_state:
    st.session_state.speed = 1.0

if "autoplay" not in st.session_state:
    st.session_state.autoplay = True


# ============================================================
# MODERN CSS
# ============================================================

st.html(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    html,
    body {
        background: #07080c;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(87, 65, 255, 0.16),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 5%,
                rgba(0, 180, 255, 0.08),
                transparent 25%
            ),
            #07080c;
        color: #f5f7fb;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
        padding-bottom: 4rem;
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0d0f15 0%,
                #08090d 100%
            );

        border-right:
            1px solid rgba(255,255,255,0.07);
    }


    /* ========================================================
       HERO
    ======================================================== */

    .hero {
        position: relative;

        min-height: 230px;

        display: flex;
        align-items: center;
        justify-content: space-between;

        overflow: hidden;

        padding: 40px;

        margin-bottom: 25px;

        border-radius: 28px;

        border:
            1px solid rgba(255,255,255,0.08);

        background:
            linear-gradient(
                120deg,
                rgba(85,70,255,0.18),
                rgba(255,255,255,0.035) 45%,
                rgba(0,170,255,0.08)
            );

        box-shadow:
            0 25px 80px rgba(0,0,0,0.35);
    }

    .hero::before {
        content: "";

        position: absolute;

        width: 350px;
        height: 350px;

        right: -120px;
        top: -170px;

        border-radius: 50%;

        background:
            rgba(94, 77, 255, 0.18);

        filter: blur(30px);
    }

    .hero-content {
        position: relative;
        z-index: 2;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1.8px;
        line-height: 1.1;
    }

    .hero-subtitle {
        color: #a1a7b5;
        font-size: 15px;
        margin-top: 12px;
    }

    .hero-icon {
        position: relative;
        z-index: 2;

        font-size: 90px;

        filter:
            drop-shadow(
                0 15px 30px rgba(0,0,0,0.5)
            );
    }


    /* ========================================================
       STAT CARDS
    ======================================================== */

    .stats {
        display: grid;

        grid-template-columns:
            repeat(4, 1fr);

        gap: 14px;

        margin-bottom: 28px;
    }

    .stat-card {
        padding: 18px 20px;

        border-radius: 18px;

        border:
            1px solid rgba(255,255,255,0.07);

        background:
            rgba(255,255,255,0.035);
    }

    .stat-number {
        font-size: 25px;
        font-weight: 750;
    }

    .stat-label {
        color: #858c9d;
        font-size: 12px;
        margin-top: 4px;
    }


    /* ========================================================
       PLAYER
    ======================================================== */

    .player-container {
        margin-bottom: 30px;

        padding: 22px;

        border-radius: 25px;

        border:
            1px solid rgba(255,255,255,0.08);

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.065),
                rgba(255,255,255,0.018)
            );

        box-shadow:
            0 25px 80px rgba(0,0,0,0.4);
    }

    .player-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        margin-bottom: 18px;
    }

    .player-name {
        font-size: 22px;
        font-weight: 750;
    }

    .player-category {
        color: #8c94a5;
        font-size: 13px;
        margin-top: 4px;
    }

    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;

        padding: 6px 10px;

        border-radius: 20px;

        background:
            rgba(255,50,70,0.12);

        color: #ff6473;

        font-size: 11px;
        font-weight: 700;
    }

    .live-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #ff465c;

        box-shadow:
            0 0 10px #ff465c;
    }

    .empty-player {
        display: flex;

        min-height: 260px;

        align-items: center;
        justify-content: center;

        flex-direction: column;

        border-radius: 18px;

        background:
            linear-gradient(
                135deg,
                rgba(255,255,255,0.035),
                rgba(255,255,255,0.012)
            );

        border:
            1px dashed rgba(255,255,255,0.10);
    }

    .empty-player-icon {
        font-size: 50px;
        margin-bottom: 12px;
    }

    .empty-player-title {
        font-size: 18px;
        font-weight: 650;
    }

    .empty-player-text {
        color: #777f90;
        font-size: 13px;
        margin-top: 5px;
    }


    /* ========================================================
       SECTION
    ======================================================== */

    .section-header {
        display: flex;

        align-items: center;
        justify-content: space-between;

        margin-top: 32px;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 750;
        letter-spacing: -0.5px;
    }

    .section-count {
        color: #7d8494;
        font-size: 13px;
    }


    /* ========================================================
       CHANNEL CARD
    ======================================================== */

    .channel-card {
        position: relative;

        min-height: 205px;

        padding: 18px;

        margin-bottom: 8px;

        border-radius: 19px;

        border:
            1px solid rgba(255,255,255,0.07);

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.018)
            );

        overflow: hidden;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease,
            box-shadow 0.2s ease;
    }

    .channel-card:hover {
        transform: translateY(-5px);

        border-color:
            rgba(108, 91, 255, 0.55);

        box-shadow:
            0 20px 45px rgba(0,0,0,0.35);
    }

    .channel-logo {
        display: flex;

        width: 82px;
        height: 82px;

        object-fit: contain;

        align-items: center;
        justify-content: center;

        border-radius: 17px;

        background:
            rgba(255,255,255,0.06);

        padding: 10px;

        margin-bottom: 14px;
    }

    .channel-placeholder {
        font-size: 36px;
    }

    .channel-name {
        font-size: 14px;
        font-weight: 650;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .channel-group {
        color: #818999;

        font-size: 11px;

        margin-top: 6px;

        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .channel-live {
        position: absolute;

        top: 13px;
        right: 13px;

        padding: 4px 8px;

        border-radius: 20px;

        color: #ff6572;

        background:
            rgba(255,50,70,0.12);

        font-size: 9px;
        font-weight: 750;

        letter-spacing: 0.5px;
    }


    /* ========================================================
       BUTTONS
    ======================================================== */

    .stButton > button {
        border-radius: 11px !important;

        min-height: 38px;

        border:
            1px solid rgba(255,255,255,0.08) !important;

        background:
            rgba(255,255,255,0.045) !important;

        color: #f5f7fb !important;

        font-weight: 600;

        transition:
            all 0.18s ease;
    }

    .stButton > button:hover {
        border-color:
            rgba(105,88,255,0.65) !important;

        background:
            rgba(105,88,255,0.15) !important;

        transform:
            translateY(-1px);
    }


    /* ========================================================
       INPUTS
    ======================================================== */

    div[data-baseweb="input"] {
        border-radius: 13px !important;
    }

    div[data-baseweb="select"] {
        border-radius: 13px !important;
    }


    /* ========================================================
       TABS
    ======================================================== */

    button[data-baseweb="tab"] {
        color: #818999;
        font-weight: 600;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff;
    }


    /* ========================================================
       MOBILE
    ======================================================== */

    @media (max-width: 900px) {

        .stats {
            grid-template-columns:
                repeat(2, 1fr);
        }

        .hero {
            padding: 28px;
        }

        .hero-title {
            font-size: 32px;
        }

        .hero-icon {
            font-size: 65px;
        }
    }

    @media (max-width: 600px) {

        .stats {
            grid-template-columns: 1fr 1fr;
        }

        .hero {
            min-height: 180px;
        }

        .hero-title {
            font-size: 27px;
        }

        .hero-subtitle {
            font-size: 13px;
        }

        .hero-icon {
            font-size: 45px;
        }
    }

    </style>
    """
)


# ============================================================
# M3U PARSER
# ============================================================

def parse_extinf(
    line: str,
) -> tuple[str, Optional[str], Optional[str]]:
    """
    Parse an M3U #EXTINF line.

    Supports:
        tvg-logo
        group-title
        channel name
    """

    if "," in line:
        name = line.split(",", 1)[1].strip()
    else:
        name = "Unknown Channel"

    logo = None
    group = None

    if 'tvg-logo="' in line:
        try:
            logo = (
                line.split('tvg-logo="', 1)[1]
                .split('"', 1)[0]
                .strip()
            )
        except IndexError:
            logo = None

    if 'group-title="' in line:
        try:
            group = (
                line.split('group-title="', 1)[1]
                .split('"', 1)[0]
                .strip()
            )
        except IndexError:
            group = None

    return name, logo, group


# ============================================================
# PLAYLIST LOADER
# ============================================================

@st.cache_data(
    ttl=600,
    show_spinner=False,
)
def load_channels(
    playlist_url: str,
) -> list[Channel]:

    channels: list[Channel] = []

    if not playlist_url:
        return channels

    try:

        response = requests.get(
            playlist_url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36"
                )
            },
        )

        response.raise_for_status()

    except requests.RequestException as exc:

        st.warning(
            f"Could not load playlist: {exc}"
        )

        return channels

    lines = [
        line.strip()
        for line in response.text.splitlines()
        if line.strip()
    ]

    i = 0

    while i < len(lines):

        line = lines[i]

        if not line.startswith("#EXTINF"):
            i += 1
            continue

        name, logo, group = parse_extinf(line)

        stream_url = None

        j = i + 1

        while j < len(lines):

            candidate = lines[j].strip()

            if candidate.startswith(
                ("http://", "https://")
            ):
                stream_url = candidate
                break

            if candidate.startswith("#EXTINF"):
                break

            j += 1

        if stream_url:

            channels.append(
                Channel(
                    name=name,
                    url=stream_url,
                    logo=logo,
                    group=group,
                )
            )

        i = max(j, i + 1)

    return channels


# ============================================================
# FILTER CHANNELS
# ============================================================

def filter_channels(
    channels: list[Channel],
    query: str,
    category: str,
    favorites_only: bool = False,
) -> list[Channel]:

    query = query.strip().lower()

    result = channels

    if query:

        result = [
            channel
            for channel in result
            if (
                query in channel.name.lower()
                or query in (
                    channel.group or ""
                ).lower()
            )
        ]

    if category != "All":

        result = [
            channel
            for channel in result
            if channel.group == category
        ]

    if favorites_only:

        result = [
            channel
            for channel in result
            if channel.url in st.session_state.favorites
        ]

    return result


# ============================================================
# CATEGORIES
# ============================================================

def get_categories(
    channels: list[Channel],
) -> list[str]:

    groups = {
        channel.group
        for channel in channels
        if channel.group
    }

    return [
        "All",
        *sorted(groups),
    ]


# ============================================================
# SELECT CHANNEL
# ============================================================

def select_channel(
    channel: Channel,
) -> None:

    st.session_state.selected_channel = channel


# ============================================================
# FAVORITES
# ============================================================

def toggle_favorite(
    channel: Channel,
) -> None:

    url = channel.url

    if url in st.session_state.favorites:
        st.session_state.favorites.remove(url)
    else:
        st.session_state.favorites.add(url)


# ============================================================
# CHANNEL CARD
# ============================================================

def render_channel_card(
    channel: Channel,
    index: int,
    prefix: str,
) -> None:

    safe_name = escape(channel.name)

    safe_group = escape(
        channel.group or "Live TV"
    )

    if channel.logo:

        safe_logo = escape(
            channel.logo,
            quote=True,
        )

        logo_html = f"""
        <img
            class="channel-logo"
            src="{safe_logo}"
            alt="Channel logo"
        >
        """

    else:

        logo_html = """
        <div class="
            channel-logo
            channel-placeholder
        ">
            📺
        </div>
        """

    is_favorite = (
        channel.url
        in st.session_state.favorites
    )

    favorite_icon = "★" if is_favorite else "☆"

    st.html(
        f"""
        <div class="channel-card">

            <div class="channel-live">
                ● LIVE
            </div>

            {logo_html}

            <div class="channel-name">
                {safe_name}
            </div>

            <div class="channel-group">
                {safe_group}
            </div>

        </div>
        """
    )

    col_watch, col_favorite = st.columns(
        [4, 1],
        gap="small",
    )

    with col_watch:

        if st.button(
            "▶ Watch",
            key=f"{prefix}_watch_{index}",
            use_container_width=True,
        ):

            select_channel(channel)

            st.rerun()

    with col_favorite:

        if st.button(
            favorite_icon,
            key=f"{prefix}_favorite_{index}",
            use_container_width=True,
        ):

            toggle_favorite(channel)

            st.rerun()


# ============================================================
# CHANNEL GRID
# ============================================================

def render_channel_grid(
    channels: list[Channel],
    prefix: str,
    limit_key: str,
) -> None:

    if not channels:

        st.html(
            """
            <div class="empty-player">

                <div class="empty-player-icon">
                    🔍
                </div>

                <div class="empty-player-title">
                    No channels found
                </div>

                <div class="empty-player-text">
                    Try another search or category.
                </div>

            </div>
            """
        )

        return

    limit = st.session_state[limit_key]

    visible_channels = channels[:limit]

    # Four-column desktop layout.
    columns = st.columns(
        4,
        gap="medium",
    )

    for index, channel in enumerate(
        visible_channels
    ):

        with columns[index % 4]:

            render_channel_card(
                channel=channel,
                index=index,
                prefix=prefix,
            )

    if len(channels) > limit:

        st.write("")

        remaining = (
            len(channels) - limit
        )

        amount = min(
            CHANNELS_PER_PAGE,
            remaining,
        )

        if st.button(
            f"＋ Load {amount} More Channels",
            key=f"{prefix}_load_more",
            use_container_width=True,
        ):

            st.session_state[limit_key] += (
                CHANNELS_PER_PAGE
            )

            st.rerun()


# ============================================================
# LOAD PLAYLISTS
# ============================================================

with st.spinner("Loading IPTV channels..."):

    main_channels = load_channels(
        MAIN_M3U_URL
    )

    live_channels = load_channels(
        LIVE_M3U_URL
    )

    stream_channels = load_channels(
        STREAM_M3U_URL
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div style="
            padding: 8px 0 15px 0;
        ">

            <div style="
                font-size:24px;
                font-weight:800;
            ">
                📺 World IPTV
            </div>

            <div style="
                color:#7f8798;
                font-size:12px;
                margin-top:5px;
            ">
                Modern streaming dashboard
            </div>

        </div>
        """
    )

    st.divider()

    st.markdown(
        "### 🔎 Search"
    )

    search = st.text_input(
        "Search channels",
        placeholder="Channel name...",
        label_visibility="collapsed",
    )

    st.session_state.search_query = search

    st.divider()

    st.markdown(
        "### 🎛 Player"
    )

    st.session_state.volume = st.slider(
        "Volume",
        min_value=0,
        max_value=100,
        value=st.session_state.volume,
        step=5,
    )

    st.session_state.speed = st.selectbox(
        "Playback Speed",
        options=[
            0.5,
            0.75,
            1.0,
            1.25,
            1.5,
            2.0,
        ],
        index=2,
    )

    st.session_state.autoplay = st.toggle(
        "Auto Play",
        value=st.session_state.autoplay,
    )

    st.divider()

    st.markdown(
        "### 📡 Playlists"
    )

    st.caption(
        f"Main: {len(main_channels):,}"
    )

    st.caption(
        f"Live: {len(live_channels):,}"
    )

    st.caption(
        f"Streams: {len(stream_channels):,}"
    )

    st.divider()

    if st.button(
        "🔄 Refresh Playlists",
        use_container_width=True,
    ):

        load_channels.clear()

        st.rerun()


# ============================================================
# HERO
# ============================================================

total_channels = (
    len(main_channels)
    + len(live_channels)
    + len(stream_channels)
)

st.html(
    f"""
    <div class="hero">

        <div class="hero-content">

            <div class="hero-title">
                🌐 World IPTV
            </div>

            <div class="hero-subtitle">
                Watch live television from around
                the world in one place.
            </div>

        </div>

        <div class="hero-icon">
            📡
        </div>

    </div>
    """
)


# ============================================================
# STATISTICS
# ============================================================

st.html(
    f"""
    <div class="stats">

        <div class="stat-card">
            <div class="stat-number">
                {total_channels:,}
            </div>
            <div class="stat-label">
                Total Channels
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-number">
                {len(main_channels):,}
            </div>
            <div class="stat-label">
                Main Channels
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-number">
                {len(live_channels):,}
            </div>
            <div class="stat-label">
                Live Channels
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-number">
                {len(st.session_state.favorites):,}
            </div>
            <div class="stat-label">
                Favorites
            </div>
        </div>

    </div>
    """
)


# ============================================================
# NOW PLAYING
# ============================================================

selected: Optional[Channel] = (
    st.session_state.selected_channel
)


if selected:

    safe_selected_name = escape(
        selected.name
    )

    safe_selected_group = escape(
        selected.group or "Live TV"
    )

    st.html(
        f"""
        <div class="player-container">

            <div class="player-header">

                <div>

                    <div class="player-name">
                        ▶ {safe_selected_name}
                    </div>

                    <div class="player-category">
                        {safe_selected_group}
                    </div>

                </div>

                <div class="live-indicator">

                    <span class="live-dot"></span>

                    LIVE

                </div>

            </div>

        </div>
        """
    )

    try:

        st_player(
            selected.url,
            playing=st.session_state.autoplay,
            volume=(
                st.session_state.volume / 100
            ),
            playback_rate=st.session_state.speed,
        )

    except Exception as exc:

        st.error(
            f"Unable to play this stream: {exc}"
        )

else:

    st.html(
        """
        <div class="player-container">

            <div class="empty-player">

                <div class="empty-player-icon">
                    🎬
                </div>

                <div class="empty-player-title">
                    Nothing Playing
                </div>

                <div class="empty-player-text">
                    Select a channel below to start watching.
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# TABS
# ============================================================

main_tab, live_tab, stream_tab = st.tabs(
    [
        "📺 Main Channels",
        "🔴 Live Channels",
        "🌐 Stream Channels",
    ]
)


# ============================================================
# MAIN CHANNELS
# ============================================================

with main_tab:

    main_categories = get_categories(
        main_channels
    )

    category = st.selectbox(
        "Category",
        main_categories,
        key="main_category",
    )

    filtered_main = filter_channels(
        main_channels,
        st.session_state.search_query,
        category,
    )

    st.html(
        f"""
        <div class="section-header">

            <div class="section-title">
                📺 Main Channels
            </div>

            <div class="section-count">
                {len(filtered_main):,} channels
            </div>

        </div>
        """
    )

    render_channel_grid(
        filtered_main,
        "main",
        "main_limit",
    )


# ============================================================
# LIVE CHANNELS
# ============================================================

with live_tab:

    live_categories = get_categories(
        live_channels
    )

    category = st.selectbox(
        "Category",
        live_categories,
        key="live_category",
    )

    filtered_live = filter_channels(
        live_channels,
        st.session_state.search_query,
        category,
    )

    st.html(
        f"""
        <div class="section-header">

            <div class="section-title">
                🔴 Live Channels
            </div>

            <div class="section-count">
                {len(filtered_live):,} channels
            </div>

        </div>
        """
    )

    render_channel_grid(
        filtered_live,
        "live",
        "live_limit",
    )


# ============================================================
# STREAM CHANNELS
# ============================================================

with stream_tab:

    stream_categories = get_categories(
        stream_channels
    )

    category = st.selectbox(
        "Category",
        stream_categories,
        key="stream_category",
    )

    filtered_stream = filter_channels(
        stream_channels,
        st.session_state.search_query,
        category,
    )

    st.html(
        f"""
        <div class="section-header">

            <div class="section-title">
                🌐 Stream Channels
            </div>

            <div class="section-count">
                {len(filtered_stream):,} channels
            </div>

        </div>
        """
    )

    render_channel_grid(
        filtered_stream,
        "stream",
        "stream_limit",
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.html(
    """
    <div style="
        text-align:center;
        padding:25px 0;
        color:#606879;
        font-size:12px;
    ">
        🌐 World IPTV
        &nbsp;•&nbsp;
        Modern Streaming Dashboard
    </div>
    """
)
