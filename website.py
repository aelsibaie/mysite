from flask import Flask, render_template, request, make_response
app = Flask(__name__, static_url_path='/static')


from datetime import datetime
from os import urandom


import sqlite_db
        

@app.route('/')
def index():
    time = datetime.now()
    time = time.strftime("%c") # Locale’s appropriate date and time representation
    return render_template('index.html', time=time)

@app.route('/auth')
def auth():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    if sqlite_db.check_session(username, id) == True:
        return "Authenticated"
    else:
        return "Denied access"

@app.route('/login', methods=['POST'])
def login():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    
    login_request = sqlite_db.login(username, password)
    
    if type(login_request) != str:
        resp = make_response("Log in successful")
        resp.set_cookie('username', username)
        resp.set_cookie('id', login_request)
        return resp
        #return "Log in successful"
    else:
        return login_request


@app.route('/register', methods=['POST'])
def register():
    post_data = request.form
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert plaintext to bytes
    email = post_data['email']
    problems = sqlite_db.register(username, email, password)
    if problems == []:
        return "Registration successful"
    else:
        return str(problems)

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    print("Closing SQLite connection")
    sqlite_db.connection.close