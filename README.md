# Pop Mart Collection Tracker
A lightweight Flask application for tracking Pop Mart blind‑box collections. Each collection can contain multiple figurines, and the app provides a simple interface for adding, editing, and organizing them.

This project started as a simple Pop Mart tracker, similar in structure to my TCG tracker but built with Flask instead of Django. I used SQLAlchemy to model collections and figurines cleanly, and Alembic handled schema changes as the project evolved.

## Features
- Create and manage Pop Mart collections
- Add figurines inside each collection
- Upload and display collection images
- Edit or delete collections and figurines
- SQLite database for local storage
- SQLAlchemy ORM for model definitions and relationships
- Alembic migrations for schema updates

## Tech Stack
| Component       | Purpose                            |
|-----------------|------------------------------------|
| Flask           | Web framework and routing          |
| SQLite          | Lightweight local database         |
| SQLAlchemy ORM  | Models, relationships, and queries |
| Alembic         | Database schema migrations         |
| Jinja2          | HTML templating                    |
| HTML/CSS        | UI layout and styling              |

## Why SQLAlchemy + Alembic?
Most of my earlier Flask apps used raw SQLite without an ORM.
For this project, I needed:

- collections
- figurines inside collections
- a clean relationship between them
- the ability to add new fields later

SQLAlchemy made the data model easy to work with, and Alembic handled schema updates (like adding price_per_box) without recreating the database.

## Project Structure
```
.
├── app.py                # Flask app + routes
├── models.py             # SQLAlchemy ORM models
├── migrations/           # Alembic migration scripts
├── static/               # CSS + uploaded images
├── templates/            # HTML templates
├── requirements.txt
└── .gitignore
```
The instance/ folder (database + uploads) is intentionally excluded from version control.

## Running the App
1. Create a virtual environment
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run the app:
```
flask run
```
The app will start on http://127.0.0.1:5003/.

## Database Migrations
Alembic is used to manage schema changes.

Common commands:

```
flask db migrate -m "message"
flask db upgrade
```
Migration scripts live in migrations/versions/ and are committed to version control.


## License
MIT License
