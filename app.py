#!/usr/bin/env python3
from flask import Flask, jsonify, abort, request, make_response, session, send_from_directory
from flask_restful import Resource, Api, reqparse
from flask_session import Session
import json
import werkzeug, os, shutil
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql.cursors
import ssl
from tools import allowed_file, authenticated, authorized
import cgitb
import cgi
import sys
cgitb.enable()

import settings
app = Flask(__name__, static_url_path='/static')
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
                #return make_response( jsonify({ "message": "Welcome to the Image Store Repo. Go to /signin POST to sign in."}), 200)
                return app.send_static_file('index.html')



class SignIn(Resource):
        #
        # Login, start a session and set/return a session cookie
        #
        # Example curl command:
        # curl -i -H "Content-Type: application/json" -X POST
        # -d '{"username": "Casper", "password": "cr*ap"}'
        # -c cookie-jar -k https://info3103.cs.unb.ca:51496/signin
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
        # -k https://info3103.cs.unb.ca:51496/signin
        def get(self):
                if 'username' in session:
                        response = {'status': 'success'}
                        responseCode = 200
                else:
                        response = {'status': 'fail', 'message': 'must sign in'}
                        responseCode = 403

                return make_response(jsonify(response), responseCode)


        # DELETE: Log Out a User
        #
        # Example curl command:
        # curl -i -X DELETE -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/signin
        @authenticated
        def delete(self):
                session.clear()
                response = {'status': 'successfully logged out'}
                responseCode = 204

                return make_response(jsonify(response), responseCode)



class User(Resource):
        # DELETE: For deleting a user and all associated images of said user
        #
        # Example curl command:
        # curl -i -X DELETE -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>
        @authenticated
        @authorized
        def delete(self, userId):

                path = './users/'+str(userId)
                #return not found if path to user folder does not exist
                if not os.path.exists(path):
                       abort(404)
                try:
                        #Delete all user info from DB and associated images
                        dbConnection = pymysql.connect(settings.DB_HOST,
                                                       settings.DB_USER,
                                                       settings.DB_PASSWD,
                                                       settings.DB_DATABASE,
                                                       charset='utf8mb4',
                                                       cursorclass= pymysql.cursors.DictCursor)
                        sql = 'deleteUser'
                        cursor = dbConnection.cursor()
                        sqlArgs = (userId,)
                        cursor.callproc(sql,sqlArgs)
                        row = cursor.fetchone()
                        dbConnection.commit()
                #Universal catch, all errors will result in a 500
                except:
                        abort(500) #Server error
                finally:
                        cursor.close()
                        dbConnection.close()

                try:
                        #Delete folder containing user images
                        shutil.rmtree(path)
                except:
                        #user folder not found
                        abort(500)
                return make_response(jsonify( { "status" : "success" } ), 204)





