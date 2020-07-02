# from flask import Flask, render_template, request

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def hello():
#     return 'Hello! Welcome to Backend Speaker Recognition'
    

# if __name__ == '__main__':
#     app.run(debug=True,host='0.0.0.0')



from flask import Flask, render_template, request
import mysql.connector
import os
from flask_mysqldb import MySQL
import json
from werkzeug.utils import secure_filename
from flask import Response

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="pageone1Q",
  database="speakerrecognition"
)

mycursor = mydb.cursor()

# mycursor.execute("CREATE TABLE host (host_id INT AUTO_INCREMENT PRIMARY KEY, host_name VARCHAR(255))")

# mycursor.execute("CREATE TABLE user (client_id VARCHAR(255) PRIMARY KEY,userid INT, name VARCHAR(255), is_attending BOOLEAN, is_host BOOLEAN, train_folder VARCHAR(255), test_folder VARCHAR(255) )")

# mycursor.execute("CREATE TABLE host_user (host_user_id  INT AUTO_INCREMENT PRIMARY KEY, host_id INT, client_id VARCHAR(255) , FOREIGN KEY (host_id) REFERENCES host (host_id) ON DELETE CASCADE  ON UPDATE CASCADE, FOREIGN KEY (client_id) REFERENCES user (client_id) ON DELETE CASCADE  ON UPDATE CASCADE)")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pageone1Q'
app.config['MYSQL_DB'] = 'speakerrecognition'

mysql = MySQL(app)


@app.route('/createTeacher', methods=['POST'])
def createTeacher():
  content = request.json
  userid = content['userid']
  print("USERID"+ str(userid))
  name = content['name']
  client_id = str(userid)+'_'+name
  is_attending = False
  is_host = True
  train_folder = 'local/bin/usr/voice_recog/train_folder/'+str(client_id)
  if not os.path.exists(train_folder):
    os.makedirs(train_folder)
  test_folder = 'local/bin/usr/voice_recog/test_folder/'+str(client_id)
  if not os.path.exists(test_folder):
    os.makedirs(test_folder)

  cur = mysql.connection.cursor()
  cur.execute("INSERT INTO user(client_id, userid, name, is_attending, is_host, train_folder, test_folder) VALUES (%s, %s,%s, %s,%s, %s,%s)", (client_id, userid, name, is_attending, is_host, train_folder, test_folder))
  mysql.connection.commit()

  cur.execute( "SELECT * FROM user WHERE client_id = %s", [client_id] )
  user = cur.fetchone()
  cur.close()
  result = json.dumps({"user": user})
  return Response(result, status=201, mimetype='application/json')


@app.route('/createStudent', methods=['POST'])
def createStudent():
  content = request.json
  userid = content['userid']
  print("USERID"+ str(userid))
  name = content['name']
  client_id = str(userid)+'_'+name
  is_attending = False
  is_host = False
  train_folder = 'local/bin/usr/voice_recog/train_folder/'+str(client_id)
  if not os.path.exists(train_folder):
    os.makedirs(train_folder)
  test_folder = 'local/bin/usr/voice_recog/test_folder/'+str(client_id)
  if not os.path.exists(test_folder):
    os.makedirs(test_folder)

  cur = mysql.connection.cursor()
  cur.execute("INSERT INTO user(client_id, userid, name, is_attending, is_host, train_folder, test_folder) VALUES (%s, %s,%s, %s,%s, %s,%s)", (client_id, userid, name, is_attending, is_host, train_folder, test_folder))
  mysql.connection.commit()
  cur.execute( "SELECT * FROM user WHERE client_id = %s", [client_id] )
  user = cur.fetchone()
  print(user)
  cur.close()
  #return 'Successfully create new student!'
  result = json.dumps({"user": user})
  return Response(result, status=201, mimetype='application/json')

