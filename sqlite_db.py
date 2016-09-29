import time
import email

import hashlib
import base64
import os

import sqlite3
connection = sqlite3.connect('users.sqlite3', check_same_thread = False)
cursor = connection.cursor()

# First, let's create the DB if it doesn't exist
cursor.execute('''CREATE TABLE if not exists users (
    username        TEXT        PRIMARY KEY,
    email           TEXT,
    salt            BLOB,
    key             BLOB,
    session_id      BLOB,
    creationtime    DATETIME,
    logintime       DATETIME,
    admin           BOOLEAN,
    validated       BOOLEAN)''')

def check_session(username, id):
    cursor.execute("SELECT session_id FROM users WHERE username = ?", (username,))
    db_id = cursor.fetchone()[0]
    print(base64.b64decode(id))
    print(base64.b64decode(db_id))
    if base64.b64decode(id) == base64.b64decode(db_id[0]):
        return True
    return False
    

def __validate_input(username, user_email, password):
    problems = []
    temp_email = email.utils.parseaddr(user_email)
    if temp_email == ('', ''):
        problems.append("Invalid email address")
    if len(password) > 100:
        problems.append("Password must be less than 100 characters")
    if len(password) < 8:
        problems.append("Password must be greater than 8 characters")
    if len(username) > 30:
        problems.append("Username must be less than 30 characters")
    if len(username) < 4:
        problems.append("Username must be greater than 4 characters")
    return problems

def register(username, user_email, password):
    problems = __validate_input(username, user_email, password)
    if problems != []:
        return problems
    salt = os.urandom(16) # Salt should be about 16 or more bytes
    key = __get_key(password, salt)
    creationtime = time.time()
    try:
        cursor.execute("INSERT INTO users (username,email,salt,key,creationtime,admin,validated) VALUES (?,?,?,?,?,?,?)", (
            username,
            user_email,
            salt,
            key,
            creationtime,
            False,
            False)
        )
        connection.commit()
    except sqlite3.IntegrityError as error:
        problems.append("Username already taken")
    return problems
        
def login(username, password):
    try:
        cursor.execute("SELECT salt, key FROM users WHERE username = ?", (username,))
        salt, db_key = cursor.fetchone() 
        user_key = __get_key(password, salt)
        if db_key == user_key:
            logintime = time.time()
            session_id = base64.b64encode(os.urandom(64))
            cursor.execute("UPDATE users SET logintime = ?, session_id = ?  WHERE username = ?", (logintime,session_id,username))
            connection.commit()
            return session_id
        else:
            return "Incorrect password"
    except TypeError as error:
        return "User not found"

def __get_key(password, salt):
    # As of 2013, at least 100,000 iterations of SHA-256 are suggested
    key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    return key
