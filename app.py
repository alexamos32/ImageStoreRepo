#!/usr/bin/env python3
from flask import Flask, jsonify, abort, request, make_response, session
from flask_restful import Resource, Api, reqparse
from flask_session import Session
import pymysql.cursors
import json
import werkzeug, os

from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *

import cgitb
import cgi
import sys
cgitb.enable()

import settings

app = Flask(__name__)
api= Api(app)

# Setting up SESSION info

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
                return make_response(jsonify({ "message": "Welcome to the Image Store Repo. Go to /signin POST to sign in."}), 200)

api.add_resource(Root,'/')


class Users(Resource):
        #'ONLY POST
        #For creating new users, but do not want to Allow GET on all users
        def post(self):
                # Sample command line usage:
        #
        # curl -i -X POST -H "Content-Type: application/json"
        #    -d '{"username": "johnsmith1"}'
        #         http://info3103.cs.unb.ca:xxxxx/schools
        
                if not request.json or not 'username' in request.json:
                        abort(400)

                username = request.json['username']

                try:
                        dbConnection = pymysql.connect(settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        sql = 'insertUser'
                        cursor = dbConnection.cursor()
                        sqlArgs = (username)
                        cursor.callproc(sql,sqlArgs)
                        row = cursor.fetchone()
                        dbConnection.commit()
                except:
                        abort(500) #Server error
                finally:
                        cursor.close()
                        dbConnection.close()
                #Construct URI to return to user for successful creation
                uri = 'http://' + settings.APP_HOST + ':' + str(settings.APP_PORT)
                uri = uri + str(request.url_rule) + '/' + str(row['LAST_INSERT_ID()'])
                return make_response(jsonify( { "usr" : uri } ), 201)

api.add_resource(Users, '/users')


class User(Resource):
        #GET: get info about user
        #UPDATE: Update User info
        def get(self, username):
                try:
                        dbConnection = pymysql.connect(settings.DB_HOST,
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

api.add_resource(User, '/users/<int:userId>')

class Images(Resource):
        def get(self, userId):
                #Retrieving parameters
                url = request.url
                imageId = None
                if "imageId" in url:
                        imageId = request.args.get("imageId")
                try:
                        dbConnection = pymysql.connect(settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        if imageId is None:
                                sql = 'getImages'
                                sqlArgs = (userId)
                        else:
                                #Args: owner, imageId
                                sql = 'getImageById'
                                sqlArgs = (userId, imageId)

                        cursor = dbConnection.cursor()
                        cursor.callproc(sql,sqlArgs)
                        rows = cursor.fetchall()
                        for row in rows:
                                pass
                except:
                        abort(500)
                return 'HEy'
    
        def post(self):
                if not request.json:
                        abort(400)#bad request
        
                #Parse Json
                parser = reqparse.RequestParser()
                #try:
                return "Hey"
            

api.add_resource(Images, '/users/<int:userId>/images')

if __name__ == "__main__":
   	app.run(host=settings.APP_HOST, port=settings.APP_PORT, debug=settings.APP_DEBUG)
