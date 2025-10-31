import streamlit as st
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="🎬 CineMatch - Movie Recommendations",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS - Netflix Theme
# -------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(to bottom, #000000 0%, #1a0000 50%, #000000 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Netflix Logo Animation */
    .netflix-logo {
        font-family: 'Bebas Neue', cursive;
        font-size: 5rem;
        font-weight: 900;
        color: #E50914;
        text-shadow: 3px 3px 0px rgba(0,0,0,0.7);
        animation: glow 2s ease-in-out infinite alternate;
        text-align: center;
        margin-bottom: 10px;
        letter-spacing: 8px;
    }
    
    @keyframes glow {
        from {
            text-shadow: 0 0 5px #E50914, 0 0 10px #E50914, 0 0 15px #E50914;
        }
        to {
            text-shadow: 0 0 10px #E50914, 0 0 20px #E50914, 0 0 30px #E50914, 0 0 40px #E50914;
        }
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 30px;
        letter-spacing: 2px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141414 0%, #000000 100%);
        border-right: 2px solid #E50914;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #E50914 !important;
        font-family: 'Bebas Neue', cursive;
        font-size: 2rem;
        text-align: center;
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #333333 !important;
        border-radius: 5px !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #E50914 !important;
        box-shadow: 0 0 10px rgba(229, 9, 20, 0.5) !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #E50914 !important;
    }
    
    /* Button */
    .stButton button {
        background: linear-gradient(90deg, #E50914 0%, #b20710 100%);
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        padding: 12px 30px;
        border: none;
        border-radius: 5px;
        width: 100%;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #b20710 0%, #E50914 100%);
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(229, 9, 20, 0.6);
    }
    
    /* Movie Card */
    .movie-card {
        background: linear-gradient(145deg, #1a1a1a 0%, #0d0d0d 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 2px solid #2a2a2a;
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(229, 9, 20, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .movie-card:hover::before {
        left: 100%;
    }
    
    .movie-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #E50914;
        box-shadow: 0 8px 25px rgba(229, 9, 20, 0.4);
    }
    
    .movie-title {
        color: #E50914;
        font-size: 1.6rem;
        font-weight: bold;
        margin-bottom: 10px;
        font-family: 'Roboto', sans-serif;
    }
    
    .movie-info {
        color: #b3b3b3;
        font-size: 1rem;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .movie-genre {
        color: #ffffff;
        font-size: 0.95rem;
        background: rgba(229, 9, 20, 0.2);
        padding: 5px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px 5px 5px 0;
        border: 1px solid rgba(229, 9, 20, 0.3);
    }
    
    .score-badge {
        background: linear-gradient(135deg, #E50914 0%, #b20710 100%);
        color: white;
        padding: 8px 15px;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
        box-shadow: 0 2px 8px rgba(229, 9, 20, 0.5);
    }
    
    /* Success/Warning Messages */
    .stAlert {
        background-color: rgba(229, 9, 20, 0.1) !important;
        border: 1px solid #E50914 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #E50914 !important;
    }
    
    /* Divider */
    hr {
        border-color: #E50914 !important;
        opacity: 0.3;
    }
    
    /* Rating Star */
    .star {
        color: #ffd700;
        font-size: 1.1rem;
    }
    
    /* Pulse Animation for New Recommendations */
    @keyframes pulse {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .movie-card {
        animation: pulse 0.6s ease-out;
    }
    
    /* Label Colors */
    label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Load Models and Data
# -------------------------------
@st.cache_data
def load_data():
    movies = pd.read_csv("data/movies_clean.csv")
    
    def clean_genres(x):
        if isinstance(x, str):
            return [g.strip() for g in x.split(',')]
        else:
            return []

    movies['genres'] = movies['genres'].apply(clean_genres)

    with open("model/tfidf.pkl", "rb") as f:
        tfidf = pickle.load(f)
    with open("model/nn_tfidf.pkl", "rb") as f:
        nn = pickle.load(f)
    with open("model/user_similarity.pkl", "rb") as f:
        user_similarity_df = pickle.load(f)
    with open("model/user_movie_matrix.pkl", "rb") as f:
        user_movie_matrix = pickle.load(f)

    return movies, tfidf, nn, user_similarity_df, user_movie_matrix


movies, tfidf, nn, user_similarity_df, user_movie_matrix = load_data()


def get_content_recommendations(title, top_n=10):
    idx = movies[movies['title'].str.lower() == title.lower()].index
    if len(idx) == 0:
        return pd.DataFrame()
    idx = idx[0]
    movie_vector = tfidf.transform([movies.iloc[idx]['description']])
    cosine_scores = cosine_similarity(movie_vector, tfidf.transform(movies['description'])).flatten()
    top_indices = cosine_scores.argsort()[-top_n-1:-1][::-1]
    df = movies.iloc[top_indices][['title', 'genres', 'vote_average', 'release_date']]
    df['content_score'] = df['vote_average']
    return df


def get_collaborative_recommendations(user_id, top_n=10):
    if user_id not in user_similarity_df.index:
        return pd.DataFrame()
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:10].index
    similar_users_ratings = user_movie_matrix.loc[similar_users].mean(axis=0)
    user_rated = user_movie_matrix.loc[user_id].dropna().index
    similar_users_ratings = similar_users_ratings.drop(user_rated, errors='ignore')
    collab_df = similar_users_ratings.sort_values(ascending=False).head(top_n).reset_index().rename(columns={'index':'title', 0:'collab_score'})
    return collab_df


def hybrid_recommendations(user_id, title, alpha=0.7, top_n=10):
    content_df = get_content_recommendations(title, top_n=20)
    collab_df = get_collaborative_recommendations(user_id, top_n=20)

    merged = pd.merge(content_df, collab_df, on='title', how='outer').fillna(0)
    merged['hybrid_score'] = alpha * merged['content_score'] + (1 - alpha) * merged['collab_score']

    merged = merged[merged['hybrid_score'] > 0]
    merged = merged.sort_values('hybrid_score', ascending=False)

    merged = merged[merged['genres'] != 0]
    merged = merged[merged['vote_average'] != 0]

    return merged[['title', 'genres', 'vote_average', 'release_date', 'hybrid_score']].head(top_n)


# -------------------------------
# Main UI
# -------------------------------
st.markdown('<div class="netflix-logo">CINEMATCH</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Discover Your Next Favorite Movie</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎯 PREFERENCES")
st.sidebar.markdown("---")

user_id = st.sidebar.number_input(
    "👤 User ID",
    min_value=1,
    max_value=610,
    value=5,
    help="Enter your unique user ID"
)

movie_title = st.sidebar.text_input(
    "🎬 Movie Title",
    value="Toy Story",
    help="Enter a movie you like"
)

st.sidebar.markdown("---")

alpha = st.sidebar.slider(
    "⚖️ Algorithm Balance",
    0.0,
    1.0,
    0.7,
    help="Slide towards Content (1.0) or Collaborative (0.0)"
)

st.sidebar.markdown(f"""
<div style='text-align: center; color: #b3b3b3; font-size: 0.85rem; margin-top: 10px;'>
    <b style='color: #E50914;'>{int(alpha*100)}%</b> Content-Based<br>
    <b style='color: #E50914;'>{int((1-alpha)*100)}%</b> Collaborative
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Get Recommendations Button
if st.sidebar.button("🎯 GET RECOMMENDATIONS"):
    with st.spinner("🎬 Loading your personalized recommendations..."):
        results = hybrid_recommendations(user_id, movie_title, alpha, top_n=10)

    if results.empty:
        st.warning("⚠️ No recommendations found. Please try a different movie title.")
    else:
        st.success(f"✨ Top Recommendations Based on **{movie_title}**")
        st.markdown("---")

        # Display movie cards
        for idx, row in results.iterrows():
            genres_html = ''.join([f'<span class="movie-genre">{genre}</span>' for genre in row['genres']])
            
            st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-title">🎬 {row['title']}</div>
                    <div class="movie-info">
                        <span class="star">⭐</span>
                        <span><b>{row['vote_average']}</b>/10</span>
                        <span>•</span>
                        <span>📅 {row['release_date'][:4]}</span>
                    </div>
                    <div style="margin: 15px 0;">
                        {genres_html}
                    </div>
                    <div class="score-badge">
                        🎯 Match Score: {round(row['hybrid_score'], 2)}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p style='font-size: 0.9rem; margin-bottom: 10px;'>Powered by Advanced ML Algorithms | Content-Based & Collaborative Filtering</p>
    <p style='font-size: 0.85rem; color: #888;'>Made with ❤️ by <span style='color: #E50914; font-weight: bold;'>Dhruv Devaliya</span></p>
    <p style='font-size: 0.75rem; color: #555; margin-top: 5px;'>© 2025 CineMatch. All Rights Reserved.</p>
</div>
""", unsafe_allow_html=True)