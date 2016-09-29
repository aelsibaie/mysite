from flask import Flask, render_template, request, make_response, redirect
app = Flask(__name__, static_url_path='/static')

# Change this and keep it secret
# app.secret_key = 'vzHUWR5FZnwMG8wBzFgCGJRTqButzArqFtUbQ5vLsUV5bBf3'

import sqlite_db

from datetime import datetime


def check_auth():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    auth = sqlite_db.check_session(username, id)
    if auth == "ADMIN":
        return {"username":username, "rank":auth}
    elif auth == "AUTH":
        return {"username":username, "rank":auth}
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
    auth = check_auth()
    if auth != False:
        if auth['rank'] == "ADMIN":
            admin_data = sqlite_db.get_users()
    else:
        admin_data = None

    return render_template('admin.html', auth=auth, admin_data=admin_data)


@app.route('/logoff', methods=['POST'])
def logoff():
    auth = check_auth()
    if auth != False:
        sqlite_db.logoff(auth['username'])
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    login_request = sqlite_db.login(username, password)
    if login_request != False:
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