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
        total_pages = db.session.query(Movie).count()
        data_body = {
                      "data": movies_list,
                      "pagination": {
                                   "current_page": page,
                                   "total_pages": total_pages,
                                   "items_per_page": limit
                                  }
                      }
        return data_body, 200
        # return movies_list, 200

    def post(self):
        movie_json = request.json
        movie = Movie(**movie_json)
        with db.session.begin():
            db.session.add(movie)
        return f"/movies/{movie.id}", 201


@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        movie = db.session.query(Movie).get(id)
        if movie:
            movie_json = movie_schema.dump(movie)
            return movie_json, 200
        return '', 404

    def put(self, id):
        movie = db.session.query(Movie).get(id)
        movie_json = request.json
        if not movie:
            return "", 404
        try:
            movie.id = movie_json['id']
            movie.title = movie_json['title']
            movie.description =movie_json['description']
            movie.trailer = movie_json['trailer']
            movie.year =movie_json['year']
            movie.rating = movie_json['rating']
            movie.genre_id = movie_json['genre_id']
            movie.director_id = movie_json['director_id']
        except:
            return "", 400
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, id):
        movie = db.session.query(Movie).get(id)
        if not movie:
            return "", 404
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        req =request.args
        directors = db.session.query(Director).all()
        directors_list = directors_schema.dump(directors)
        return directors_list, 200

    def post(self):
        director_json = request.json
        director = Director(**director_json)
        with db.session.begin():
            db.session.add(director)
        return f"/directors/{director.id}", 201

@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id):
        director = db.session.query(Director).get(id)
        if director:
            director_json = director_schema.dump(director)
            return director_json, 200
        return '', 404

    def put(self, id):
        director = db.session.query(Director).get(id)
        director_json = request.json
        if not director:
            return "", 404
        try:
            director.id = director_json['id']
            director.name = director_json['name']
        except:
            return "", 400
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, id):
        director = db.session.query(Director).get(id)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        genres_list = genres_schema.dump(genres)
        return genres_list, 200

    def post(self):
        genre_json = request.json
        genre = Genre(**genre_json)
        with db.session.begin():
            db.session.add(genre)
        return f"/genres/{genre.id}", 201

@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id):
        genre = db.session.query(Genre).get(id)
        if genre:
            genre_json = genre_schema.dump(genre)
            return genre_json, 200
        return '', 404

    def put(self, id):
        genre = db.session.query(Genre).get(id)
        genre_json = request.json
        if not genre:
            return "", 404
        try:
            genre.id = genre_json['id']
            genre.name = genre_json['name']
        except:
            return "", 400
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, id):
        genre = db.session.query(Genre).get(id)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
