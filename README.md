# Spotify Recommender Starter App

### Startup Instructions

1) Clone the repository and change directories to the outer project folder:

`cd DS_code_along_11.2_deploying_ML_models_starter`

2) Ensure that all dependencies are properly installed:

 `pipenv install`

3) Activate the virtual enviroment with:

`pipenv shell`

4) Start up the Flask app.

`flask run`

5) Obtain [API keys from Spotify.](https://developer.spotify.com/dashboard/login) and put them in a `.env` file

`touch .env`

```
FLASK_APP=spotify_app
FLASK_DEBUG=1
CLIENT_ID=YOUR_CLIENT_ID_HERE
CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE
```

6) Visit `localhost:5000` to view the running app

[127.0.0.1:5000/](http://127.0.0.1:5000/)
