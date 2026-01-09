import pandas as pd
import os
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# Ensure model directory exists
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def load_data():
    movies = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_movies.csv'))
    credits = pd.read_csv(os.path.join(DATA_DIR, 'tmdb_5000_credits.csv'))
    return movies.merge(credits, on='title')

def clean_tags(text):
    return " ".join(ast.literal_eval(text)) if isinstance(text, str) else ""

# Processing Logic
movies = load_data()
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords']]
movies.dropna(inplace=True)

# Vectorization (The AI part)
tfidf = TfidfVectorizer(stop_words='english')
matrix = tfidf.fit_transform(movies['overview'] + " " + movies['genres'])
similarity = cosine_similarity(matrix)

# Saving to the 'model' subfolder
pickle.dump(movies, open(os.path.join(MODEL_DIR, 'movie_list.pkl'), 'wb'))
pickle.dump(similarity, open(os.path.join(MODEL_DIR, 'similarity.pkl'), 'wb'))

print(f"✅ AI Models saved successfully in: {MODEL_DIR}")