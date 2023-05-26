from flask import Flask, render_template, request, url_for
from .spotify import get_song_by_title
from .models import DB, RecentSearches
from .predict import get_similar_songs
# import pandas as pd
# from os.path import relpath

import warnings
warnings.filterwarnings("ignore")


def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/', methods=['POST', 'GET'])
    def root():
        if request.method == "GET": 
            return render_template('base.html',
                                   message="Please enter a song title above")
        elif request.method == 'POST':
            song_title = request.values['song_title']

            search_song, predictions = get_similar_songs(song_title)

            return render_template('base.html', search_song=search_song,
                                   predictions=predictions, message='')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html')

    return app
