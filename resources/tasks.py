# Arica: I followed this tutorial for comments and error trapping:
# https://dev.to/imdhruv99/flask-user-authentication-with-jwt-2788

from datetime import date
from tkinter import INSERT
from flask_restful import Resource, reqparse
from flask import jsonify#, request, abort, g, url_for
from src.db import get_db
from werkzeug.security import generate_password_hash,check_password_hash
#from passlib.apps import custom_app_context as pwd_context
#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

parser = reqparse.RequestParser()

class Task(Resource): 

    def get(self, task_id):

        result = get_db().cursor().execute(f'SELECT * FROM tasks WHERE id="{task_id}"')
        row = result.fetchone()
        return dict(zip([c[0] for c in result.description], row))

    def post(self):

        parser.add_argument('roomnumber')
        parser.add_argument('staffname')
        parser.add_argument('taskname')
        parser.add_argument('taskdesc')
        data = parser.parse_args()
        rid = data['roomnumber']
        sid = data['staffname']
        tnm = data['taskname']
        tdc = data['taskdesc']
        checkroom = get_db().cursor().execute(f'SELECT id FROM rooms WHERE roomnumber = "{rid}"').fetchone()
        if checkroom[0] is None:
            return jsonify({'message': 'invalid room number entered.'})
        checkstaff = get_db().cursor().execute(f'SELECT id FROM staff WHERE staffname = "{sid}"').fetchone()
        if checkstaff[0] is None:
            return jsonify({'message': 'invalid staff member entered.'})
        get_db().cursor().execute(f'INSERT INTO tasks(roomnumber, staffname, taskname, taskdesc) VALUES({rid}, "{sid}", "{tnm}", "{tdc}")')
        get_db().commit()
        get_db().close()
        return jsonify({'message': 'successfully added task'})

class Tasks(Resource):

    def get(self):
        
        result = get_db().cursor().execute('SELECT * FROM tasks')
        rows = result.fetchall()
        get_db().close()
        response = []
        for row in rows:
            response.append(dict(zip([c[0] for c in result.description], row)))
        return response