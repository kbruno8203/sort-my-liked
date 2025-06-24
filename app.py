# ============================
# SECTION 1: BACKGROUND SETUP
# ============================

# LIBRARIES
import spotipy # to interact w Spotify API
from spotipy.oauth2 import SpotifyOAuth # to handle user authentication
from flask import Flask, redirect, request, session, url_for, render_template, jsonify # flask and flask utilities
from collections import Counter

# SETUP THE APP
app = Flask(__name__)
app.secret_key = 'e5c9f8e1a6b7c3d4e8f5a1b2c3d4e5f6a7b8c9d0e1f2'  # set secret key for user session management
app.config['SESSION_COOKIE_NAME'] = 'SortMyLikedSession' # configure session cookie name


# Spotify API credentials
CLIENT_ID = '1881f04983e04c8980db5280d3f80a98'  # Replace with actual client ID
CLIENT_SECRET = '618a24b406554002a6d7e84a139ccda9'  # Replace with actual client secret
REDIRECT_URI = 'http://localhost:8888/callback'  # Ensure this matches exactly with the Spotify Developer Dashboard
SCOPE = 'user-library-read playlist-modify-private playlist-modify-public user-library-modify user-top-read' # scope of what you will have access to 


# AUTHORIZE USER/SPOTIFY CLIENT
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)



# ======================
# SECTION 2: APP ROUTE
# ======================

# log in 
@app.route('/')
def login():
    # redirect to spotify authentication page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# callback catch
@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session['token_info'] = token_info
    return redirect(url_for('loading'))

# display loading to user
@app.route('/loading')
def loading():
    return render_template('loading.html')

# show user main dashboard
@app.route('/dashboard')
def dashboard():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Fetch user data
    user_data = {
        "num_liked_songs": get_num_liked_songs(sp),
        "song_distribution_by_year": get_song_distribution_by_year(sp),
        "most_frequently_liked_artists": get_most_frequently_liked_artists(sp),
    }

    return render_template('dashboard.html', user_data=user_data)


# ============================
# SECTION 3: HELPER FUNCTIONS
# ============================
def get_num_liked_songs(sp):
    results = sp.current_user_saved_tracks(limit=1) # use fetch liked songs?
    return results['total']

def get_song_distribution_by_year(sp):
    liked_songs = fetch_liked_songs(sp)
    years = [int(song['track']['album']['release_date'][:4]) for song in liked_songs]
    year_counts = {year: years.count(year) for year in set(years)}
    return year_counts

def get_most_frequently_liked_artists(sp):
    liked_tracks = fetch_liked_songs(sp)
    artist_count = Counter()
    artist_images = {}

    for item in liked_tracks:
        track = item['track']
        for artist in track['artists']:
            artist_name = artist['name']
            artist_count[artist_name] += 1
            # Fetch artist image if not already stored
            if artist_name not in artist_images:
                try:
                    artist_info = sp.artist(artist['id'])
                    if artist_info['images']:
                        artist_images[artist_name] = artist_info['images'][0]['url']
                    else:
                        artist_images[artist_name] = ""
                except Exception:
                    artist_images[artist_name] = ""

    top3 = artist_count.most_common(3)
    result = []
    for i, (artist, count) in enumerate(top3, 1):
        result.append({
            "ranking": i,
            "name": artist,
            "image": artist_images.get(artist, ""),
            "count": count
        })
    return result

def fetch_liked_songs(sp):
    results = sp.current_user_saved_tracks()
    liked_songs = results['items']

    while results['next']:
        results = sp.next(results)
        liked_songs.extend(results['items'])

    return liked_songs

# ============
# RUN THE APP
# ============
if __name__ == '__main__':
    app.run(port=8888)
