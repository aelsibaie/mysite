import time
import email

import hashlib
import base64
import os

import sqlite3
connection = sqlite3.connect('db.sqlite3', check_same_thread = False)
cursor = connection.cursor()

# First, let's create the DB if it doesn't exist
cursor.execute('''CREATE TABLE if not exists users (
    username        TEXT        PRIMARY KEY,
    email           TEXT,
    salt            BLOB,
    key             BLOB,
    session_id      TEXT,
    creationtime    DATETIME,
    logintime       DATETIME,
    admin           BOOLEAN,
    validated       BOOLEAN)''')

cursor.execute('''CREATE TABLE if not exists blogs (
    blog_id         INTEGER     PRIMARY KEY,
    author          TEXT,
    content         TEXT,
    creationtime    DATETIME)''')

def check_session(username, id):
    cursor.execute("SELECT session_id, admin FROM users WHERE username = ?", (username,))
    try:
        db_id, admin = cursor.fetchone()
        if db_id == None:
            return False
        elif db_id == id:
            if admin == True:
                return "ADMIN"
            else:
                return "AUTH"
        else:
            return False # Bad user ID
    except TypeError:
        return False # Username not found

def get_users():
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    users_clean = []
    for dirty_user in users:
        users_clean.append(dirty_user[0])
    return users_clean

def logoff(username):
    cursor.execute("UPDATE users SET session_id = NULL WHERE username = ?", (username,))
    connection.commit()
    
def __validate_input(username, user_email, password):
    problems = []
    temp_email = email.utils.parseaddr(user_email)
    if temp_email == ('', ''):
        problems.append("Invalid email address")
    cursor.execute("SELECT email FROM users WHERE email = ?", (user_email,))
    email_conflicts = cursor.fetchall()
    if email_conflicts != []:
        problems.append("Email address already in use")
    if len(password) > 128:
        problems.append("Password must be less than 100 characters")
    if len(password) < 8:
        problems.append("Password must be greater than 8 characters")
    if len(username) > 32:
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
        cursor.execute('''INSERT INTO users (username, email, salt, key, creationtime, admin, validated) VALUES (?, ?, ?, ?, ?, ?, ?)''', (
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
            session_id = base64.b64encode(os.urandom(64)).decode('utf-8')
            cursor.execute("UPDATE users SET logintime = ?, session_id = ?  WHERE username = ?", (logintime,session_id,username))
            connection.commit()
            return session_id
        else:
            return False # Incorrect password
    except TypeError as error:
        return False # User not found

def __get_key(password, salt):
    # As of 2013, at least 100,000 iterations of SHA-256 are suggested
    key = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
    return key
