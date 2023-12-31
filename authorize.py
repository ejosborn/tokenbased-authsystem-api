import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sqlite3

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config["JWT_SECRET_KEY"] = os.getenv('SECRET_KEY')
jwt = JWTManager(app)

# creating database file
connect = sqlite3.connect('users.db')
cursor = connect.cursor()

# creating users table
cursor.execute(
    ''' CREATE TABLE IF NOT EXISTS users 
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
    )'''
)

connect.commit()
connect.close()

# api endpoint for registering users
@app.route("/register", methods=["POST"])
def register():
    info = request.get_json()
    username = info.get('username')
    password = info.get('password')

    #check if exists in user table
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    exists = cursor.fetchone()
    conn.close()

    #if username exists
    if exists:
        return jsonify({'error': 'Username is already taken. Choose a unique username.'}), 400
    
    #create user
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (? , ?)', (username, password))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User Registration Successful!'}), 201


# api endpoint for logging users in
@app.route("/login", methods=["POST"])
def login():
    info = request.get_json()
    username = info.get('username')
    password = info.get('password')

    #check user and password vs database data
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    userExists = cursor.fetchone()

    #creates valid jwt if user exists, else return error
    if userExists:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': ' Invalid username or password'}), 401

# api endpoint making sure requests have valid JWT Web Tokens
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in=current_user), 200


if __name__ == "__main__":
    app.run(debug=True)