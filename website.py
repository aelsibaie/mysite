from flask import Flask, render_template, request, make_response, redirect, session
import sqlite_db
from datetime import datetime, timedelta
import time
from decimal import Decimal
import requests


app = Flask(__name__, static_url_path='/static')

# Change this and keep it secret
app.secret_key = 'vzHUWR5FZnwMG8wBzFgCGJRTqButzArqFtUbQ5vLsUV5bBf3'
recaptcha_secret_key = '6LfoZgkUAAAAAI8gnK6Ii3Pz_vln87HkhI77OS-B'


def universal_content(content, start):
    # Get website title
    content['title'] = "Welcome to Amir's Experimental Website"
    # Get server time
    current_time = datetime.now()
    current_time = time.strftime("%c")
    content['time'] = current_time
    # Process render time
    end = time.clock()
    render_time = Decimal.from_float(end - start)
    if render_time <  0.0001:
        render_time = "< 0.10 ms"
    else:
        render_time = str("{0:.2f}".format((render_time * 1000))) + " ms"
    content['render_time'] = render_time
    return content

@app.route('/')
def index():
    render_start = time.clock()
    content = {}
    # Check if there are any users in the DB
    content['num_users'] = sqlite_db.get_num_users()
    auth = check_auth(request)
    if auth != False:
        auth_data = None
    else:
        auth_data = None

    content = universal_content(content, render_start)

    return render_template('index.html', content=content, auth=auth, auth_data=auth_data)


@app.route('/admin')
def admin():
    render_start = time.clock()
    content = {}
    auth = check_auth(request)
    if auth != False:
        if auth['rank'] == "ADMIN":
            admin_data = {}
            admin_data["users"] = sqlite_db.get_users()
    else:
        admin_data = None
    content = universal_content(content, render_start)
    return render_template('admin.html', content=content, auth=auth, admin_data=admin_data)


@app.route('/logoff', methods=['POST'])
def logoff():
    auth = check_auth(request)
    if auth != False:
        session.clear()
        sqlite_db.logoff(auth['username'])
        return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    session_id = sqlite_db.login(username, password)
    if session_id != False:
        session['username'] = username
        session['id'] = session_id
        if 'remember' in post_data:
            session.permanent = True
        return redirect('/')
    else:
        return render_template('error.html', problems=["Username of password incorrect"])


@app.route('/register', methods=['POST'])
def register():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    email = post_data['email']
    #handle reCAPTCHA verification
    g_recaptcha_response = post_data['g-recaptcha-response']
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data = {'secret':recaptcha_secret_key, 'response':g_recaptcha_response}).json()
    if response['success'] == False:
        return render_template('error.html', problems=["reCAPTCHA error"])
    problems = sqlite_db.register(username, email, password)
    if problems == []:
        return render_template('registered.html', username=username, email=email)
    else:
        return render_template('error.html', problems=problems)


@app.route('/submit_blog', methods=['POST'])
def submit_blog():
    auth = check_auth(request)
    if auth != False:
        if auth['rank'] == "ADMIN":
            blog_data = request.form['blog_data']
    return redirect('/')


def check_auth(request):
    if 'username' in session:
        username = session['username']
        id = session['id']
        ip = request.environ['REMOTE_ADDR']
    else:
        return False
    auth = sqlite_db.check_id(username, id, ip)
    if auth == "ADMIN":
        return {"username":username, "rank":auth}
    elif auth == "AUTH":
        return {"username":username, "rank":auth}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    sqlite_db.connection.close
