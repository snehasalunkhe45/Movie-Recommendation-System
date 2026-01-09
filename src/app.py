import streamlit as st
import pickle
import requests
from pathlib import Path

# --- 1. SETTINGS & CUSTOM MATTE STYLING ---
st.set_page_config(page_title="AI Movie Scout", layout="wide")

st.markdown("""
    <style>
    /* 1. Main Background */
    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
        background-attachment: fixed;
    }

    /* 2. SIDEBAR STYLING (Matching Title Color #1A1A1A) */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A !important; 
        border-right: 1px solid #333333;
    }

    /* Sidebar Text (White for high contrast on dark grey) */
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown,
    .history-item {
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif;
        font-weight: 400 !important;
    }

    .history-item {
        transition: 0.3s;
        margin-bottom: 5px;
        opacity: 0.8;
    }

    .history-item:hover {
        opacity: 1;
        padding-left: 5px;
        cursor: pointer;
    }

    /* UNIVERSAL TOGGLE BUTTON FIX */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #333333 !important; 
        border-radius: 8px !important;
        border: 1px solid #444444 !important;
        top: 10px !important;
        left: 10px !important;
    }

    [data-testid="stSidebarCollapseButton"] svg {
        fill: #F5F5F5 !important;
    }

    /* 3. Main Page Title Animations */
    @keyframes fadeInDown {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .main-title {
        animation: fadeInDown 1.5s ease-out;
        color: #1A1A1A !important; 
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 800;
    }

    .main-subtitle {
        animation: fadeInDown 1.8s ease-out;
        color: #455a64 !important; 
        text-align: center;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* 4. High-Contrast Body Text */
    h1, h2, h3 { color: #263238 !important; }
    p, span, label, .stMarkdown { color: #212121 !important; font-weight: 500; }

    /* 5. Buttons & Elements */
    .stImage img {
        border-radius: 12px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.12);
    }

    .stButton>button {
        background-color: #90a4ae; 
        color: #ffffff;
        border: none;
        border-radius: 8px;
        width: 100%;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background-color: #607d8b;
        color: white;
    }

    .footer {
        position: fixed;
        left: 0; bottom: 0; width: 100%;
        background-color: rgba(255, 255, 255, 0.9);
        color: #263238;
        text-align: center;
        padding: 8px;
        font-size: 13px;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API FUNCTION ---
@st.cache_data(show_spinner=False)
def get_movie_info(movie_title):
    API_KEY ="ad8cdb2"
    url = f"http://www.omdbapi.com/?t={movie_title.strip()}&apikey={API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get('Response') == 'True':
            poster = data.get('Poster')
            if poster == 'N/A' or not poster:
                poster = "https://via.placeholder.com/500x750?text=Poster+Coming+Soon"
            return {
                "poster": poster,
                "rating": data.get('imdbRating', 'N/A'),
                "plot": data.get('Plot', 'No summary available.'),
                "year": data.get('Year', 'N/A'),
                "genre": data.get('Genre', 'N/A')
            }
    except: pass
    return None

# --- 3. LOAD DATA ---
BASE_DIR = Path(__file__).parent.parent
MODEL_PATH = BASE_DIR / 'model'

try:
    movies = pickle.load(open(MODEL_PATH / 'movie_list.pkl', 'rb'))
    similarity = pickle.load(open(MODEL_PATH / 'similarity.pkl', 'rb'))
except Exception:
    st.error("Error: Pickle files missing from the 'model' folder.")
    st.stop()

# --- 4. SIDEBAR (Search History) ---
if 'history' not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("## 🕒 Recent Searches")
    if st.session_state.history:
        for m in reversed(st.session_state.history[-5:]):
            st.markdown(f"<div class='history-item'>• {m}</div>", unsafe_allow_html=True)
    else:
        st.markdown("*No recent searches*")
    
    st.divider()
    
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

# --- 5. MAIN UI ---
st.markdown("<h1 class='main-title'>🎬 AI Movie Insight </h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Explore 5000+ Hollywood & Bollywood Movies</p>", unsafe_allow_html=True)

selected_movie = st.selectbox("Search Hollywood or Bollywood movies:", movies['title'].values)

if selected_movie:
    if not st.session_state.history or st.session_state.history[-1] != selected_movie:
        st.session_state.history.append(selected_movie)
    
    info = get_movie_info(selected_movie)
    if info:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(info['poster'], use_container_width=True)
        with col2:
            st.markdown(f"## {selected_movie} ({info['year']})")
            st.markdown(f"### ⭐ IMDb Rating: {info['rating']}/10 | 🎭 {info['genre']}")
            st.markdown(f"**Plot Summary:** {info['plot']}")
    else:
        st.warning("⚠️ Movie details not found.")

    st.divider()

    if st.button('✨ Show Similar Recommendations'):
        st.markdown("## You might also like:")
        idx = movies[movies['title'] == selected_movie].index[0]
        distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:7]
        
        cols = st.columns(6)
        for i, dist in enumerate(distances):
            rec_title = movies.iloc[dist[0]].title
            rec_info = get_movie_info(rec_title)
            with cols[i]:
                if rec_info:
                    st.image(rec_info['poster'])
                    st.markdown(f"**{rec_title}**")
                else:
                    st.write(rec_title)

# --- 6. FOOTER ---
st.markdown("""
    <div class="footer">
        Developed by Sneha Salunkhe | AI Movie Scout © 2026
    </div>
    """, unsafe_allow_html=True)
