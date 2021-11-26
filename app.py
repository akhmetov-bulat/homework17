# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

director_ns = api.namespace('/directors')
genre_ns = api.namespace('/genres')
movie_ns = api.namespace('/movies')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        req =request.args
        page = int(req.get('page', 1))
        limit = int(req.get('limit', 10))
        offset = (page-1)*limit
        if all (key in req.keys() for key in ("director_id","genre_id")):
            try:
                director_id = int(req.get('director_id'))
                genre_id = int(req.get('genre_id'))
                movies = db.session.query(Movie).filter(Movie.director_id==director_id, Movie.genre_id==genre_id).all()
            except:
                return "", 404
        elif 'director_id' in req.keys():
            try:
                director_id = int(req.get('director_id'))
                movies = db.session.query(Movie).filter(Movie.director_id==director_id).all()
            except:
                return "", 404
        elif 'genre_id' in req.keys():
            try:
                genre_id = int(req.get('genre_id'))
                movies = db.session.query(Movie).filter(Movie.genre_id==genre_id).all()
            except:
                return "", 404
        else:
            movies = db.session.query(Movie).limit(limit).offset(offset).all()
        movies_list = movies_schema.dump(movies)
        return movies_list, 200


@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = db.session.query(Movie).get(id)
        if movie:
            movie_json = movie_schema.dump(movie)
            return movie_json, 200
        return '', 404


@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        req =request.args
        directors = db.session.query(Director).all()
        directors_list = directors_schema.dump(directors)
        return directors_list, 200


@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        director = db.session.query(Director).get(id)
        if director:
            director_json = director_schema.dump(director)
            return director_json, 200
        return '', 404


if __name__ == '__main__':
    app.run(debug=True)
