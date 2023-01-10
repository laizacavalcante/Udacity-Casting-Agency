import os
from dotenv import load_dotenv
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import (
    setup_db,
    db_drop_and_create_all,
    Movie,
    Actor,
    db_insert_data
)

load_dotenv()


CASTING_ASSISTANT_TOKEN = os.getenv("CASTING_ASSISTANT_TOKEN")
CASTING_DIRECTOR_TOKEN = os.getenv("CASTING_DIRECTOR_TOKEN")
PRODUCER_TOKEN = os.getenv("PRODUCER_TOKEN")
INVALID_TOKEN = os.getenv("INVALID_TOKEN")
EXPIRED_TOKEN = os.getenv("EXPIRED_TOKEN")


class CastingAgencyCase(unittest.TestCase):
    """
    This class represents the casting agency test case
    """

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client

        # Setting up Database connection
        self.database_path = "postgresql://{}:{}@localhost:{}/{}".format(
            "postgres", "admin", 5432, "castAgencyTests")

        print("Tests -> Setting up Database connection", self.database_path)

        setup_db(self.app, self.database_path)
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            db_drop_and_create_all()
            db_insert_data()


    def tearDown(self):
        """Executed after reach test"""
        pass

    # ---------------------------------------#
    # Test actors endpoints
    # ---------------------------------------#
    def test_retrieve_actors(self):
        res = self.client().get(
            "/actors", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actors"])
        self.assertGreater(len(data["actors"]), 0)

    def test_401_retrieve_actors_without_authorization_headers(self):
        res = self.client().get("/actors")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Authorization header is expected")

    def test_401_expired_token_error(self):
        res = self.client().get(
            "/actors", headers={"Authorization": f"Bearer {EXPIRED_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "Token expired.")

    def test_405_use_not_allowed_method(self):
        res = self.client().post(
            "/actors", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    def test_retrieve_actor(self):
        with self.app.app_context():
            actors = Actor.query.all()
        actor_id = actors[0].id
        res = self.client().get(
            "/actors/" + str(actor_id),
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["actor"]), 0)
        self.assertEqual(data["actor"]["id"], actor_id)

    def test_404_retrieve_actor_which_does_not_exist(self):
        res = self.client().get(
            "/actors/100000",
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_add_actor(self):
        actor = {
            "name": "test_actor",
            "age": 18,
            "gender": "male",
            "email": "testuser@gmail.com",
            "phone": "0000000000",
            "photo": "artist photo link",
            "seeking_movie": True,
        }
        res = self.client().post(
            "/actors/create",
            data=json.dumps(actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor_id"])

    def test_422_add_actor_with_not_enough_data(self): # ❗
        actor = {
            "name": "test_actor",
        }
        res = self.client().post(
            "/actors/create",
            data=json.dumps(actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    def test_422_add_actor_with_incorrect_data_format(self):
        actor = {
            "name": "test_actor",
            "age": "NOT INTEGER!!!",
            "gender": "male",
            "email": "testuser@gmail.com",
            "phone": "0000000000",
            "photo": "photo link to actor",
            "seeking_movie": True,
        }
        res = self.client().post(
            "/actors/create",
            data=json.dumps(actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable resource")

    def test_401_add_actor_unauthorized(self):
        actor = {
            "name": "test_actor",
            "age": 18,
            "gender": "male",
            "email": "testuser@gmail.com",
            "phone": "0000000000",
            "photo": "https://images.unsplash.com/photo-1631084655463-e671365ec05f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
            "seeking_movie": True,
        }
        res = self.client().post(
            "/actors/create",
            data=json.dumps(actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")

    def test_modify_actor(self):
        with self.app.app_context():
            actor = Actor.query.filter(Actor.id == 1).one_or_none()
        modified_actor = {
            "name": "Sandy",
            "age": 20,
            "gender": "female",
            "email": "sandyproom@gmail.com",
            "phone": "1234567890",
            "photo": "link to photo",
            "seeking_movie": True,
        }
        res = self.client().patch(
            "/actors/" + str(actor.id),
            data=json.dumps(modified_actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["actor_updated"])
        self.assertEqual(data["actor_updated"]["id"], actor.id)

    def test_404_modify_actor_which_does_not_exist(self):
        modified_actor = {
            "name": "Sandy",
            "age": "20",
            "gender": "female",
            "email": "sandyproom@gmail.com",
            "phone": "1234567890",
            "photo": "https://images.unsplash.com/photo-1631084655463-e671365ec05f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
            "seeking_movie": True,
        }
        res = self.client().patch(
            "/actors/10000",
            data=json.dumps(modified_actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_401_modify_actor_unauthorized(self): # ❗
        print("test_401_modify_actor_unauthorized")
        with self.app.app_context():
            actor = Actor.query.filter(Actor.id == 1).one_or_none()
        print(actor)
        modified_actor = {
            "name": "Sandy",
            "age": "20",
            "gender": "female",
            "email": "sandyproom@gmail.com",
            "phone": "1234567890",
            "photo": "https://images.unsplash.com/photo-1631084655463-e671365ec05f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
            "seeking_movie": True,
        }
        res = self.client().patch(
            "/actors/" + str(actor.id),
            data=json.dumps(modified_actor),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")

    def test_delete_actor(self):
        res = self.client().delete(
            "/actors/1", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted_actor"])
        self.assertEqual(data["deleted_actor"]["id"], 1)

    def test_404_delete_actor_which_does_not_exist(self):
        res = self.client().delete(
            "/actors/10000",
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_401_delete_actor_unauthorized(self):
        res = self.client().delete(
            "/actors/1", headers={"Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")

    # ---------------------------------------#
    # Test movies endpoints
    # ---------------------------------------#
    def test_retrieve_movies(self):
        res = self.client().get(
            "/movies", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movies"])
        self.assertGreater(len(data["movies"]), 0)

    def test_401_retrieve_movies_with_no_authorization_headers(self):
        res = self.client().get("/movies")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Authorization header is expected")

    def test_405_use_not_allowed_method(self):
        res = self.client().post(
            "/movies", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Method Not Allowed")

    def test_retrieve_movie(self):
        with self.app.app_context():
            movies = Movie.query.all()
        movie_id = movies[0].id
        res = self.client().get(
            "/movies/" + str(movie_id),
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["movie"]), 0)
        self.assertEqual(data["movie"]["id"], movie_id)

    def test_404_retrieve_movie_which_does_not_exist(self):
        res = self.client().get(
            "/movies/100000",
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_add_movie(self):
        movie = {
            "title": "test_movie",
            "genres": ["test_movie"],
            "release_date": "2040/01/01",
            "seeking_actor": True,
        }
        res = self.client().post(
            "/movies/create",
            data=json.dumps(movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["movie_id"])

    def test_422_add_movie_with_not_enough_data(self): #❗
        movie = {
            "title": "test_movie",
            "seeking_actor": True,
        }
        res = self.client().post(
            "/movies/create",
            data=json.dumps(movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")

    def test_422_add_movie_with_incorrect_data_format(self):
        movie = {
            "title": "test_movie",
            "genres": ["test_movie"],
            "release_date": "2040/0101",
            "seeking_actor": False,
        }
        res = self.client().post(
            "/movies/create",
            data=json.dumps(movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable resource")

    def test_401_add_movie_unauthorized(self):
        movie = {
            "title": "test_movie",
            "genres": ["test_movie"],
            "release_date": "2040/01/01",
            "seeking_actor": True,
        }
        res = self.client().post(
            "/movies/create",
            data=json.dumps(movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")

    def test_modify_movie(self):
        with self.app.app_context():
            movie = Movie.query.filter(Movie.id == 1).one_or_none()
        modified_movie = {
            "title": "Smiles",
            "genres": ["Comedy"],
            "release_date": "2023/12/12",
            "seeking_actor": True,
        }
        res = self.client().patch(
            "/movies/" + str(movie.id),
            data=json.dumps(modified_movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["movie_updated"]["id"], movie.id)

    def test_404_modify_movie_which_does_not_exist(self):
        modified_movie = {
            "title": "Smiles",
            "genres": ["Comedy"],
            "release_date": "2023/12/12",
            "seeking_actor": True,
        }
        res = self.client().patch(
            "/movies/10000",
            data=json.dumps(modified_movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {PRODUCER_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_401_modify_movie_unauthorized(self):
        with self.app.app_context():
            movie = Movie.query.filter(Movie.id == 1).one_or_none()
        modified_movie = {
            "title": "Smiles",
            "genres": ["Comedy"],
            "release_date": "2023/12/12",
            "seeking_actor": True,
        }
        res = self.client().patch(
            "/movies/" + str(movie.id),
            data=json.dumps(modified_movie),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}",
            },
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")

    def test_delete_movie(self):
        res = self.client().delete(
            "/movies/1", headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted_movie"])
        self.assertEqual(data["deleted_movie"]["id"], 1)

    def test_404_delete_movie_which_does_not_exist(self):
        res = self.client().delete(
            "/movies/10000",
            headers={"Authorization": f"Bearer {PRODUCER_TOKEN}"},
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_401_delete_movie_unauthorized(self): # ❗
        res = self.client().delete(
            "/movies/1", headers={"Authorization": f"Bearer {CASTING_ASSISTANT_TOKEN}"}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "User don't have sufficient permission")


if __name__ == "__main__":
    unittest.main()
