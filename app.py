# ============================
# SECTION 1: BACKGROUND SETUP
# ============================

# LIBRARIES
import spotipy # to interact w Spotify API
from spotipy.oauth2 import SpotifyOAuth # to handle user authentication
from flask import Flask, redirect, request, session, url_for, render_template, jsonify # flask and flask utilities


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
       # "liked_songs_not_in_playlist": get_liked_songs_not_in_playlist(sp),
        "song_distribution_by_year": get_song_distribution_by_year(sp),
        "most_frequently_liked_artists": get_most_frequently_liked_artists(sp),
       # "most_played_liked_songs": get_most_played_liked_songs(sp),
       # "genre_breakdown": get_genre_breakdown(sp)
    }

    return render_template('dashboard.html', user_data=user_data)


# ============================
# SECTION 3: HELPER FUNCTIONS
# ============================
def get_num_liked_songs(sp):
    results = sp.current_user_saved_tracks(limit=1) # use fetch liked songs?
    return results['total']


def get_liked_songs_not_in_playlist(sp):
    """
    Identify liked songs that are not in any playlist.

    Args:
        sp (spotipy.Spotify): Authenticated Spotify client.

    Returns:
        dict: {
            'count': int,  # Number of liked songs not in any playlist
            'songs': list of dicts: [{ 'name': str, 'artist': str, 'album': str, 'id': str }]
        }
    """
    # Step 1: Fetch all liked songs
    liked_tracks = {}
    results = sp.current_user_saved_tracks(limit=50)

    while results:
        for item in results['items']:
            track = item['track']
            track_id = track['id']
            liked_tracks[track_id] = {
                'name': track['name'],
                'artist': ", ".join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'id': track_id
            }
        results = sp.next(results) if results['next'] else None

    # Step 2: Fetch all user playlists and their tracks
    user_id = sp.current_user()['id']
    playlist_tracks = set()

    playlists = sp.current_user_playlists(limit=50)
    while playlists:
        for playlist in playlists['items']:
            playlist_id = playlist['id']
            tracks = sp.playlist_tracks(playlist_id, fields="items.track.id", limit=100)
            while tracks:
                for item in tracks['items']:
                    if item['track']:
                        playlist_tracks.add(item['track']['id'])
                tracks = sp.next(tracks) if tracks['next'] else None
        playlists = sp.next(playlists) if playlists['next'] else None

    # Step 3: Find liked songs not in any playlist
    songs_not_in_playlist = {track_id: data for track_id, data in liked_tracks.items() if track_id not in playlist_tracks}

    return {
        'count': len(songs_not_in_playlist),
        'songs': list(songs_not_in_playlist.values())  # Convert dict to list for easier processing
    }

#def get_liked_songs_not_in_playlist(sp):
    # Example logic to determine liked songs not in a playlist
    #return 25  # Placeholder valueget_

def get_song_distribution_by_year(sp):
    liked_songs = fetch_liked_songs(sp)
    years = [int(song['track']['album']['release_date'][:4]) for song in liked_songs]
    year_counts = {year: years.count(year) for year in set(years)}
    return year_counts


from collections import Counter

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


def get_most_played_liked_songs(sp):
    results = sp.current_user_top_tracks(limit=5)
    return results['items']

def get_genre_breakdown(sp):
    # Example logic to get genre breakdown
    return []  # Placeholder value

def fetch_liked_songs(sp):
    results = sp.current_user_saved_tracks()
    liked_songs = results['items']

    while results['next']:
        results = sp.next(results)
        liked_songs.extend(results['items'])

    return liked_songs


def get_80s_songs(sp):
    """Fetch all liked songs and filter for songs released between 1980-1989."""
    liked_tracks = []
    results = fetch_liked_songs(sp)
    
    while results:
        for item in results['items']:
            track = item['track']
            release_year = int(track['album']['release_date'][:4]) if track['album']['release_date'] else None
            if release_year and 1980 <= release_year <= 1989:
                liked_tracks.append(track['id'])

        results = sp.next(results) if results['next'] else None

    return liked_tracks

def create_80s_playlist(sp):
    """Create a new playlist and add 80s songs to it."""
    user_id = sp.current_user()['id']
    track_ids = get_80s_songs(sp)

    if not track_ids:
        return "No songs from the 1980s found in your liked tracks."

    playlist = sp.user_playlist_create(user_id, "My 80s Playlist", public=False, description="All my liked songs from the 1980s")
    playlist_id = playlist['id']

    # Add songs in batches of 100 (Spotify API limit)
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i:i+100])

    return f"Playlist created! <a href='{playlist['external_urls']['spotify']}' target='_blank'>Listen here</a>"






# ============
# RUN THE APP
# ============
if __name__ == '__main__':
    app.run(port=8888)
