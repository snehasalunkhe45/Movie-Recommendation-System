import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Load your existing Hollywood data
movies_hollywood = pickle.load(open('model/movie_list.pkl', 'rb'))

# --- DEBUG: Print columns to terminal to see what we have ---
print("Hollywood Columns found:", movies_hollywood.columns.tolist())

# 2. Load your new Bollywood CSV
bollywood_raw = pd.read_csv('data/bollywood_movies.csv')

# 3. Create Bollywood dataframe with same logic as your Hollywood tags
bollywood = pd.DataFrame()
bollywood['title'] = bollywood_raw['movie_name']
# Creating tags from available Bollywood columns
bollywood['tags'] = (
    bollywood_raw['genre'].fillna('') + " " + 
    bollywood_raw['lead_actor'].fillna('') + " " + 
    bollywood_raw['director'].fillna('')
)

# 4. Handle the 'id' and 'tags' mismatch
# If Hollywood is missing 'id', we create it.
if 'id' not in movies_hollywood.columns:
    movies_hollywood['id'] = range(0, len(movies_hollywood))

bollywood['id'] = range(len(movies_hollywood), len(movies_hollywood) + len(bollywood))

# 5. Combine only 'title', 'id', and 'tags'
# We ensure Hollywood has 'tags' column. If not, it might be named something else like 'overview'
if 'tags' not in movies_hollywood.columns:
    # If your Hollywood data uses 'overview', rename it to 'tags'
    if 'overview' in movies_hollywood.columns:
        movies_hollywood.rename(columns={'overview': 'tags'}, inplace=True)
    else:
        # Emergency: Create an empty tags column so the merge doesn't crash
        movies_hollywood['tags'] = ""

# Now merge safely
movies_combined = pd.concat([
    movies_hollywood[['id', 'title', 'tags']], 
    bollywood[['id', 'title', 'tags']]
], ignore_index=True)

# 6. RE-TRAIN Similarity
cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(movies_combined['tags'].values.astype('U')).toarray()
new_similarity = cosine_similarity(vector)

# 7. Save updated models
pickle.dump(movies_combined, open('model/movie_list.pkl', 'wb'))
pickle.dump(new_similarity, open('model/similarity.pkl', 'wb'))

print(f"Success! Total movies now: {len(movies_combined)}")