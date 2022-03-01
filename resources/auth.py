# Arica: I followed this tutorial for comments and error trapping:
# https://dev.to/imdhruv99/flask-user-authentication-with-jwt-2788

import re
from flask_restful import Resource
from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, reqparse
from functools import wraps
from src.db import get_db
import sqlite3
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from resources.user import Users

parser = reqparse.RequestParser()

# Arica: Does this need to be implemented? 
class Signup(Resource):

    def post(self, credentials):

        return 'signing up'

class Login(Resource):

    def post(self):

        parser.add_argument('username')
        parser.add_argument('password')
        data = parser.parse_args()
        un = data['username']
        pw = data['password']

        # Arica: Checks to see if both username and password are empty.
        if not data['username'] and not data['password']:
            message = jsonify(error = 'Username and password are required fields.')
            return make_response(message, 400) 

        # Arica: Checks to see if only the username is empty.
        if not data['username']:
            message = jsonify(error = 'Username is a required field.')
            return make_response(message, 400) 

        # Arica: Checks to see if only the password is empty.
        if not data['password']:
            message = jsonify(error = 'Password is a required field.')
            return make_response(message, 400) 

        # Arica: Checks to see if the username and/or password are typed incorrectly.
        if not get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone() or not get_db().cursor().execute(f'SELECT id FROM users WHERE password = "{pw}"').fetchone():
            message = jsonify(error = 'Incorrect username or password submitted. Please check if the username or password is typed correctly.')
            return make_response(message, 400)   

        hpw = generate_password_hash(data['password'], method='sha256')

        try:

            res = get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone()
            respw = get_db().cursor().execute(f'SELECT password FROM users WHERE username = "{un}"').fetchone()
            # respwtext = respw.fetchone()
            # restext = res.fetchone()

            con = sqlite3.connect('example.db')
            cur = con.cursor()

            cur.execute('CREATE TABLE IF NOT EXISTS token(id INTEGER NOT NULL, tokenid text PRIMARY KEY)')
            con.commit()
            con.close()

            if check_password_hash(respw[0], pw):
                token = jwt.encode({'id' : res[0], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, "somesecretkeything", "HS256")
                get_db().cursor().execute(f'INSERT INTO token(id, tokenid) VALUES({res[0]},"{token}")')
                get_db().commit()
                # Arica: Returns a successful login message. I removed the token to test it out.
                # When the token is not returned, I can log in. If it returns the token, I get a 500 error message.
                # Does the token need to be returned? Does the user need to see it?
                message = jsonify(message = 'Successfully logged in. Welcome!')
                return make_response(message, 200)
                # Original code: 
                # return jsonify({'token': token}, 201)
                # Originally commented out:
                # access_token = create_access_token(identity=un)
                # return jsonify({'token': access_token}, 200)

            get_db().close()
        
        except:
            
            message = jsonify(error = 'Something went wrong during the login process. Please try again.')
            return make_response(message, 500)
            # Arica: Leaving this one just in case:
            # return make_response(f'could not verify. stored: "{respw}"  typed: "{hpw}"',  401, {'Authentication': '"login required"'})

class Logout(Resource):

    def delete(self):

        parser.add_argument('username')
        data = parser.parse_args()
        un = data['username']

        # Arica: Checks to see if the username is empty.
        if not data['username']:
            message = jsonify(error = 'Username is a required field.')
            return make_response(message, 400) 
        
        # Arica: Checks to see if the username is typed incorrectly.
        if not get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone():
            message = jsonify(error = 'Incorrect username submitted. Please check if the username is typed correctly.')
            return make_response(message, 400) 

        try:
            
            res = get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone()
            validToken = get_db().cursor().execute(f'SELECT tokenid FROM token WHERE id = {res[0]}').fetchone()
            
            # Arica: Checks to see if the token has already been deleted (i.e. the user has already logged out).
            if validToken is None:
                message = jsonify(message = 'You have already logged out.')
                return make_response(message, 404)

            if validToken:
                get_db().cursor().execute(f'DELETE FROM token WHERE id = {res[0]}')
                get_db().commit()
                message = jsonify(message = 'Successfully logged out. Goodbye!')
                return make_response(message, 200)
        
            get_db().close()
        
        except:
            
            message = jsonify(error = 'Something went wrong during the logout process. Please try again.')
            return make_response(message, 500)
            # Arica: Leaving this one just in case:
            # return make_response(f'was not able to log you out with id: "{res[0]}"', 400, {'info': '"you might have log out already"'})

class Token(Resource):

    def get(self):

        result = get_db().cursor().execute('SELECT * FROM token')
        rows = result.fetchall()
        get_db().close()
        response = []
        for row in rows:
            response.append(dict(zip([c[0] for c in result.description], row)))
        return response


