# Natalman Nahm
# Arica Conrad
# Mackenzie Fear

# Arica: I followed this tutorial for comments and error trapping:
# https://dev.to/imdhruv99/flask-user-authentication-with-jwt-2788

from flask import Flask, jsonify, make_response, request
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import uuid
import jwt
import datetime
from flask_restful import Resource, Api
from resources.user import User, Users, Staff, AllStaff
import sqlite3
from os.path import exists
from src.migrate_db import init_db
import src.const
from flask import g
from src.db import get_db
from resources.auth import Login, Logout, Token
from resources.rooms import Room, Rooms
from resources.rooms import Task, Tasks

# Arica: Making the Flask application.
app = Flask(__name__)

# Arica: An object of the Api class.
api = Api(app)

# Arica: Configuring the application.
app.config['SECRET_KEY'] = 'somesecretkeything'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///example.db'

# Arica: The JWTManager object.
jwt = JWTManager(app)

if not exists(src.const.DB_NAME):
    init_db()

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# def token_required(f):
#    @wraps(f)
#    def decorator(*args, **kwargs):
#        token = None
#        if 'x-access-tokens' in request.headers:
#            token = request.headers['x-access-tokens']
 
#        if not token:
#            return jsonify({'message': 'a valid token is missing'})
#        try:
#            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#            current_user = Users.query.filter_by(public_id=data['public_id']).first()
#        except:
#            return jsonify({'message': 'token is invalid'})
 
#        return f(current_user, *args, **kwargs)
#    return decorator

api.add_resource(HelloWorld, '/')
api.add_resource(User, '/users/<string:user_name>', '/signup')
api.add_resource(Users, '/users')
api.add_resource(Login, '/login')
api.add_resource(Logout,'/logout')
api.add_resource(Token,'/token')
api.add_resource(Room, '/rooms/<string:room_no>', '/rooms/create')
api.add_resource(Rooms, '/rooms')
api.add_resource(AllStaff, '/staff')
api.add_resource(Staff, '/staff/<staffid>')
api.add_resource(Tasks, '/tasks')
api.add_resource(Task, '/tasks/<task_id>', '/newtask')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
