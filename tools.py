from flask import Flask, jsonify, request, abort, make_response, session, render_template
from flask_session import Session
from functools import wraps
import pymysql.cursors
import settings


ALLOWED_EXTENSION = set(['png', 'jpg', 'jpeg', 'gif'])


#Wrapper function that checks if user is authenticated
#returns 403 if user is not
def authenticated(f):
    @wraps(f)
    def wrapper_authenticated(*args, **kwargs):
        if not 'username' in session:
            response = {'status': 'fail', 'message': 'must sign in'}
            responseCode = 403
            return make_response(jsonify(response), responseCode)
        return f(*args, **kwargs)

    return wrapper_authenticated

#Wrapper function that checks if user is authorized to view that resource.
#Returns 403 if the user is attempting to access another user's resources
def authorized(f):
    @wraps(f)
    def wrapper_authorized(*args, **kwargs):
        username = None;
        if 'username' in session:
            username = session['username']
        else:
            return make_response(jsonify({'status': 'fail', 'message': 'must sign in'}),403)
        path = request.path
        path = path.split('/')
        uid = int(path[2])
        try:
            #Retrieve user info from db based of session cookie data
             dbConnection = pymysql.connect(
                                settings.DB_HOST,
                                settings.DB_USER,
                                settings.DB_PASSWD,
                                settings.DB_DATABASE,
                                charset='utf8mb4',
                                cursorclass= pymysql.cursors.DictCursor)
             sql = 'getUserByUsername'
             sqlArgs = (username,)
             cursor = dbConnection.cursor()
             cursor.callproc(sql, sqlArgs)
             row = cursor.fetchone()
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()

        if row is None:
            abort(404)
        #Compare actual uid and uid specified in resource path
        if not int(row['userId']) == uid:
            return make_response(jsonify({'status': 'fail', 'message': 'Not authorized to view this resource'}),403)

        return f(*args, **kwargs)
    return wrapper_authorized


#Checks if the file being uploaded is within the allowed file types
def allowed_file(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSION
