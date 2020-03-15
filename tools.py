from flask import Flask, jsonify, abort, request, make_response, session, render_template
from flask_restful import Resource, Api, reqparse
from flask_session import Session
from functools import wraps


ALLOWED_EXTENSION = set(['png', 'jpg', 'jpeg', 'gif'])



def authenticated(f):
    @wraps(f)
    def wrapper(self, userId):
        print('authenticated')
        return f(self, userId)

    return wrapper



def allowed_file(filename):
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSION
