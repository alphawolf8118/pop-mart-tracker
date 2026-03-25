from flask import Flask, render_template, request, redirect, url_for
from models import db, Collection, Figurine
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload config
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'collections')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    collections = Collection.query.order_by(Collection.title.asc()).all()
    
    collection_stats = []
    for coll in collections:
        total_figurines = Figurine.query.filter_by(collection_id=coll.id).count()
        
        # Count how many unique figurines you have at least one of (collected = True)
        unique_collected = Figurine.query.filter_by(
            collection_id=coll.id,
            collected=True
        ).count()
        
        collection_stats.append({
            'collection': coll,
            'total_figurines': total_figurines,
            'unique_collected': unique_collected
        })
    
    return render_template('index.html', collection_stats=collection_stats)

@app.route('/collection/<int:coll_id>')
def view_collection(coll_id):
    collection = Collection.query.get_or_404(coll_id)
    figurines = Figurine.query.filter_by(collection_id=coll_id).all()
    return render_template('collection.html', collection=collection, figurines=figurines)

@app.route('/add_collection', methods=['GET', 'POST'])
def add_collection():
    if request.method == 'POST':
        title = request.form['title']
        price_per_box = float(request.form.get('price_per_box', 19.99))
        cover_image_url = request.form.get('cover_image_url', '').strip()
        
        # Check for uploaded file first (priority)
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cover_image_url = f"/static/uploads/collections/{filename}"
        
        # If no upload and URL is provided, use the URL
        elif not cover_image_url:
            cover_image_url = ''  # None provided
        
        collection = Collection(title=title, cover_image_url=cover_image_url, price_per_box=price_per_box)
        db.session.add(collection)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_collection.html')

@app.route('/edit_collection/<int:coll_id>', methods=['GET', 'POST'])
def edit_collection(coll_id):
    collection = Collection.query.get_or_404(coll_id)
    if request.method == 'POST':
        collection.title = request.form['title']
        collection.price_per_box = float(request.form.get('price_per_box', 19.99))
        
        new_url = request.form.get('cover_image_url', '').strip()
        
        # Priority: uploaded file
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                collection.cover_image_url = f"/static/uploads/collections/{filename}"
            elif new_url:
                collection.cover_image_url = new_url
            # else: keep existing
        elif new_url:
            collection.cover_image_url = new_url
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit_collection.html', collection=collection)

@app.route('/delete_collection/<int:coll_id>', methods=['GET', 'POST'])
def delete_collection(coll_id):
    collection = Collection.query.get_or_404(coll_id)
    
    if request.method == 'POST':
        # Delete all figurines first
        Figurine.query.filter_by(collection_id=coll_id).delete()
        db.session.delete(collection)
        db.session.commit()
        return redirect(url_for('index'))
    
    # GET: show confirmation
    return render_template('delete_collection.html', collection=collection)

@app.route('/add_figurine/<int:coll_id>', methods=['POST'])
def add_figurine(coll_id):
    name = request.form['name']
    image_url = request.form['image_url']
    figurine = Figurine(collection_id=coll_id, name=name, image_url=image_url)
    db.session.add(figurine)
    db.session.commit()
    return redirect(url_for('view_collection', coll_id=coll_id))

@app.route('/toggle/<int:fig_id>')
def toggle(fig_id):
    fig = Figurine.query.get_or_404(fig_id)
    fig.owned_count += 1
    if fig.owned_count >= 1:
        fig.collected = True
    db.session.commit()
    return redirect(url_for('view_collection', coll_id=fig.collection_id))

@app.route('/remove_duplicate/<int:fig_id>')
def remove_duplicate(fig_id):
    fig = Figurine.query.get_or_404(fig_id)
    if fig.owned_count > 0:
        fig.owned_count -= 1
        if fig.owned_count == 0:
            fig.collected = False
    db.session.commit()
    return redirect(url_for('view_collection', coll_id=fig.collection_id))

@app.route('/edit_figurine/<int:fig_id>', methods=['GET', 'POST'])
def edit_figurine(fig_id):
    fig = Figurine.query.get_or_404(fig_id)
    if request.method == 'POST':
        fig.name = request.form['name']
        fig.image_url = request.form['image_url']
        db.session.commit()
        return redirect(url_for('view_collection', coll_id=fig.collection_id))
    
    return render_template('edit_figurine.html', fig=fig, collection_id=fig.collection_id)

@app.route('/delete_figurine/<int:fig_id>', methods=['GET', 'POST'])
def delete_figurine(fig_id):
    fig = Figurine.query.get_or_404(fig_id)
    collection_id = fig.collection_id
    
    if request.method == 'POST':
        db.session.delete(fig)
        db.session.commit()
        return redirect(url_for('view_collection', coll_id=collection_id))
    
    # GET request: show confirmation page
    return render_template('delete_figurine.html', fig=fig, collection_id=collection_id)

if __name__ == '__main__':
    app.run(debug=True, port=5003)