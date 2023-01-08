import os
import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    ForeignKey,
    DateTime,
    ARRAY,
    CheckConstraint,
    Enum,
)
from sqlalchemy.orm import relationship
from flask_migrate import Migrate
from datetime import datetime


database_name = "castAgency"
username = os.environ.get("DB_USERNAME")
password = os.environ.get("PASSWORD")
database_path = f"postgresql://{username}:{password}@localhost:5432/{database_name}"
print(f"DB_USERNAME {username}, {password}, {database_path}")


db = SQLAlchemy()
migrate = Migrate()


class DbTransactions:
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class GenderType(enum.Enum):
    male = "male"
    female = "female"
    undeclared = "undeclared"


class StatusType(enum.Enum):
    accept = "accept"
    reject = "reject"
    in_process = "evaluation"


class Movie(db.Model, DbTransactions):
    __tablename__ = "Movies"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(ARRAY(String(120)), nullable=False)
    release_date = Column(DateTime, default=datetime.now)
    seeking_actor = Column(Boolean, nullable=False, default=True)
    movie_castings = relationship("Casting", back_populates="movie_cast")

    __table_args__ = (
        CheckConstraint(
            release_date > datetime.today().strftime("%Y/%m/%d"),
            name="check_release_date",
        ),
        {},
    )

    def __init__(self, title, genres, release_date, seeking_actor):
        self.title = title
        self.genres = genres
        self.release_date = release_date
        self.seeking_actor = seeking_actor

    # TODO Rever função
    def format_json(self):
        ordered_keys = ["id", "title", "genres", "release_date", "seeking_actor"]

        data = {
            "id": self.id,
            "title": self.title,
            "genres": self.genres,
            "release_date": str(self.release_date),
            "seeking_actor": self.seeking_actor,
        }

        ordered_data = {key: data[key] for key in ordered_keys}

        return ordered_data

    def __repr__(self):
        return f"""Movie: {self.id}, {self.title} ({self.genres}),
            need actors: {self.seeking_actor}, 
            release_date: {self.release_date}"""


class Actor(db.Model, DbTransactions):
    __tablename__ = "Actors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderType), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    phone = Column(String(120), unique=True, nullable=False)
    photo = Column(String(600), nullable=False)  # TODO Add checagem de link
    seeking_movie = Column(Boolean, nullable=False, default=False)
    actor_castings = relationship("Casting", back_populates="actor_cast")

    __table_args__ = (CheckConstraint(age > 0, name="check_valid_age"), {})

    def __init__(self, name, age, gender, email, phone, photo, seeking_movie):
        self.name = name
        self.age = age
        self.gender = gender
        self.email = email
        self.phone = phone
        self.photo = photo
        self.seeking_movie = seeking_movie

    def format_json(self):

        ordered_keys = [
            "id",
            "name",
            "age",
            "gender",
            "email",
            "phone",
            "photo",
            "seeking_movie",
        ]

        data = {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": str(self.gender.value),
            "email": self.email,
            "phone": self.phone,
            "photo": self.photo,
            "seeking_movie": self.seeking_movie,
        }

        ordered_data = {key: data[key] for key in ordered_keys}

        return ordered_data

    def __repr__(self):
        return (
            f"""Actor: {self.id}, {self.name} {self.name} ({self.age}, {self.gender})"""
        )


class Casting(db.Model, DbTransactions):
    __tablename__ = "Casting"

    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("Actors.id", ondelete="cascade"))
    movie_id = Column(Integer, ForeignKey("Movies.id", ondelete="cascade"))
    role = Column(String(120), nullable=False)

    actor_cast = db.relationship("Actor", back_populates="actor_castings")
    movie_cast = db.relationship("Movie", back_populates="movie_castings")

    def __init__(self, actor_id, movie_id, role):
        self.actor_id = actor_id
        self.movie_id = movie_id
        self.role = role

    def format_json(self):
        return {
            "id": self.id,
            "movie_name": self.movies.title,
            "actor_name": self.actors.name,
            "role": self.role,
        }

    def __repr__(self):
        return f"""movie: {self.movies.title}, 
            actor: {self.actors.name} 
            role: {self.role}"""


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        db_insert_data()


def setup_migrations(app):
    migrate = Migrate(app, db)  # setup_migrations
    migrate.init_app(app, db)  # render_as_batch=False


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()


def db_insert_data():

    movie1 = Movie(
        title="Big house",
        genres=["TV show"],
        release_date="2023.08.01",
        seeking_actor=True,
    )

    movie2 = Movie(
        title="Smile",
        genres=["Comedy"],
        release_date="2023.12.12",
        seeking_actor=True,
    )

    movie3 = Movie(
        title="Cry cry cry",
        genres=["Drama"],
        release_date="2024.12.12",
        seeking_actor=True,
    )

    movie1.insert()
    movie2.insert()
    movie3.insert()

    actor1 = Actor(
        name="Sandy",
        age="20",
        gender=GenderType.female,
        email="sandccyproom@gnmail.com",
        phone="1234567890",
        photo="https://images.unsplash.com/photo-1631084655463-e671365ec05f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
        seeking_movie=True,
    )
    actor1.insert()

    actor2 = Actor(
        name="Luna",
        age="25",
        gender=GenderType.female,
        email="lunagccrey@gnmail.com",
        phone="1234567891",
        photo="https://images.unsplash.com/photo-1508326099804-190c33bd8274?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=774&q=80",
        seeking_movie=False,
    )
    actor2.insert()

    actor3 = Actor(
        name="John",
        age="32",
        gender=GenderType.male,
        email="johnhccolms@gnmail.com",
        phone="1234567892",
        photo="https://images.unsplash.com/photo-1542583701-20d3be307eba?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=770&q=80",
        seeking_movie=True,
    )

    actor3.insert()

    casting1 = Casting(
        actor_id=1,
        movie_id=1,
        role="main",
    )

    casting2 = Casting(
        actor_id=3,
        movie_id=1,
        role="second",
    )

    casting3 = Casting(
        actor_id=3,
        movie_id=2,
        role="second",
    )

    casting1.insert()
    casting2.insert()
    casting3.insert()