class Images(Resource):
        # GET: Returns list of all images for user, or 1 image with specified ID
        #
        # Example curl command:
        # curl -i -H "Content-Type: application/json" -d '{"imageId": 1}
        # -X GET -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>/images
        #
        # OR
        #
        # curl -i -X GET -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>/images
        @authenticated
        @authorized
        def get(self, userId):
                #Retrieving parameters
                imageId = None
                parser = reqparse.RequestParser()
                parser.add_argument('imageId', type=int)
                request_params = parser.parse_args()
                if "imageId" in request_params:
                        imageId = request_params["imageId"]
                try:
                        dbConnection = pymysql.connect(settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        #Procedure changes if imageId specified
                        if imageId is None:
                                sql = 'getImages'
                                sqlArgs = (userId,)
                        else:
                                #Args: owner, imageId
                                sql = 'getImageById'
                                sqlArgs = (userId, imageId)

                        cursor = dbConnection.cursor()
                        cursor.callproc(sql,sqlArgs)
                        rows = cursor.fetchall()

                except:
                        abort(500)
                finally:
                        cursor.close()
                        dbConnection.close()
                response={'images': rows}
                responsecode=200
                return make_response(jsonify(response),responsecode)

        # POST: Upload a new image
        # Allowed types (jpg, jpeg, gif, png)
        # Example curl command:
        # curl -i -X POST -H "Content-Type: multipart/form-data"
        # -F "file=@test.jpg" -F "description=image description" -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>/images
        #
        #NOTE: description is an optional parameter
        @authenticated
        @authorized
        def post(self, userId):
                UPLOAD_FOLDER = 'users/'+str(userId)+'/images'
                description = None
                imageId=None

                parser = reqparse.RequestParser()
                #Adding arguments for imagefile and description
                parser.add_argument('file',type=werkzeug.datastructures.FileStorage, location='files')
                parser.add_argument('description',type=str)
                data = parser.parse_args()

                #Error if no file included
                if not request.files:
                        abort(400)#bad request

                #Grab file from arguments
                photo = data['file']
                #Split file name to get file type e.g. test.jpg
                filetype = (photo.filename).split(".")[1].lower()
                #return error if filetype is not permitted
                if not allowed_file(photo.filename):
                        return make_response(jsonify({"error": "only allowed types: jpg, jpeg, png, gif"}),403)

                #If description is in request grab it for db
                if 'description' in data:
                        description = data['description']
                try:
                        #DB INSERT
                        dbConnection = pymysql.connect(
                                settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        sql = 'insertImage'
                        sqlArgs = (description, UPLOAD_FOLDER, userId, filetype)
                        cursor = dbConnection.cursor()
                        cursor.callproc(sql,sqlArgs)
                        row = cursor.fetchone()
                        dbConnection.commit()
                except:
                        abort(500)
                finally:
                       cursor.close()
                       dbConnection.close()
                #Insert will return row for image from db
                if 'imageId' in row:
                        imageId = row['imageId']
                else:
                        abort(500)
                #Join image ID and Filetype to create filename, then save file
                filename = str(imageId) +'.'+ filetype
                try:
                        photo.save(os.path.join(UPLOAD_FOLDER,filename))
                except:
                        abort(500)
                #Create a path to image to return to user
                path = UPLOAD_FOLDER +'/'+ str(imageId)
                responsecode = 201
                response = {"status": "success", "url": path }
                return make_response(jsonify(response),responsecode)

class ImageId(Resource):
        # GET: Returns an image file back to user
        #
        # Example curl command:
        # curl -X GET -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>/images/<imageId>
        # --output download.jpg
        # NOTE: do not use -i curl tag for this command.
        # This will cause headers to be saved in image file creating a corrupte file
        # Also should perform GET on images endpoint first
        # This will show list of images along with their file types,
        # this way the output file can be saved with the proper file type
        # i.e jpg, png ...
        @authenticated
        @authorized
        def get(self, userId, imageId):
                try:
                        #Search for image in DB
                        dbConnection = pymysql.connect(
                                settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        sql = 'getImageById'
                        sqlArgs = (userId, imageId)
                        cursor = dbConnection.cursor()
                        cursor.callproc(sql, sqlArgs)
                        row = cursor.fetchone()
                except:
                        abort(500)
                finally:
                        cursor.close()
                        dbConnection.close()

                #Abort 404 if no image found
                if row is None:
                        abort(404)
                #Grab filetype from DB row
                filetype = row["filetype"]
                imagename = str(imageId) +"." + filetype
                directory = "users/"+str(userId)+"/images"
                try:
                        #Send file to user as attachment
                        return make_response(send_from_directory(directory, filename=imagename, as_attachment=True),200)
                except:
                        #404 if file not found in specified directory
                        abort(404)


        # DELETE: Delete an image
        #
        # Example curl command:
        # curl -i -X DELETE -b cookie-jar
        # -k https://info3103.cs.unb.ca:51496/users/<userId>/images/<imageId>
        @authenticated
        @authorized
        def delete(self, userId, imageId):
                try:
                        #Delete image from DB
                        #Procedure will also return deleted row so that filetype can be obtained
                        dbConnection = pymysql.connect(
                                settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
                        sql = 'deleteImage'
                        sqlArgs = (imageId,)
                        cursor = dbConnection.cursor()
                        cursor.callproc(sql, sqlArgs)
                        row = cursor.fetchone()
                        dbConnection.commit()
                except:
                        abort(500)
                finally:
                        cursor.close()
                        dbConnection.close()
                if row is None:
                        abort(404)
                #construct filename and path for file delete
                filename = str(imageId)+'.'+row['filetype']
                path = 'users/'+str(userId)+'/images/'+filename
                try:
                        os.remove(path)
                except:
                        #abort 404 if image not found
                        abort(404)
                response = {'status': 'success'}
                responsecode = 204
                return make_response(jsonify(response),responsecode)
#Create EndPoints            
api= Api(app)
api.add_resource(Images, '/users/<int:userId>/images')
api.add_resource(SignIn, '/signin')
api.add_resource(ImageId, '/users/<int:userId>/images/<int:imageId>')
api.add_resource(User, '/users/<int:userId>')
api.add_resource(Root,'/') 
if __name__ == "__main__":
        context = ('cert.pem', 'key.pem')
        app.run(host=settings.APP_HOST, port=settings.APP_PORT, ssl_context=context, debug=settings.APP_DEBUG)
