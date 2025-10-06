#!/usr/bin/env python3


import sqlite3
import hashlib
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# DB initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Insert some test data
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('admin', 'admin123', 'admin@example.com', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('user1', 'password123', 'user1@example.com', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (username, password, email, role) VALUES ('test', 'test123', 'test@example.com', 'user')")
    
    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({"message": "Login successful", "user": user[1]})
        else:
            return jsonify({"message": "Invalid credentials"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/search', methods=['GET'])
def search_users():
    search_term = request.args.get('q', '')
    
    query = "SELECT * FROM users WHERE username LIKE '%{}%' OR email LIKE '%{}%'".format(search_term, search_term)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({"results": results})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')
    
    query = f"DELETE FROM users WHERE id = {user_id}"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        
        return jsonify({"message": "User deleted successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form.get('user_id')
    new_email = request.form.get('email')
    
    query = f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        
        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/get_user_details', methods=['GET'])
def get_user_details():
    username = request.args.get('username')
    include_admin = request.args.get('include_admin', 'false')
    
    if include_admin.lower() == 'true':
        query = f"SELECT * FROM users WHERE username = '{username}' OR role = 'admin'"
    else:
        query = f"SELECT * FROM users WHERE username = '{username}' AND role != 'admin'"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({"users": results})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    user_id = request.args.get('id')
    
    query = f"SELECT username, email FROM users WHERE id = {user_id}"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return jsonify({"username": result[0], "email": result[1]})
        else:
            return jsonify({"message": "User not found"})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

@app.route('/list_users', methods=['GET'])
def list_users():
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'ASC')
    
    query = f"SELECT * FROM users ORDER BY {sort_by} {order}"
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({"users": results})
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})

# Simple HTML interface for testing
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My App</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .form-group { margin: 10px 0; }
            input, button { padding: 8px; margin: 5px; }
        </style>
    </head>
    <body>

    </body>
    </html>
    '''

if __name__ == '__main__':
    init_db()

    print("🔍 Available endpoints:")
    print("   - GET  / (HTML interface)")
    print("   - POST /login")
    print("   - GET  /search")
    print("   - POST /delete_user")
    print("   - POST /update_user")
    print("   - GET  /get_user_details")
    print("   - GET  /get_user_info")
    print("   - GET  /list_users")
    app.run(debug=True, host='0.0.0.0', port=5000)
