from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo, MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from urllib.parse import urlparse, parse_qs, quote
from datetime import datetime

app = Flask(__name__)

# Use environment variables for sensitive configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/PolicyKYC')
app.config['UPLOAD_FOLDER'] = './static/uploads/'

# Initialize PyMongo
mongo = PyMongo(app)

# MongoDB collections
users_collection = mongo.db.users
sales_collection = mongo.db.sales
bids_collection = mongo.db.bids


@app.route('/')
def index():
    return render_template('login.html')



# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({'username': username})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_type'] = user['user_type']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('login.html') 

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']  #
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        if user_type == 'agent':
            kyc_details = request.form['kyc_details']  # Capturing KYC for agents
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'user_type': user_type,
                'kyc_details': kyc_details
            })
        else:
            users_collection.insert_one({
                'username': username,
                'password': hashed_password,
                'user_type': user_type
            })
        
        return redirect(url_for('login'))
    
    return render_template('register.html')


#Dashboard Route
@app.route('/dashboard')
def dashboard():
     if 'user_id' not in session:
         return redirect(url_for('login'))
    
     user_type = session.get('user_type')  # Retrieve the user type from the session
     user_id = session.get('user_id')  # Retrieve user_id from session

     if user_type == 'retailer':
         return render_template('retailers_dashboard.html',user_id=user_id, user_type=user_type)
     elif user_type == 'agent':
         return render_template('agents_dashboard.html',user_id=user_id, user_type=user_type)
     else:
         return redirect(url_for('login'))  # Redirect to login if user type is invalid


# retailer Dashboard - Post sale Article
@app.route('/retailer_post_article', methods=['GET', 'POST'])
def retailer_post_article():
    if 'user_id' not in session or session['user_type'] != 'retailer':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        fryp_price = float(request.form['fryp_price'])
        sale_DateTime = request.form['sale_date_time']  
        # Handle image upload
        image = request.files['image']
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
 
        # Ensure the upload folder exists
        #os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        try:
            image.save(image_path)
        except Exception as e:
            return jsonify({"file not saved ***": str(e)}), 500
        
            # Insert article into sales collection
        sales_collection.insert_one({
            'title': title,
            'description': description,
            'fryp_price': fryp_price,
            'sale_DateTime': sale_DateTime,
            'image_path': image_path,
            'retailer_id': session['user_id'],
            'bids': []  # Empty list of bids initially
        })
        
        return redirect(url_for('dashboard'))
    
    return render_template('retailers_dashboard.html')






@app.route('/logout', methods=['POST'])
def logout():
    # Clear session or handle logout logic
    session.clear()
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True, port=5001)
    #app.run(host='0.0.0.0', debug=True)
