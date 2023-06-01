from .spotify import get_song_by_title, get_audio_features
from .spotify import get_artist_genres, get_song_by_id
import pandas as pd
import numpy as np
import os
from joblib import load

# Set global path and model
APP_ROOT = os.path.dirname(os.path.abspath(__file__))     
VECT_PATH = os.path.join(APP_ROOT, "./model/vect.pkl")  
NEIGH_PATH = os.path.join(APP_ROOT, "./model/neigh.pkl")

vect = load(VECT_PATH)
neigh = load(NEIGH_PATH)

DF_PATH = os.path.join(APP_ROOT, "../data/final/audio_qualities.csv")
song_indices = pd.read_csv(DF_PATH)

# Columns of our X Matrix
# columns = ['popularity', 'duration_ms', 'explicit', 'danceability',
#                   'energy', 'key', 'loudness', 'mode', 'speechiness',
#                   'acousticness', 'instrumentalness', 'liveness', 'valence',
#                   'tempo', 'time_signature', 'year']


def get_similar_songs(title):
    song = get_song_by_title(title)
    song_id = song['id']
    artist_id = song['artist_id']
    song_attributes = get_audio_features(song_id)
    artist_genres = get_artist_genres(artist_id)
    genre_doc = " ".join(artist_genres)

    genre_features = np.asarray(vect.transform([genre_doc]).todense())

    song_features = np.array([[song['popularity'],
                              song_attributes['duration_ms'],
                              int(song['explicit']),
                              song_attributes['danceability'],
                              song_attributes['energy'],
                              song_attributes['key'],
                              song_attributes['loudness'],
                              song_attributes['mode'],
                              song_attributes['speechiness'],
                              song_attributes['acousticness'],
                              song_attributes['instrumentalness'],
                              song_attributes['liveness'],
                              song_attributes['valence'],
                              song_attributes['tempo'],
                              song_attributes['time_signature'],
                              pd.to_datetime(song['year']).year]])

    row = np.concatenate([song_features, genre_features], axis=1)

    _, indices = neigh.kneighbors(row, 6)

    song_ids = np.array([song_indices.iloc[song_index]['id'].values
                         for song_index in indices])[0]

    recommended_songs = [get_song_by_id(id) for id in song_ids]

    return song, recommended_songs[1:]
