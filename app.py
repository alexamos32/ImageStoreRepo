#!/usr/bin/env python3
from flask import Flask, jsonify, abort, request, make_response, session, render_template
from flask_restful import Resource, Api, reqparse
from flask_session import Session
import json
import werkzeug, os
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql.cursors
import ssl

import cgitb
import cgi
import sys
cgitb.enable()

import settings
UPLOAD_FOLDER ='/path/to/folder' #PLACEHOLDER
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])
app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
Session(app)

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
                return make_response( jsonify({ "message": "Welcome to the Image Store Repo. Go to /signin POST to sign in."}), 200)



class SignIn(Resource):
        #
        # Login, start a session and set/return a session cookie
        #
        # Example curl command:
        # curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Casper", "password": "cr*ap"}'
        #  	-c cookie-jar http://info3103.cs.unb.ca:61340/signin
        #
        def post(self):
                userId = None
                if not request.json:
                        abort(400) # bad request
                # Parse the json
                parser = reqparse.RequestParser()
                try:
                        # Check for required attributes in json document, create a dictionary
                        parser.add_argument('username', type=str, required=True)
                        parser.add_argument('password', type=str, required=True)
                        request_params = parser.parse_args()
                except:
                        #Bad request if missing username or password
                        abort(400) # bad request

                # Already logged in
                if request_params['username'] in session:
                        response = {'status': 'success'}
                        responseCode = 200
                else:
                        try:
                                #Attempting Login through LDAP
                                ldapServer = Server(host=settings.LDAP_HOST)
                                ldapConnection = Connection(ldapServer,
                                        raise_exceptions=True,
                                        user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
                                        password = request_params['password'])
                                ldapConnection.open()
                                ldapConnection.start_tls()
                                ldapConnection.bind()
                                # At this point we have sucessfully authenticated.
                                #Add username to session object
                                session['username'] = request_params['username']
                                response = {'status': 'success' }
                                responseCode = 201
                        except (LDAPException):
                                response = {'status': 'Access denied'}
                                responseCode = 403
                        finally:
                                ldapConnection.unbind()

                #If Logged in
                if responseCode <=201:
                        try:
                                #Check user exists in DB
                                dbConnection = pymysql.connect(
                                        settings.DB_HOST,
                                        settings.DB_USER,
                                        settings.DB_PASSWD,
                                        settings.DB_DATABASE,
                                        charset='utf8mb4',
                                        cursorclass= pymysql.cursors.DictCursor)
                                sql = 'getUserByUsername'
                                sqlArgs = (request_params['username'],)
                                cursor = dbConnection.cursor()
                                cursor.callproc(sql,sqlArgs)
                                row = cursor.fetchone()

                        except :
                                abort(500)

                        if row is None:
                                #User Doesn't exist must insert user
                                try:
                                        sql = 'insertUser'
                                        cursor.callproc(sql,sqlArgs)
                                        row = cursor.fetchone()
                                        dbConnection.commit()

                                except:
                                        abort(500)
                                finally:
                                        cursor.close()
                                        dbConnection.close()
                                if "userId" in row:
                                        userId = row["userId"]
                                else:
                                        abort(500)
                                path = './users/'+ str(userId)
                                pathImg = path + '/images'
                                #Set up folders for user on server
                                try:
                                        os.mkdir(path)
                                        os.mkdir(pathImg)
                                except OSError:
                                        abort(500)
                        else:
                                #user already exists, save userId for response
                                userId = row["userId"]
                response["userId"] = userId
                response["message"] = 'Got to /users/<userId>/images (GET to view images, POST to upload images)'

                return make_response(jsonify(response), responseCode)

        # GET: Check for a login
        #
        # Example curl command:
        # curl -i -H "Content-Type: application/json" -X GET -b cookie-jar
        #http://info3103.cs.unb.ca:61340/signin
        def get(self):
                if 'username' in session:
                        response = {'status': 'success'}
                        responseCode = 200
                else:
                        response = {'status': 'fail'}
                        responseCode = 403

                return make_response(jsonify(response), responseCode)

        def delete(self):
                ###############
                #Log Out a User
                ###############
                if 'username' in session:
                        session.clear()
                        response = {'status': 'successfully logged out'}
                        responseCode = 200
                else:
                        response = {'status': 'could not log out'}
                        responseCode = 403

                return make_response(jsonify(response), responseCode)


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
            


#Create EndPoints            
api= Api(app)
api.add_resource(Users, '/users')
api.add_resource(Images, '/users/<int:userId>/images')
api.add_resource(User, '/users/<int:userId>')
api.add_resource(SignIn, '/signin')
api.add_resource(Root,'/') 
if __name__ == "__main__":
        context = ('cert.pem', 'key.pem')
        app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)
