import pandas as pd
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Load your dataset (I recommend downloading tmdb_5000_movies.csv from Kaggle)
# For now, let's use a sample to ensure it runs immediately
movies = pd.DataFrame({
    'id': [19995, 285, 206647, 49026, 49529, 100], 
    'title': ['Avatar', 'Pirates of the Caribbean', 'Spectre', 'The Dark Knight Rises', 'John Carter', 'Pathaan'],
    'genres': ['Action Adventure Fantasy', 'Action Adventure', 'Action Crime', 'Action Crime Drama', 'Action Adventure', 'Action Thriller'],
    'overview': ['A paraplegic Marine...', 'Captain Barbossa...', 'A cryptic message...', 'Following the death...', 'John Carter is...', 'An Indian spy...']
})

# --- AI DATA PREPROCESSING ---
def create_soup(x):
    return x['genres'] + ' ' + x['overview']

movies['soup'] = movies.apply(create_soup, axis=1)

# --- VECTORIZATION ---
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['soup'])

# --- SIMILARITY MATRIX ---
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save models to use in your UI
pickle.dump(movies, open('movie_list.pkl', 'wb'))
pickle.dump(cosine_sim, open('similarity.pkl', 'wb'))

print("AI Models Saved Successfully!")