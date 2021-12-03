import spotipy
import spotipy.util as util
import pandas as pd
from functions import generate_playlist_df,generate_playlist_vector,generate_recommendation
from sklearn.preprocessing import MinMaxScaler


def genPlaylist(sp, nTracks,namePlaylist):
    
    playlist_dic = {}
    for i in sp.current_user_playlists()['items']:
        playlist_dic[i['name']] = i['uri'].split(':')[2]
    
    spotify_data = pd.read_csv("SpotifyFeatures.csv")
    playlist_df = generate_playlist_df(namePlaylist, playlist_dic, spotify_data, sp)
    spotify_features_df = spotify_data
    genre_OHE = pd.get_dummies(spotify_features_df.genre)
    
    key_OHE = pd.get_dummies(spotify_features_df.key)
    scaled_features = MinMaxScaler().fit_transform([spotify_features_df['acousticness'].values,spotify_features_df['danceability'].values,spotify_features_df['duration_ms'].values,spotify_features_df['energy'].values,spotify_features_df['instrumentalness'].values,spotify_features_df['liveness'].values,spotify_features_df['loudness'].values,spotify_features_df['speechiness'].values,spotify_features_df['tempo'].values,spotify_features_df['valence'].values])

    spotify_features_df[['acousticness','danceability','duration_ms','energy','instrumentalness','liveness','loudness','speechiness','tempo','valence']] = scaled_features.T

    spotify_features_df = spotify_features_df.drop('genre',axis = 1)
    spotify_features_df = spotify_features_df.drop('artist_name', axis = 1)
    spotify_features_df = spotify_features_df.drop('track_name', axis = 1)
    spotify_features_df = spotify_features_df.drop('popularity',axis = 1)
    spotify_features_df = spotify_features_df.drop('key', axis = 1)
    spotify_features_df = spotify_features_df.drop('mode', axis = 1)
    spotify_features_df = spotify_features_df.drop('time_signature', axis = 1)

    spotify_features_df = spotify_features_df.join(genre_OHE)
    spotify_features_df = spotify_features_df.join(key_OHE)

    spotify_features_df.shape

    playlist_vector, nonplaylist_df = generate_playlist_vector(spotify_features_df, playlist_df, 1.2)

    nonplaylist_df.shape

    top15 = generate_recommendation(spotify_data, playlist_vector, nonplaylist_df, sp,nTracks)

    return list(top15["track_id"])


if __name__ == "__main__":
    client_id = "31aa0e52bc444791bd5e4ca52a1674c5"
    client_secret= "30ac3631080340a180a8767274bc598d"

    scope = 'user-library-read'

    token = util.prompt_for_user_token(scope, client_id= client_id, client_secret=client_secret, redirect_uri='http://localhost:8080/callback')
    sp = spotipy.Spotify(auth=token)
    playlist=genPlaylist(sp,20,"El david")
    print(playlist)