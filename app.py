from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
import uuid
from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

# Database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Bhary123$$@localhost/Users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    account_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return username

@app.route('/v1/user', methods=['POST'])
def create_user():
    data = request.json
    username = data['username']
    if User.query.filter_by(username=username).first():
        return make_response(jsonify({"error": "User already exists"}), 400)
    
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        id=str(uuid.uuid4()),
        first_name=data['first_name'],
        last_name=data['last_name'],
        username=username,
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "account_created": user.account_created.isoformat() + 'Z',
        "account_updated": user.account_updated.isoformat() + 'Z'
    }), 201


@app.route('/v1/user/self', methods=['PUT'])
@auth.login_required
def update_user():
    data = request.json
    username = auth.current_user()
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    else:
        return make_response(jsonify({"error": "Bad Request. Missing required fields."}), 400)

    user.account_updated = datetime.utcnow()
    db.session.commit()
    
    return '', 204


@app.route('/v1/user/self', methods=['GET'])
@auth.login_required
def get_user():
    username = auth.current_user()
    user = User.query.filter_by(username=username).first()
    
    if user:
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "account_created": user.account_created.isoformat() + 'Z',
            "account_updated": user.account_updated.isoformat() + 'Z'
        }
        return jsonify(user_data), 200
    else:
        return make_response(jsonify({"error": "User not found"}), 404)

# Public: Operations available to all users without authentication 
@app.route('/healthz', methods=['GET'])
def health_end_point():
    # check if payload (payload not allowed)
    if request.args:
        return make_response('', 405)

    if request.get_data():
        return make_response('', 400, {'Cache-Control': 'no-cache'})

    try:
        # db.session.connection().ping()
        return make_response('', 200, {'Cache-Control': 'no-cache'})

    except Exception as e:
        return make_response('', 503, {'Cache-Control': 'no-cache'})
   
@app.route('/healthz', methods=['POST'])   
def health_post_end_point():
    return make_response('', 405)

@app.route('/healthz', methods=['PUT'])   
def health_put_end_point():
    return make_response('', 405)

@app.route('/healthz', methods=['DELETE'])   
def health_delete_end_point():
    return make_response('', 405)

@app.route('/healthz', methods=['HEAD'])   
def health_head_end_point():
    return make_response('', 405)

@app.route('/healthz', methods=['OPTIONS'])   
def health_options_end_point():
    return make_response('', 405)

if __name__ == '__main__':
    app.run(port= 8080, debug=True)
