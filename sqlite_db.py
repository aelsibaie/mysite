from time import time

import hashlib

import sqlite3
connection = sqlite3.connect('users.sqlite3', check_same_thread = False)
cursor = connection.cursor()

# First, let's create the DB if it doesn't exist
cursor.execute('''CREATE TABLE if not exists users (
    username    TEXT    PRIMARY KEY,
    email       TEXT,
    salt        BLOB,
    key         BLOB,
    time        DATETIME,
    admin       BOOLEAN,
    validated   BOOLEAN)''')

class User:
    def __init__(self, username, email=None, salt=None, key=None, time=None, admin=False, validated=False, password=None):
        self.username = username
        self.email = email
        self.salt = salt
        self.key = key
        self.time = time
        self.admin = admin
        self.validated = validated
        self.password = password
    
    def register(self):
        self.__get_key()
        try:
            cursor.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (
                self.username,
                self.email,
                self.salt,
                self.key,
                time(),
                self.admin,
                self.validated,)
            )
            connection.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate username detected
            return False
            
    def login(self):
        try:
            cursor.execute("SELECT salt, key FROM users WHERE username=?", (self.username,))
            salt, key = cursor.fetchone()
            
            self.__get_key()
            
            if self.key == key:
                print("LOG HIM IN!!")
            else:
                print("GET ON OUT!!")

        except sqlite3.IntegrityError:
            print("uh oh")

    def __get_key(self):
        # As of 2013, at least 100,000 iterations of SHA-256 are suggested
        self.key = hashlib.pbkdf2_hmac('sha256', self.password, self.salt, 100000)
