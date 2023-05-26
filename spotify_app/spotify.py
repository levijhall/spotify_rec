import requests
from os import getenv


def authenticate():
    AUTH_URL = 'https://accounts.spotify.com/api/token'

    # POST
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': getenv('CLIENT_ID'),
        'client_secret': getenv('CLIENT_SECRET'),
    })

    # convert the response to JSON
    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    return access_token


def get_song_by_title(title):

    # Get an authentication token
    token = authenticate()

    # Base URL for Query
    BASE_URL = 'https://api.spotify.com/v1/'

    # Add authentication token to the request headers
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Remove quotation marks from title
    # These could mess up the URL
    title = title.replace('"', '')
    title = title.replace("'", '')
    # Build a string of the URL that we want to query
    query_url = BASE_URL + 'search?q=track:' + title \
        + "&type=track&offset=0&limit=1"
    # Query the Spotify API for the song
    response = requests.get(query_url, headers=headers)
    # Parse the response into a dictionary (JSON)
    response = response.json()

    # The API returns many songs in order of relevancy/popularity
    # We'll just grab the first one and assume it's the best result
    if response['tracks']['items']:
        first_song = response['tracks']['items'][0]
        # print(first_song)
        # print(first_song['artists'][0]['id'])
        # Grabbing only the portions of the response that we want
        # to save in the DB
        song = {'id': first_song['id'],
                'title': first_song['name'],
                'href': first_song['href'],
                'uri': first_song['uri'],
                'popularity': first_song['popularity'],
                'explicit': first_song['explicit'],
                'year': first_song['album']['release_date'],
                'artist_id': first_song['artists'][0]['id']}
        return song
    else:
        return False


def get_audio_features(id):
    # https://api.spotify.com/v1/audio-features/{id}

    # Get an authentication token
    token = authenticate()

    # Base URL for Query
    BASE_URL = 'https://api.spotify.com/v1/'

    # Add authentication token to the request headers
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Build a string of the URL that we want to query
    query_url = BASE_URL + 'audio-features/' + id
    # Query the Spotify API for the song
    response = requests.get(query_url, headers=headers)
    # Parse the response into a dictionary (JSON)
    response = response.json()

    return response


def get_artist_genres(artist_id):
    # https://api.spotify.com/v1/artists/{id}

    # Get an authentication token
    token = authenticate()

    # Base URL for Query
    BASE_URL = 'https://api.spotify.com/v1/'

    # Add authentication token to the request headers
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Build a string of the URL that we want to query
    query_url = BASE_URL + 'artists/' + artist_id
    # Query the Spotify API for the song
    response = requests.get(query_url, headers=headers)
    # Parse the response into a dictionary (JSON)
    response = response.json()

    if len(response['genres']) == 0:
        return ['']
    else:
        return response['genres']


def get_song_by_id(song_id):

    # print(song_id)

    # https://api.spotify.com/v1/tracks/{id}

    # Get an authentication token
    token = authenticate()

    # Base URL for Query
    BASE_URL = 'https://api.spotify.com/v1/'

    # Add authentication token to the request headers
    headers = {
        'Authorization': 'Bearer {token}'.format(token=token)
    }

    # Build a string of the URL that we want to query
    query_url = BASE_URL + 'tracks/' + song_id
    # Query the Spotify API for the song
    response = requests.get(query_url, headers=headers)
    # Parse the response into a dictionary (JSON)
    response = response.json()

    track = {'title': response['name'],
             'artist': response['artists'][0]['name'],
             'uri': response['uri'],
             'href': response['href'],
             'song_id': response['id']}

    # print(response['name'])
    # print(response['artists'][0]['name'])
    # print(response['uri'])
    # print(response['href'])

    return track


if __name__ == '__main__':
    pass
    # Test things out down here
