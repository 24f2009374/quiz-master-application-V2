from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db, Api
from app.models import User, Subject, Chapter, Quiz, Questions, Scores, Enrollments
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_login import login_required, current_user, logout_user, login_user, login_manager
import datetime

bp_main=Blueprint('main',__name__)

#--------------------------------------------ADMIN WRAPPER--------------------------------------------
def admin_required(f):
    @wraps(f)
    def decor(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You do not have permission to view this page!", "danger")
            return redirect(url_for('home'))  # Redirect non-admins to home
        return f(*args, **kwargs)
    return decor

"""---------------------------------------------------------API SECTION---------------------------------------------------------"""

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
    
class Login(Resource):
    def post(self):
        data=request.get_json()
        email=data.get('email')
        password=data.get('password')

        if not email or not password:
            return {"error": "Both fields are required"}, 400
        
        user=User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"error": "Invalid email or password"}, 401
        
        login_user(user)

        if user.role == "admin":
            return jsonify({"redirect": url_for('main.admin_dashboard')})
        else:
            return jsonify({"redirect": url_for('main.user_dashboard', user_id=user.user_id)})
    

#--------------------------------------------CRUD RESOURCES--------------------------------------------

class DB_Subjects(Resource):
    method_decorators=[login_required]
    
    def get(self):
        subs=Subject.query.all()
        return [{'id':s.sub_id, 'name':s.sub_name, 'desc':s.sub_desc} for s in subs]
    
    def post(self):
        data=request.get_json()
        sub_name=data.get('sub_name')
        sub_desc=data.get('sub_desc')

        if not sub_name or not sub_desc:
            return {"error": "Both fields are required"}, 400
        
        subj=Subject.query.filter_by(sub_name=sub_name).first()

        if subj:
            return {"error": "Subject Exists"}, 401
        
        new_sub= Subject(sub_name=sub_name, sub_desc=sub_desc)
        db.session.add(new_sub)
        db.session.commit()

        return {'message': 'Subject created successfully'}, 201
    
class DB_Chapters(Resource):
    method_decorators=[login_required]
    def get(self, sub_id):
        chaps=Chapter.query.filter_by(subject_id=sub_id)
        return [{'id':c.chap_id, 'name':c.chap_name, 'desc':c.chap_desc, 'parent':c.subject_id} for c in chaps]
    
    def post(self, sub_id):
        data=request.get_json()
        chap_name=data.get('chap_name')
        chap_desc=data.get('chap_desc')
        sub_id=data.get('sub_id')

        if not chap_name or not chap_desc:
            return {"error": "Both fields are required"}, 400
        
        chap=Chapter.query.filter_by(chap_name=chap_name).first()

        if chap:
            return {"error": "Chapter Exists"}, 401
        
        new_chap= Chapter(chap_name=chap_name, chap_desc=chap_desc, subject_id=sub_id)
        db.session.add(new_chap)
        db.session.commit()

        return {'message': 'Chapter created successfully'}, 201
    
    pass

