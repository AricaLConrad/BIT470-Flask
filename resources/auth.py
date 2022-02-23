from flask_restful import Resource
from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, reqparse
from functools import wraps
from src.db import get_db
import jwt
import datetime
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
from resources.user import Users

parser = reqparse.RequestParser()

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
        hpw = generate_password_hash(data['password'], method='sha256')
        if not data['username'] or not data['password']:
            return jsonify({'error': 'enter a username or password'})
        res = get_db().cursor().execute(f'SELECT id FROM users WHERE username = "{un}"')
        respw = get_db().cursor().execute(f'SELECT password FROM users WHERE username = "{un}"')
        respwtext = respw.fetchone()
        restext = res.fetchall()
        get_db().close()
        if not restext:
            return jsonify({'user': 'user not found'})
        if check_password_hash(respwtext[0], pw):
            token = jwt.encode({'id' : restext, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}, "somesecretkeything", "HS256")
            return jsonify({'token': token.decode('UTF-8')}, 201)
        return make_response(f'could not verify. stored: "{respwtext}"  typed: "{hpw}"',  401, {'Authentication': '"login required"'})

