# Arica: I followed this tutorial for comments and error trapping:
# https://dev.to/imdhruv99/flask-user-authentication-with-jwt-2788

import re
from flask_restful import Resource
from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_restful import Resource, reqparse
from functools import wraps
from src.db import get_db
import sqlite3
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
from resources.user import Users

parser = reqparse.RequestParser()


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

        # Arica: Checks to see if the username is typed incorrectly.
        if not get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone():
            get_db().close()
            message = jsonify(error = 'Incorrect username submitted. Please check if the username is typed correctly.')
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

                # Arica: Instead of just returning a message saying the user is already logged in,
                # we now create and return a new token. Initially, this was in a try-except block.
                # However, since we want to create a new token every time the user logs in, we do not
                # care if they were already logged in. We just send them a new token.

                exp = datetime.timedelta(minutes=45)
                token = create_access_token(identity=str(res[0]), expires_delta=exp)
                get_db().cursor().execute(f'INSERT INTO token(id, tokenid) VALUES({res[0]},"{token}")')
                get_db().commit()
                get_db().close()
                message = jsonify(token = token)
                return make_response(message, 200)

                # Original code: 
                # try block to catch users already logged in.
                # try:

                #     isloggedin = get_db().cursor().execute(f'SELECT id FROM token WHERE id = "{res[0]}"').fetchone()

                #     if not isloggedin[0] is None:

                #         # message = jsonify(message = 'User is already logged in.')
                #         # return make_response(message, 400)
                
                # except:

                #     exp = datetime.timedelta(minutes=45)
                #     token = create_access_token(identity=str(res[0]), expires_delta=exp)
                #     get_db().cursor().execute(f'INSERT INTO token(id, tokenid) VALUES({res[0]},"{token}")')
                #     get_db().commit()
                #     get_db().close()
                #     # Arica: No longer returns a successful login message, just the 200 HTTP code. Instead, the 
                #     # token is returned. The make_response method can only accept one argument and the code, unless
                #     # you made it a tuple by passing in some headers information, according to my internet research.
                #     message = jsonify(token = token)
                #     return make_response(message, 200)
                #     # Original code: 
                #     # return jsonify({'token': token}, 201)
                #     # Originally commented out: 
                #     # access_token = create_access_token(identity=un)
                #     # return jsonify({'token': access_token}, 200)

            get_db().close()

            # Arica: Otherwise, the password was typed incorrectly.
            message = jsonify(error = 'Incorrect password submitted. Please check if the password is typed correctly.')
            return make_response(message, 400)

        except:

            message = jsonify(error = 'Something went wrong during the login process. Please try again.')
            return make_response(message, 500)
            # Arica: Leaving this one just in case:
            # return make_response(f'could not verify. stored: "{respw}"  typed: "{hpw}"',  401, {'Authentication': '"login required"'})


#TODO: For the future, we might want adjust the logout to check against the login token and not the username. 
# Arica: Could comment out Logout, but I left it for now so that I could check if the tokens are being deleted.

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
            get_db().close()
            message = jsonify(error = 'Incorrect username submitted. Please check if the username is typed correctly.')
            return make_response(message, 400) 
        
        try:

            res = get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"').fetchone()
            validToken = get_db().cursor().execute(f'SELECT tokenid FROM token WHERE id = {res[0]}').fetchone()

            # Arica: Checks to see if the token has already been deleted (i.e. the user has already logged out).
            if validToken is None:
                get_db().close()
                message = jsonify(message = 'You have already logged out.')
                return make_response(message, 404)
            
            if validToken:
                get_db().cursor().execute(f'DELETE FROM token WHERE id = {res[0]}')
                get_db().commit()
                get_db().close()
                message = jsonify(message = 'Successfully logged out. Goodbye!')
                return make_response(message, 200)        

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