class DB_Quizzes(Resource):
    method_decorators=[login_required]
    def get(self, chap_id):
        quizzes=Quiz.query.filter_by(chapter_id=chap_id)
        return [{'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.isoformat(), 'parent':q.chapter_id} for q in quizzes]
    
    def post(self, chap_id):
        data=request.get_json()
        quiz_name=data.get('quiz_name')
        date_str=data.get('date')
        time=data.get('time')
        chap_id=data.get('chap_id')

        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        if not quiz_name or not date_obj or not time:
            return {"error": "All fields are required"}, 400
        
        quiz=Quiz.query.filter_by(quiz_name=quiz_name).first()

        if quiz:
            return {"error": "Quiz Exists"}, 401
        
        new_quiz=Quiz(quiz_name=quiz_name, date=date_obj, time=time, chapter_id=chap_id)
        db.session.add(new_quiz)
        db.session.commit()

        return {'message': 'Quiz created successfully'}, 201
    
class DB_Questions(Resource):
    method_decorators=[login_required]
    def get(self, quiz_id):
        questions=Questions.query.filter_by(quiz_id=quiz_id)
        return [{'id':q.qid,'statement':q.question_statement, 'parent':q.quiz_id, 'correct':q.correct_option, 'marks':q.marks, 'options':[q.option_1,q.option_2,q.option_3,q.option_4]} for q in questions]
    
    def post(self, quiz_id):
        data=request.get_json()
        print("DATA")
        print(data)
        question_statement=data.get('question')
        correct=data.get('correct')
        marks=data.get('marks')
        options=data.get('options')
        quiz_id=data.get('quiz_id')

        print(type(question_statement))

        if not question_statement or not marks or not correct:
            return {"error":"All Field are required"}, 400
        
        question=Questions.query.filter_by(question_statement=question_statement).first()

        if question:
            return {"error": "Question Exists"}, 401
        
        new_ques=Questions(quiz_id=quiz_id,
                           question_statement=question_statement,  
                           option_1=options[0] if options[0] else None, 
                           option_2=options[1] if options[1] else None, 
                           option_3=options[2] if options[2] else None, 
                           option_4=options[3] if options[3] else None,
                           correct_option=correct, 
                           marks=marks)
        db.session.add(new_ques)
        db.session.commit()

        return {'message': 'Question created successfully'}, 201

#--------------------------------------------HEIRARCHIAL VIEW RESOURCES--------------------------------------------
class SubjectDetail(Resource):
    method_decorators=[login_required]
    def get(self, sub_id):
        subject=Subject.query.filter_by(sub_id=sub_id).first()
        if not subject:
            return {"error":"Subject Not Found"}, 404
        return {"id": subject.sub_id, "name": subject.sub_name, "desc": subject.sub_desc}

class ChapterDetail(Resource):
    method_decorators=[login_required]
    def get(self, chap_id):
        chapter=Chapter.query.filter_by(chap_id=chap_id).first()
        if not chapter:
            return {"error":"Chapter Not Found"}, 404
        return {"id": chapter.chap_id, "name": chapter.chap_name, "desc": chapter.chap_desc}
    pass

class QuizDetail(Resource):
    method_decorators=[login_required]
    def get(self, quiz_id):
        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
        if not quiz:
            return {"error":"Quiz Not Found"}, 404
        return {"id": quiz.quiz_id, "name": quiz.quiz_name, "time":quiz.time, "date":quiz.date.isoformat()}

class QuestionDetail(Resource):
    pass

#--------------------------------------------MAIN ROUTES--------------------------------------------

@bp_main.route('/')
def home():
    return render_template('index.html')

@bp_main.route('/register')
def register():
    return render_template('register.html')

@bp_main.route('/login')
def login():
    return render_template('login.html')

@bp_main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login')) 

"""--------------------------------------------------------ADMIN ROUTES--------------------------------------------------------"""
@bp_main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin_templates/admin_dashboard.html")

#--------------------------------------------DB CREATES--------------------------------------------

@bp_main.route('/admin/subjects/create')
@login_required
@admin_required
def create_subject():
    return render_template('admin_templates/create_subject.html')

@bp_main.route('/admin/subjects/<int:sub_id>/chapters/create')
@login_required
@admin_required
def create_chapter(sub_id):
    return render_template('admin_templates/create_chapter.html')

@bp_main.route('/admin/chapters/<int:chap_id>/quizzes/create')
@login_required
@admin_required
def create_quiz(chap_id):
    return render_template('admin_templates/create_quiz.html')

@bp_main.route('/admin/quizzes/<int:quiz_id>/questions/create')
@login_required
@admin_required
def create_question(quiz_id):
    return render_template('admin_templates/create_question.html')



#--------------------------------------------DB UPDATES--------------------------------------------



#--------------------------------------------DB DELETES--------------------------------------------



#--------------------------------------------DB VIEWS--------------------------------------------
@bp_main.route('/admin/subjects/<int:sub_id>')
@login_required
@admin_required
def view_subject(sub_id): #Goes into Subject to view chapters and options
    return render_template('admin_templates/view_subject.html')

@bp_main.route('/admin/chapters/<int:chap_id>')
@login_required
@admin_required
def view_chapter(chap_id): #Goes into Chapter to view Quizzes and options
    return render_template('admin_templates/view_chapter.html')

@bp_main.route('/admin/quizzes/<int:quiz_id>')
@login_required
@admin_required
def view_quiz(quiz_id): #Goes into Chapter to view Quizzes and options
    return render_template('admin_templates/view_quiz.html')






@bp_main.route('/admin/chapters')
@login_required
@admin_required
def view_chapters():
    return "Chapters view"

@bp_main.route('/admin/quizzes')
@login_required
@admin_required
def view_quizzes():
    return "All Quizzes"

@bp_main.route('/admin/users')
@login_required
@admin_required
def view_users():
    return "All Users"




