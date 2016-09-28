from flask import Flask, render_template, request
app = Flask(__name__, static_url_path='/static')


from datetime import datetime
from os import urandom


import sqlite_db
        

@app.route('/')
def index():
    time = datetime.now()
    time = time.strftime("%c") # Locale’s appropriate date and time representation
    return render_template('index.html', time=time)


@app.route('/login', methods=['POST'])
def login():
    post_data = request.form
    
    username = post_data['username']
    password = str.encode(post_data['password']) # Convert to bytes
    
    user = sqlite_db.User(username=username, password=password)
    login_attempt = user.login()
    
    
    yep = "hello"
    return yep


@app.route('/register', methods=['POST'])
def register():
    post_data = request.form
    
    salt = urandom(16)
    username = post_data['username']
    password = post_data['password']
    password = str.encode(password) # Convert to bytes
    email = post_data['email']
 
    
    user = sqlite_db.User(username, email=email, salt=salt, password=password)
    user.register()
    
    
    yep = "hello"
    return yep

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
