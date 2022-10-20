
from flask import Flask, jsonify, request, render_template, url_for, redirect
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from dotenv import dotenv_values
import mysql.connector
import os
load_dotenv()
config = dotenv_values(".env")
# print(config['DATABASE'])

mydb = mysql.connector.connect(
    host="mysql",
    user="root",
    password="admin",
    port="3306",
    database='flask_mysql'
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

list_db = []
for x in mycursor:
    list_db.append(''.join(x))

if config['DATABASE'] not in list_db:
    print(config['DATABASE'])
    createddb = 'CREATE DATABASE ' + config['DATABASE']
    mycursor.execute(createddb)
else:
    print("Connected to database " + config['DATABASE'])


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title="Home Page")


@app.route('/image')
def image():
    return render_template('image.html', title="Image Page")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload',  methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            config['PATH'], filename))
        return redirect(url_for('index'))


@app.route("/api/v1/todos", methods=['POST'])
def create_todo():
    req = request.json
    sql = "INSERT INTO todos (title, des) VALUES (%s, %s)"
    val = (req["title"], req["des"])
    mycursor.execute(sql, val)
    mydb.commit()
    if mycursor.rowcount == 1:
        return jsonify({
            "status": 200,
            "message": "Inserted successfully"
        })
    else:
        return jsonify({
            "status": 400,
            "message": "Inserted failed"
        })


@app.route("/api/v1/todos", methods=['GET'])
def get_all_todo():
    mycursor.execute("SELECT * FROM todos")
    myresult = mycursor.fetchall()
    rs = []
    for x in myresult:
        rs.append(
            {'id': x[0], 'title': x[1], 'des': x[2], 'completed': "false" if x[3] == 0 else 'true'})
    return jsonify({
        "status": 200,
        "data": rs
    })


@app.route("/api/v1/todos/<string:id>", methods=['GET'])
def get_todo_by_id(id):
    sql = "SELECT * FROM todos WHERE id = %s"
    query = (id, )
    mycursor.execute(sql, query)
    myresult = mycursor.fetchall()
    if myresult:
        rs = {"id": myresult[0][0], "title": myresult[0][1],
              "des": myresult[0][2], 'completed': "false" if myresult[0][3] == 0 else 'true'}
        return jsonify({
            "status": 200,
            "data": rs
        })
    else:
        return jsonify({
            "status": 404,
            "message": "Todo not found"
        })


@app.route("/api/v1/todos/<string:id>", methods=['DELETE'])
def delete_todo_by_id(id):
    sql = "SELECT * FROM todos WHERE id = %s"
    query = (id, )
    mycursor.execute(sql, query)
    myresult = mycursor.fetchall()
    if myresult:
        sql = "DELETE FROM todos WHERE id = %s"
        mycursor.execute(sql, query)
        mydb.commit()
        if mycursor.rowcount == 1:
            return jsonify({
                "status": 200,
                "message": "Deleted successfully"
            })
        else:
            return jsonify({
                "status": 400,
                "message": "Deleted failed"
            })
    else:
        return jsonify({
            "status": 404,
            "message": "Todo not found"
        })


@app.route("/api/v1/todos/<string:id>", methods=['PUT'])
def update_todo_by_id(id):
    req = request.json
    sql = "SELECT * FROM todos WHERE id = %s"
    query = (id, )
    mycursor.execute(sql, query)
    myresult = mycursor.fetchall()
    if myresult:
        sql = "UPDATE todos SET title = %s, des = %s, completed = %s WHERE id = %s"
        val = (req["title"], req["des"], req["completed"], id)
        mycursor.execute(sql, val)
        mydb.commit()
        if mycursor.rowcount == 1:
            return jsonify({
                "status": 200,
                "message": "Updated successfully"
            })
        else:
            return jsonify({
                "status": 400,
                "message": "Updated failed"
            })
    else:
        return jsonify({
            "status": 404,
            "message": "Todo not found"
        })


if __name__ == "__main__":
    app.run(debug=True)
