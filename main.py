from flask import Flask, request, make_response, jsonify
from db import db

app = Flask(__name__)

@app.route("/" , methods = ['GET'])
def text():
    return "class-18-assignment-2" 

@app.route("/signup" , methods = ['POST'])
def signup():   
    db_conn = db.mysqlconnect()
    data = request.get_json()
    cur = db_conn.cursor()
    name = data['name']
    email = data ['email']
    password = data ['password']
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", tuple(name, email, password))
    db_conn.commit()
    db.disconnect(db_conn)
    return "user created successfully"


@app.route("/login", methods = ["POST"])
def login():
    db_conn = db.mysqlconnect()
    data = request.get_json()
        
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = %s AND password = %s", tuple(data['name'], data['password']))
    user = cur.fetchone()    
     
    if user:
        res = make_response('user logged in!')
        res.set_cookie(
                'user_id',
                str(user['id']),   
                httponly=True,  
                max_age=172800,       
                path='/',            
                samesite='Lax' 
            )
        db_conn.commit()
        db.disconnect(db_conn)
        return res
    else:
        return "Invalid login details"
    
    
@app.route("/notes", methods = ['POST'])
def create_notes():
    db_conn = db.mysqlconnect()
    data = request.get_json()

    user_id = request.cookies.get('user_id')
    if user_id:
        cur = db_conn.cursor()
        cat_id = data.get('cat_id')
        cur.execute("INSERT INTO notes (user_id, title, content, cat_id) VALUES (%s, %s, %s, %s)", tuple(user_id, data['title'], data['content'], cat_id))
        db_conn.commit()
        db.disconnect(db_conn)
        return "notes created successfully"
    else:
        return "please login first"
    
    
@app.route("/notes/<int:id>", methods = ['PUT'])
def update_notes(id):
    db_conn = db.mysqlconnect()
    data = request.get_json()
    
    user_id = request.cookies.get('user_id')
    if user_id:
        cur = db_conn.cursor()
        cur.execute("SELECT * FROM notes WHERE id = %s AND user_id = %s", tuple(id, user_id))
        note = cur.fetchone()
        if note: 
            cur = db_conn.cursor()
            cat_id = data.get('cat_id')
            cur.execute("UPDATE notes SET title = %s, content = %s, cat_id = %s WHERE id = %s AND user_id = %s", tuple(data['title'], data['content'], cat_id, id, user_id))
            db_conn.commit()
            db.disconnect(db_conn)
            return "notes updated successfully"
    else:
        return "please login first"

@app.route("/notes/<int:id>", methods = ['DELETE'])
def delete_notes(id):
    db_conn = db.mysqlconnect()
    user_id = request.cookies.get('user_id')
    if user_id:
        cur = db_conn.cursor()
        cur.execute("SELECT * FROM notes WHERE id = %s AND user_id = %s", tuple(id, user_id))
        note = cur.fetchone()
        if note: 
            cur = db_conn.cursor()
            cur.execute("DELETE FROM notes WHERE id = %s", tuple(id))
            db_conn.commit()
            db.disconnect(db_conn)
            return "notes deleted successfully"
    return "please login first"
    
@app.route("/categories", methods =['POST'])
def create_category():
    db_conn = db.mysqlconnect()
    data = request.get_json() 
    
    cur = db_conn.cursor()
    name = data['name']
    user_id = data ['user_id']
    cur.execute("INSERT INTO categories (name, user_id) VALUES (%s, %s)", tuple(name, user_id))
    db_conn.commit()
    db.disconnect(db_conn)
    return "category created successfully"

    
@app.route("/notes/<int:id>", methods=['PUT'])
def assign_category(id):
    db_conn = db.mysqlconnect()
    data = request.get_json()

    user_id = request.cookies.get('user_id')
    if user_id:
        cur = db_conn.cursor()
        cat_id = data.get('cat_id')

        cur.execute("SELECT * FROM categories WHERE id = %s", tuple(cat_id))
        if not cur.fetchone():
            db.disconnect(db_conn)
            return "category does not exist"

        cur.execute("SELECT * FROM notes WHERE id = %s AND user_id = %s", tuple(id, user_id))
        if not cur.fetchone():
            db.disconnect(db_conn)
            return "Note does not exist or these are not your notes", 

        cur.execute("INSERT INTO notes (id, cat_id) VALUES (%s, %s)", tuple(id, cat_id))
        db_conn.commit()
        db.disconnect(db_conn)
        return "category assigned successfully"
    else:
        return "please login first"
    
@app.route("/notes", methods=['GET'])
def filter_notes():
    db_conn = db.mysqlconnect()
    user_id = request.cookies.get('user_id')

    if user_id:
        query = "SELECT * FROM notes WHERE 1=1"
        condition = []

        title = request.args.get('title')
        category_id = request.args.get('category_id')
        date_created = request.args.get('date_created')
        
        query += " AND user_id = %s"
        condition.append(user_id)

        if title:
            query += " AND title = %s"
            condition.append(title)

        if category_id:
            query += " AND cat_id = %s"
            condition.append(category_id)

        if date_created:
            query += " AND DATE(created_at) = %s"
            condition.append(date_created)
            
        cur = db_conn.cursor()
        cur.execute(query, tuple(condition))
        notes = cur.fetchall()

        db.disconnect(db_conn)
        return jsonify(notes) # for readable format
    else:
        return "Please login first"


@app.route("/notes/<int:id>", methods=['GET'])
def display_notes(id):
    db_conn = db.mysqlconnect()
    user_id = request.cookies.get('user_id')

    if user_id:
        query = "SELECT * FROM notes WHERE user_id = %s and id = %s"
        cur = db_conn.cursor()
        cur.execute(query, tuple(user_id, id))
        notes = cur.fetchall()

        db.disconnect(db_conn)
        if notes:
            return jsonify(notes) 
        else:
            return "Note not found or you do not have permission to access this note"
        
    else:
        return "Please login first"

app.run(debug=True, port=3000)