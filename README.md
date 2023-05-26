# Spotify Recommender

Makes use of the a dataset of Spotify Web API values created by Yamac Eren Ay, and is [available through Kaggle](https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks).

Documentation of values in the dataset can be found in the [official documentation for the API](https://developer.spotify.com/documentation/web-api).

### To run

1) Set up the virtual enviroment with `pipenv install`

2) Activate the virtual enviroment with: `pipenv shell`

3) Start up the Flask app. `flask run`

4) Obtain [API keys from Spotify.](https://developer.spotify.com/dashboard/login) and put them in a `.env` file


```
FLASK_APP=spotify_app
FLASK_DEBUG=1
CLIENT_ID=YOUR_CLIENT_ID_HERE
CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
```

5) Flask will launch by default under `localhost:5000`