from datetime import date
from flask_restful import Resource, reqparse
from flask import jsonify#, request, abort, g, url_for
from src.db import get_db
from werkzeug.security import generate_password_hash,check_password_hash
#from passlib.apps import custom_app_context as pwd_context
#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

parser = reqparse.RequestParser()

class User(Resource): 
    def get(self, user_name):
        result = get_db().cursor().execute(f'SELECT * FROM users WHERE username="{user_name}"')
        row = result.fetchone()
        return dict(zip([c[0] for c in result.description], row))
    def post(self):
        parser.add_argument('username')
        parser.add_argument('password')
        data = parser.parse_args()
        un = data['username']
        #pw = data['password']
        hpw = generate_password_hash(data['password'], method='sha256')
        get_db().cursor().execute(f'INSERT INTO users(id, username, password) VALUES({hash(un)}, "{un}", "{hpw}")')
        get_db().commit()
        get_db().close()
        return jsonify({'message': 'successfully signed up'})
class Users(Resource):
    def get(self):
        result = get_db().cursor().execute('SELECT * FROM users')
        rows = result.fetchall()
        get_db().close()
        response = []
        for row in rows:
            response.append(dict(zip([c[0] for c in result.description], row)))
        return response