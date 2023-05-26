# Spotify Recommender

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
