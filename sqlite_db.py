import time
import email
import hashlib
import base64
import os
import datetime
import sqlite3

connection = sqlite3.connect('db.sqlite3', check_same_thread = False)
cursor = connection.cursor()

# Create the DB if it doesn't exist
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


def check_id(username, id):
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
    cursor.execute("SELECT username, email, creationtime, logintime, validated, admin FROM users")
    users = cursor.fetchall()
    users_list = [list(user) for user in users]
    for user in users_list:
        user[2] = datetime.datetime.fromtimestamp(float(user[2])).strftime('%c')# creationtime
        try:
            user[3] = datetime.datetime.fromtimestamp(float(user[3])).strftime('%c')# logintime
        except TypeError:
            user[3] = "Never"
    return users_list

def get_num_users():
    cursor.execute("SELECT count(*) from users")
    count = cursor.fetchone()[0]
    return count

def register(username, user_email, password):
    problems = __validate_input(username, user_email, password)
    if problems != []:
        return problems
    if get_num_users() == 0:
        admin = True # Set first user as admin
    else:
        admin = False
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
            admin,
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


def logoff(username):
    cursor.execute("UPDATE users SET session_id = NULL WHERE username = ?", (username,))
    connection.commit()


def __validate_input(username, user_email, password):
    problems = []
    # Alphanumeric check
    if username.isalnum() == False:
        problems.append("Username must be alphanumeric")
    # Banned password check
    with open('banned_passwords.txt', 'r') as file:
        banned_passwords = file.read()
        if password.decode('utf-8') in banned_passwords:
            problems.append("Password too common")
    # Malformed email
    temp_email = email.utils.parseaddr(user_email)
    if temp_email == ('', ''):
        problems.append("Invalid email address")
    # Duplicate email
    cursor.execute("SELECT email FROM users WHERE email = ?", (user_email,))
    email_conflicts = cursor.fetchall()
    if email_conflicts != []:
        problems.append("Email address already in use")
    # Password upper limit
    if len(password) > 128:
        problems.append("Password must be less than 100 characters")
    # Password lower limit
    if len(password) < 8:
        problems.append("Password must be greater than 8 characters")
    # Username upper limit
    if len(username) > 32:
        problems.append("Username must be less than 30 characters")
    # Username lower limit
    if len(username) < 4:
        problems.append("Username must be greater than 4 characters")
    return problems


def __get_key(password, salt):
    key = hashlib.pbkdf2_hmac('sha512', password, salt, 100000)
    return key
