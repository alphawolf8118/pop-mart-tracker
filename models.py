from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # e.g., "Fight for the Golden Spatula Chibi Series Figures II"
    cover_image_url = db.Column(db.String(500))  # New field for collection poster/cover
    price_per_box = db.Column(db.Float, default=19.99)  # New: default $19.99

class Figurine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Chibi Sweetheart Xayah"
    image_url = db.Column(db.String(500))  # URL to image
    owned_count = db.Column(db.Integer, default=0)  # For duplicates: how many you have
    collected = db.Column(db.Boolean, default=False)  # If you have at least one