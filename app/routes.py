from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db, Api
from app.models import User, Subject, Chapter, Quiz, Questions, Scores, Enrollments
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort

bp_main=Blueprint('main',__name__)

user_args=reqparse.RequestParser()
user_args.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

class Users(Resource):
    def get(self):
        users=User.query.all()
        return [u.to_dict() for u in users], 200
    
class Register(Resource):
    def post(self):
        data = request.get_json()
        username=data.get('username')
        email=data.get('email')
        password=data.get('password')

        if User.query.filter_by(username=username).first():
            return {"error": "Username already exists"}, 400
        if User.query.filter_by(email=email).first():
            return {"error": "Email already exists"}, 400
        

        hashed=generate_password_hash(password)
        new_user= User(username=username, email=email, password_hash=hashed)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201
    



@bp_main.route('/')
def home():
    return render_template('index.html')
@bp_main.route('/register')
def register():
    return render_template('register.html')