@app.route('/studentAttendRoom', methods=['POST'])
def studentAttendRoom():
  content = request.json
  client_id = content['client_id']
  print("client_id"+ str(client_id))
  host_id = content['host_id']
  print("HOSTID"+ str(host_id))

  cur = mysql.connection.cursor()
  cur.execute( "SELECT client_id, host_id  FROM host_user WHERE client_id LIKE %s and host_id LIKE %s", [client_id, host_id] )
  ver = cur.fetchone()
  if ver is not None:
    return Response("User alreadly attend room", status=400, mimetype='application/json')

  cur.execute( "SELECT * FROM host  WHERE  host_id LIKE %s", [ host_id] )
  ver = cur.fetchone()
  if ver is None:
    return Response("Invalid host_id", status=400, mimetype='application/json')

  cur.execute( "SELECT * FROM user  WHERE  client_id LIKE %s", [ client_id] )
  ver = cur.fetchone()
  if ver is None:
    return Response("Invalid client_id", status=400, mimetype='application/json')

  cur.execute("INSERT INTO host_user(host_id, client_id) VALUES (%s,%s)", (host_id, client_id))
  mysql.connection.commit()
  cur.close()
  #return 'Successfully attend room!'
  return Response('Successfully attend room!', status=200, mimetype='application/json')


@app.route('/teacherCreateRoom', methods=['POST'])
def teacherCreateRoom():
  content = request.json
  client_id = request.args.get('client_id')
  
  host_name = content['host_name']
  cur = mysql.connection.cursor()

  cur.execute( "SELECT client_id, is_host  FROM user WHERE client_id LIKE %s", [client_id] )
  ver = cur.fetchone()

  if ver[1] == 1:


    print("CLIENTID"+client_id)
    print("HOSTNAMe"+ host_name)
    #cur.execute("INSERT INTO host(host_id, host_name) VALUES (%s,%s)", (NULL, host_name))
    cur.execute("insert into host(host_name) values(%s)", [host_name])

    mysql.connection.commit()
    host_id = cur.lastrowid
    cur.execute("INSERT INTO host_user(host_id, client_id) VALUES (%s,%s)", (host_id, client_id))
    mysql.connection.commit()
    cur.execute( "SELECT * FROM host WHERE host_id = %s", [host_id] )
    host = cur.fetchone()
    cur.close()
    #return 'Successfully create new room!'
    #return Response(host, status=201, mimetype='application/json')
    result = json.dumps({"host": host})
    return Response(result, status=201, mimetype='application/json')
  
  #return "Just teacher can create new room!"
  return Response("Just teacher can create new room!", status=400, mimetype='application/json')


@app.route('/userInRoom', methods=['GET'])
def userInRoom():
  host_id = request.args.get('host_id')
  cur = mysql.connection.cursor()

  cur.execute( "SELECT client_id FROM host_user WHERE host_id = %s", [host_id] )
  data = cur.fetchall()
  user_list = []
  for row in data:
    cur.execute( "SELECT * FROM user WHERE client_id = %s AND is_attending = 1", [row[0]] )
    user = cur.fetchone()
    if user is not None:
      user_list.append(user)
  #result = json.dumps(user_list)
  result = json.dumps({"list_user": user_list})
  return Response(result, status=200, mimetype='application/json')


@app.route('/userOfRoom', methods=['GET'])
def userOfRoom():
  host_id = request.args.get('host_id')
  cur = mysql.connection.cursor()

  cur.execute( "SELECT client_id FROM host_user WHERE host_id = %s", [host_id] )
  data = cur.fetchall()
  user_list = []
  for row in data:
    cur.execute( "SELECT * FROM user WHERE client_id = %s", [row[0]] )
    user = cur.fetchone()
    if user is not None:
      user_list.append(user)
  result = json.dumps({"list_user": user_list})
  return Response(result, status=200, mimetype='application/json')


@app.route('/uploadTrainFile', methods = [ 'POST'])
def upload_train_file():
  client_id = request.args.get('client_id')
  cur = mysql.connection.cursor()
  cur.execute( "SELECT train_folder FROM user WHERE client_id = %s", [client_id] )
  user = cur.fetchone()
  trainFolder = user[0]
  f = request.files['trainfile']
  f.save(os.path.join(trainFolder, secure_filename(f.filename)))
  
  #return 'file uploaded successfully'
  return Response('file uploaded successfully', status=201, mimetype='application/json')


@app.route('/uploadTestFile', methods = [ 'POST'])
def upload_test_file():
  client_id = request.args.get('client_id')
  cur = mysql.connection.cursor()
  cur.execute( "SELECT test_folder FROM user WHERE client_id = %s", [client_id] )
  user = cur.fetchone()
  testFolder = user[0]
  f = request.files['testfile']
  f.save(os.path.join(testFolder, secure_filename(f.filename)))
  
  return Response('file uploaded successfully', status=201, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')