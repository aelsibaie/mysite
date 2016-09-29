from flask import Flask, render_template, request, make_response, redirect
app = Flask(__name__, static_url_path='/static')

import sqlite_db

from datetime import datetime
from os import urandom


def check_auth():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    if sqlite_db.check_session(username, id) == True:
        return username
    else:
        return False

def check_admin():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    if sqlite_db.check_admin_db(username, id) == True:
        return username
    else:
        return False

@app.route('/')
def index():
    auth = check_auth()
    if auth != False:
        auth_data = sqlite_db.get_users()
    else:
        auth_data = None
    time = datetime.now()
    time = time.strftime("%c") # Locale’s appropriate date and time representation
    return render_template('index.html', time=time, auth=auth, auth_data=auth_data)


@app.route('/admin')
def admin():
    admin = check_admin()
    if admin != False:
        admin_data = sqlite_db.get_users()
    else:
        admin_data = None

    return render_template('admin.html', admin=admin, admin_data=admin_data)


@app.route('/logoff', methods=['POST'])
def logoff():
    username = request.cookies.get('username')
    auth = check_auth()
    if auth != False:
        sqlite_db.logoff(username)
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    
    login_request = sqlite_db.login(username, password)
    
    if login_request != False:
        print(login_request)
        #resp = index()
        resp = make_response(redirect('/'))
        resp.set_cookie('username', username)
        resp.set_cookie('id', login_request)
        return resp
    else:
        return render_template('error.html', problems=["Username of password incorrect"])


@app.route('/register', methods=['POST'])
def register():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    email = post_data['email']
    problems = sqlite_db.register(username, email, password)
    if problems == []:
        return render_template('registered.html', username=username, email=email)
    else:
        return render_template('error.html', problems=problems)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    print("Closing SQLite connection")
    sqlite_db.connection.close