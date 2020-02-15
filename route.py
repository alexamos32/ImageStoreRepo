#!/usr/bin/env python3
from flask import Flask, jsonify, abort, request, make_response
from flask_restful import Resource, Api
import pymysql.cursors
import json

import cgitb
import cgi
import sys
cgitb.enable()

import settings

app = Flask(__name__)
api= Api(app)


####################################################################################
# Error handlers

@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { "status": "Bad request" } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { "status": "Resource not found" } ), 404)
####################################################################################



####################################################################################
# Endpoints

#TODO: Create and return index.html
class Root(Resource):
    def get(self):
        return 'Image Storage Repo'

api.add_resource(Root,'/')


class Users(Resource):
    #ONLY POST
    #For creating new users, but do not want to Allow GET on all users
    def post(self):
        # Sample command line usage:
        #
        # curl -i -X POST -H "Content-Type: application/json"
        #    -d '{"Name": "Rick\'s School of Web", "Province": "NB", "Language":
        #		  "EN", "Level": "simple"}'
        #         http://info3103.cs.unb.ca:xxxxx/schools
        
        #TODO: Finish posting users
        return

    
api.add_resource(Users, '/users')


class User(Resource):
    #GET: get info about user
    #UPDATE: Update User info
    def get(self, username):
        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
				settings.DB_DATABASE,
                charset='utf8mb4',
				cursorclass= pymysql.cursors.DictCursor)
            sql = 'getUserByUname'
            cursor = dbConnection.cursor()
            sqlArgs = (username,)
            cursor.callproc(sql,sqlArgs)
            row = cursor.fetchone()
            if row is None:
                abort(404)
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"user": row}), 200)
        
    

    def update(self, userId):
        return

apt.add_resource(User, '/users/<int:userId>')