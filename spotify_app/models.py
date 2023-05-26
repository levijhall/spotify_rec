# No Database required to generate predictions
# Try putting both Code-Alongs together as an extra challenge!

from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class RecentSearches(DB.Model):
    # This allows for IDs to be auto-incremented so that we can have
    # duplicate recent searches (duplicate song_id,
    # not duplicate primary key ids)
    id = DB.Column(DB.BigInteger().with_variant(DB.Integer, "sqlite"),
                   primary_key=True)
    song_id = DB.Column(DB.String(100), nullable=False)
    title = DB.Column(DB.String(200), nullable=False)
    href = DB.Column(DB.String(300), nullable=False)
    uri = DB.Column(DB.String(300), nullable=False)

    def __repr__(self):
        return f"Title: {self.title}"
