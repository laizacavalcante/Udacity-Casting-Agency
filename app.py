# TODO: Encontrar problema nas rotas de PATCH da api
# TODO: Resolver problema de versionamento do flask migrate
# TODO: Verificar/ refazer testes

import os
from flask import Flask, request, jsonify, abort, redirect
from flask_cors import CORS

from models import (
    setup_db,
    db_drop_and_create_all,
    setup_migrations,
    Actor,
    Movie,
    db,
)
from auth.auth import AuthError, requires_auth

# Não está funcionando
# db_drop_and_create_all()


AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
CLIENT_ID = os.environ.get("CLIENT_ID")
CALLBACK_URI = os.environ.get("CALLBACK_URI")


def create_app(test_config=None):
    # Basic app configuration
    app = Flask(__name__)
    setup_db(app)

    # TODO migrations not working
    setup_migrations(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/")
    def index():
        return jsonify({"success": True, "message": "Casting Agency API"})

    @app.route("/login")
    def redirect_login():
        login_url = f"https://{AUTH0_DOMAIN}/authorize?audience={API_AUDIENCE}&response_type=token&client_id={CLIENT_ID}&redirect_uri={CALLBACK_URI}"
        return redirect(login_url)

    @app.route("/logout")
    def redirect_logout():
        logout_url = f"https://{AUTH0_DOMAIN}/v2/logout"
        return redirect(logout_url)

    @app.route("/actors", methods=["GET"])  # 🆗
    @requires_auth("get:actors")
    def retrieve_actors(payload):
        print("retrieve_actors")
        connection_error = False
        try:
            actors = Actor.query.order_by(Actor.name).all()
            print("retrieve_actors", actors)

        except Exception as error:
            connection_error = True
            print(error)
        finally:
            db.session.close()
        if connection_error:
            abort(422)
        else:
            if len(actors) == 0:
                abort(404)

            actors_listed = [actor.format_json() for actor in actors]
            return jsonify({"success": True, "actors": actors_listed}), 200

    @app.route("/actors/<int:actor_id>", methods=["GET"])  # 🆗
    @requires_auth("get:actors")
    def retrieve_actor(payload, actor_id):
        connection_error = False
        try:
            id_actor = Actor.query.filter(Actor.id == actor_id).one_or_none()

        except Exception as error:
            connection_error = True
            message = f"Database connection error: {error}"
            print(message)
        finally:
            db.session.close()

        if connection_error:
            abort(422)

        # TODO checar para casos sem info
        if id_actor is None:
            abort(404)

        return jsonify({"success": True, "actor": id_actor.format_json()}), 200

    @app.route("/actors/create", methods=["POST"])  # 🆗
    @requires_auth("post:actor")
    def publish_actor(payload):
        print("publish_actor")
        new_actor_json = request.get_json()
        print("publish_actor", new_actor_json)

        if new_actor_json:
            name = new_actor_json.get("name", None)
            age = new_actor_json.get("age", None)
            gender = new_actor_json.get("gender", None)
            email = new_actor_json.get("email", None)
            photo = new_actor_json.get("photo", None)
            phone = new_actor_json.get("phone", None)
            seeking_movie = new_actor_json.get("seeking_movie", None)
            print(seeking_movie)
        else:
            abort(404)

        actors_cols = [name, age, gender, email, photo, phone, seeking_movie]
        if all(var is not None for var in actors_cols):
            connection_error = False

            try:
                new_actor = Actor(
                    name=name,
                    age=age,
                    gender=gender,
                    email=email,
                    phone=phone,
                    photo=photo,
                    seeking_movie=seeking_movie,
                )
                new_actor.insert()
                print(f"add_actor -> actor {name} inserted")

                return jsonify(
                    {
                        "success": True,
                        "actor_id": new_actor.id,
                        "actors_total": len(
                            Actor.query.all()
                        ),  # TODO é necessário isso
                    }
                )
            except Exception as err:
                print("Query error, ", err)
                connection_error = True
            finally:
                db.session.close()
            if connection_error:
                abort(422)
        else:
            abort(400)

    @app.route("/actors/<int:actor_id>", methods=["PATCH"])  # 🚨🚨🚨🚨
    @requires_auth("patch:actors")
    def modify_actor(payload, actor_id):
        print("modify_actor")
        new_actor_json = request.get_json()
        print(new_actor_json)
        if new_actor_json:
            name = new_actor_json.get("name", None)
            age = new_actor_json.get("age", None)
            gender = new_actor_json.get("gender", None)
            email = new_actor_json.get("email", None)
            photo = new_actor_json.get("photo", None)
            phone = new_actor_json.get("photo", None)
            seeking_movie = new_actor_json.get("seeking_movie", None)
        else:
            abort(404)

        actors_cols = [name, age, gender, email, photo, photo, seeking_movie]
        # TODO e se eu quiser mudar apenas um único valor e não todos?
        if all(var is not None for var in actors_cols):
            connection_error = False
            try:
                actor = db.session.query(Actor).filter_by(id=actor_id).one_or_none()
                print(type(actor))
                print(type(Actor.query.get(actor_id)))
                print(actor)
            except Exception as err:
                print("Query error, ", err)
                connection_error = True

            finally:
                db.session.close()
            if connection_error:
                abort(422)

            if actor is None:
                abort(404)

            actor.name = name
            actor.name = name
            actor.age = age
            actor.age = age
            actor.gender = gender
            actor.gender = gender
            actor.email = email
            actor.email = email
            actor.phone = phone
            actor.photo = photo
            actor.seeking_movie = seeking_movie

            try:
                db.session.commit()
            except:
                db.session.rollback()
            actor_update = Actor.query.get(actor_id)

            return (
                jsonify({"success": True, "modified_actor": actor.format_json()}),
                200,
            )
        else:
            abort(400)

    @app.route("/actors/<int:actor_id>", methods=["DELETE"])  # 🆗
    @requires_auth("delete:actors")
    def delete_actor(payload, actor_id):
        connection_error = False
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
        except Exception as err:
            print("Query error, ", err)
            connection_error = True
        finally:
            db.session.close()

        if connection_error:
            abort(422)

        if actor:
            actor.delete()

            return jsonify({"success": True, "deleted_actor": actor.format_json()}), 200

    @app.route("/movies", methods=["GET"])  # 🆗
    @requires_auth("get:movies")
    def retrieve_movies(payload):
        connection_error = False
        try:
            movies = Movie.query.order_by(Movie.title).all()

        except Exception as error:
            connection_error = True
            print(error)
        finally:
            db.session.close()

        if connection_error:
            abort(422)

        if movies:
            movies_listed = [movie.format_json() for movie in movies]
            return jsonify({"success": True, "movies": movies_listed}), 200

        else:
            abort(404)

    @app.route("/movies/<int:movie_id>", methods=["GET"])  # 🆗
    @requires_auth("get:movies")
    def retrieve_movie(payload, movie_id):
        connection_error = False
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        except Exception as error:
            connection_error = True
            message = f"Database connection error: {error}"
            print(message)
        finally:
            db.session.close()
        if connection_error:
            abort(422)

        if movie is None:
            abort(404)

        return jsonify({"success": True, "movie": movie.format_json()}), 200

    @app.route("/movies/create", methods=["POST"])  # 🆗
    @requires_auth("post:movie")
    def add_movie(payload):
        # Não deveria permitir filmes do passado

        movie_json = request.get_json()
        if movie_json:
            title = movie_json.get("title", None)
            genres = movie_json.get("genres", None)
            release_date = movie_json.get("release_date", None)
            seeking_actor = movie_json.get("seeking_actor", None)
        else:
            abort(404)

        movie_cols = [title, genres, release_date, seeking_actor]
        if all(var is not None for var in movie_cols):

            try:
                movie = Movie(
                    title=title,
                    genres=genres,
                    release_date=release_date,
                    seeking_actor=seeking_actor,
                )
                movie.insert()

                return jsonify(
                    {
                        "success": True,
                        "added_movie_id": movie.id,
                        "added_movie_title": movie.title,
                        "movies_total": len(Movie.query.all()),
                    }
                )
            except:
                print("unable to insert data")
                abort(500)
            finally:
                db.session.close()

        else:
            abort(400)

    @app.route("/movies/<int:movie_id>", methods=["PATCH"])  # 🚨🚨🚨🚨
    @requires_auth("patch:movies")
    def modify_movie(payload, movie_id):
        connection_error = False
        movie_json = request.get_json()

        if movie_json:
            title = movie_json.get("title", None)
            genres = movie_json.get("genres", None)
            release_date = movie_json.get("release_date", None)
            seeking_actor = movie_json.get("seeking_actor", None)
        else:
            abort(404)

        movie_cols = [title, genres, release_date, seeking_actor]
        if all(var is not None for var in movie_cols):

            with app.app_context():

                try:
                    movie = db.session.query(Movie).filter_by(id=int(movie_id)).first()
                    movie2 = Movie.query.filter(Movie.id == movie_id).one_or_none()
                    print("movie type", type(movie))
                    print("movie2 type", type(movie2))

                except Exception as err:
                    print("Query error, ", err)
                    connection_error = True
                finally:
                    db.session.close()
                if connection_error:
                    abort(422)
                if movie is None:
                    abort(404)

                movie.title = title
                movie.genres = genres
                movie.release_date = release_date
                movie.seeking_actor = seeking_actor

                try:
                    movie.update()
                except:
                    db.session.rollback()
                # db.session.commit()

                tt = db.session.query(Movie).filter_by(id=int(movie_id)).first()
                return (
                    jsonify({"success": True, "modified_movie": tt.format_json()}),
                    200,
                )
        else:
            abort(400)

    @app.route("/movies/<int:movie_id>", methods=["DELETE"])  # 🆗
    @requires_auth("delete:movies")
    def delete_movie(payload, movie_id):
        connection_error = False
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
        except Exception as err:
            print("Query error, ", err)
            connection_error = True
        finally:
            db.session.close()

        if connection_error:
            abort(422)

        if movie:
            movie.delete()

            return jsonify({"success": True, "deleted_movie": movie.format_json()}), 200

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400

    @app.errorhandler(401)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 401, "message": "Unauthorized"}),
            401,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource Not Found"}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "Unprocessable resource"}
            ),
            422,
        )

    @app.errorhandler(500)
    def internal_server(error):
        return (
            jsonify(
                {"success": False, "error": 500, "message": "Internal server error"}
            ),
            500,
        )

    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": error.status_code,
                    "message": error.error["description"],
                }
            ),
            error.status_code,
        )

    return app


# Initializing the app for gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
    # app.run(host="0.0.0.0", port=8080, debug=True)
