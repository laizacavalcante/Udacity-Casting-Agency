
# Udacity-FSND-Casting-Agency

This project is part of the Udacity's Fullstack Nanodegree program. It is an API to retireve data from a casting agency database, that could be used for a company responsible for creating movies and managing/assigning those to movies. Here we have three roles `Executive Producer`, `Casting Director`, and `Casting Assistant` with different permissions levels.



## Getting Started

### Installation and Database Setup

Clone the repo by running

```bash
git clone https://github.com/laizacavalcante/Udacity-Casting-Agency.git
```

#### Required dependencies

- [Python 3.11.0](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python).
- [Flask](http://flask.pocoo.org/) handles requests and responses.
- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) handles cross origin requests from the frontend server.
- [Flask-Migrate](https://flask-cors.readthedocs.io/en/latest/) is used to handle SQLAlchemy database migrations for Flask applications using Alembic. The database operations are made available through the Flask command-line interface.
- [PostgreSQL](https://www.postgresql.org/docs/) is the object-relational SQL database system used.
- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM used to handle PostgreSQL database.
- [Unittest](https://docs.python.org/3/library/unittest.html) is the Python testing framework used for unit testing.
- [Auth0](https://auth0.com/docs/api/management/v2) is an adaptable authentication and authorization platform used to implement RBAC.

#### Virtual Enviornment

It is recommended to work within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
. venv/bin/activate
```

#### Installing Python Dependencies

Once the virtual environment is setup and running, install the required dependencies by navigating to the project directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages in the `requirements.txt` file.

---

## Database Setup

The project uses **PostgreSQL** databases.

- Create two databases: One for **testing** and one for **development**

```bash
createdb <database_name>
```

### Windows users
```bash
<PSQL_INSTALLATION> -U postgres -c "create database \"<DATABASE_NAME>\""  -d \"castAgency\" -a -f <database_file>"
```

- Generate database tables from the saved casting_agency.psql file or the migration files included by executing:

```bash
psql casting_agency < casting_agency.psql
```

or

```bash
python manage.py db upgrade
```

## Running the Server

Switch to the project directory and ensure that the virtual environment is running.

### To run the **development** server, execute

```bash
python3 app.py
```

---

## API

In order to use the API, users need to be authenticated. JWT tokens can be generated by logging in with the provided credentials on the hosted site.

### Endpoints

#### GET /login

Redirect the user to login page.

#### GET /logout

Logout from the user account.

#### GET /actors

- **Summary**:Fetches an array of dictionaries for each actor from the database.
- **Request Arguments**: Request Arguments: None.
- **Returns**:
  - `success` boolean
  - `actors` - an array of dictionaries for each actor from the database.

```json
{
  "actors": [
    {
      "age": 32,
      "email": "random_guy@gnmail.com",
      "name": "Random Guy",
      "gender": "male",
      "id": 3,
      "phone": "1234567892",
      "photo": "link_to_photo",
      "seeking_movie": true
    }
  ],
  "success": true
}
```

#### GET /movies

- **Summary**: Fetches an array of dictionaries for each movie from the database.
- **Request Arguments**: Request Arguments: None.
- **Returns**:
  - `success` boolean
  - `movies` - an array of dictionaries for each movie from the database.

```json
{
  "movies": [
    {
      "genres": ["TV show"],
      "id": 1,
      "release_date": "2023-08-01 00:00:00",
      "seeking_actor": true,
      "title": "Big house"
    }
  ],
  "success": true
}
```

`GET '/actors/int:actor_id'`

- **Summary**: Fetches the specific actor.
- **Request Arguments**: actor_id (integer) - the actor id.
- **Returns**:
  - `success` - boolean
  - `actor` - the actor detailed data.

```json
{
  "actor": {
    "age": 20,
    "email": "Random Actor@gnmail.com",
    "gender": "female",
    "id": 1,
    "name": "Random Actor",
    "phone": "1234567890",
    "photo_link": "Link to photo",
    "seeking_movie": true
  },
  "success": true
}
```

`GET '/movies/int:movie_id'`

- **Summary**: Fetches the specific movie.
- **Request Arguments**: Request Arguments: movie_id (integer) - the movie id.
- **Returns**:
  - `success` - boolean
  - `movie` - the movie detailed data.

```json
{
  "movie": {
    "genres": ["TV show"],
    "id": 1,
    "release_date": "2038-01-01 00:00:00",
    "seeking_actor": true,
    "title": "Some incredible movie"
  },
  "success": true
}
```

`POST '/actors/create'`

- **Summary**: Add a new actor.
- **Request Arguments** None:
  - `success` - boolean
  - `actor_id` - the new actor ID.
  - `actors_total` - number of registred actors on database.

- **Returns**:
```json
{
  "actors_total": 4,
  "actor_id": 4,
  "success": true
}
```

`POST '/movies/create'`

- **Summary**: Create a new movie.
- **Request Arguments**:

  - title (string),
  - genres (array(string)),
  - release_date (date),
  - seeking_actor (Boolean)

- **Returns**:
  - `success` - boolean
  - `movie_id` - the new movie ID.
  - `actors_total` - number of registred movies on database.

```json
{
  "actors_total": 4,
  "added_actor_full_name": "Kyle 2 Locman 2",
  "added_actor_id": 4,
  "success": true
}
```

`PATCH '/actors/int:actor_id'`

- **Summary** endpoint to modify an entry using actor id.
- **Request Arguments**:
  - actor_id (integer) - the actor id.
  - name (string),
  - age (int),
  - gender (string),
  - email (string),
  - phone (string),
  - photo (string),
  - seeking_movie (Boolean)
- **Returns**:
  - `success` - boolean
  - `modified_actor` - the modified actor with detailed data.

```json
{
  "modified_actor": {
    "age": 41,
    "email": "Random_Actor@gmail.com",
    "name": "Random Actor",
    "gender": "male",
    "id": 3,
    "phone": "1234567891",
    "photo": "Link_to_photo",
    "seeking_movie": false
  },
  "success": true
}
```

`PATCH '/movies/int:movie_id'`

- **Summary**: endpoint to modify movie entry by id.
- **Request Arguments**:
  - movie_id (integer) - the movie id.
  - title (string),
  - genres (array(string)),
  - release_date (date),
  - seeking_actor (Boolean)
- Returns:
  - `success` - boolean
  - `movie_updated` - the modified movie id.

```json
{
  "modified_movie": 1,
  "success": true
}
```

`DELETE '/actors/int:actor_id'`

- **Summary**: Delete the actor using the actor ID.
- **Request Arguments**: 
  - actor_id - the actor id.
- **Returns**:
  - `success` - boolean
  - `deleted_actor` - the deleted actor with detailed data.

```json
{
  "deleted_actor": 4,
  "success": true
}
```

`DELETE '/movies/int:movie_id'`

- **Summary**: Delete the movie using the movie ID.
- **Request Arguments**: 
  - movie_id - the movie id.
- **Returns**:
  - `success` - boolean
  - `deleted_movie` - the deleted movie with detailed data.

```json
{
  "deleted_movie": 8,
  "success": true
}
```

### Errors
- Returns: an object with these keys: success, error and message.

`Error 400`

```json
{
  "success": false,
  "error": 400,
  "message": "Bad Request"
}
```

```json
{
  "success": false,
  "error": 400,
  "message": "Permissions not included in JWT"
}
```

---
`Error 401`

```json
{
  "success": false,
  "error": 401,
  "message": "Unauthorized"
}
```


```json
{
  "success": false,
  "error": 401,
  "message": "Authorization header is expected"
}
```

```json
{
  "success": false,
  "error": 401,
  "message": "Authorization header must start with Bearer"
}
```

```json
{
  "success": false,
  "error": 401,
  "message": "User don't have sufficient permission"
}
```

---
`Error 404`

```json
{
  "success": false,
  "error": 404,
  "message": "Resource Not Found"
}
```

---
`Error 405`

```json
{
  "success": false,
  "error": 405,
  "message": "Method Not Allowed"
}
```

---
`Error 422`

```json
{
  "success": false,
  "error": 422,
  "message": "Unprocessable resource"
}
```
---
`Error 500`

```json
{
  "success": false,
  "error": 500,
  "message": "Internal server error"
}
```
