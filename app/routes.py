from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db, Api, cache
from app.models import User, Subject, Chapter, Quiz, Questions, Scores, Enrollments
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from flask_login import login_required, current_user, logout_user, login_user, login_manager
import datetime
from dateutil.parser import parse
from app.mail import send_basic_mail
from sqlalchemy import func, desc


bp_main=Blueprint('main',__name__)

"""
Start Redis: sudo service redis-server start  
View Keys: redis-cli; keys *  

Terminal 1: redis-server #6379
Terminal 2: celery -A app.celery_app worker --loglevel=info
Terminal 3: celery -A app.celery_app beat --loglevel info
"""
#--------------------------------------------MAIL TESTS--------------------------------------------
@bp_main.route('/send-basic-mail')
@login_required
def test_mail():
    send_basic_mail(
        subject="Hello from QuizMaster",
        recipients=["neal@neal.com"],
        body="This is just a test email via MailHog."
    )
    return "Mail sent! Check MailHog."

@bp_main.route('/admin/monthly-mail')
@login_required
def monthly_mail():
    from app.celery_app import monthly_report
    monthly_report()
    print("[FLASK] Prompted, Check Workers, Beats and MailHog [FLASK]")
    return "Mail sent! Check MailHog."
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

class CurrentUser(Resource):
    @login_required
    @cache.cached(timeout=900, key_prefix='current_user')
    def get(self):
        return {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email
        }

class AllUsers(Resource):
    @cache.cached(timeout=900, key_prefix='all_users')
    def get(self):
        users=User.query.all()[1:]
        res=[{'username':u.username, 'email':u.email, 'user_id':u.user_id} for u in users]
        return res, 200
    
class Users(Resource):
    def get(self, user_id):
        u=User.query.filter_by(user_id=user_id).first()
        return {'username':u.username, 'email':u.email, 'user_id':u.user_id}, 200
    
class Register(Resource):
    def post(self):
        from app.celery_app import registration_mail
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

        # Celery
        registration_mail.delay(new_user.email, new_user.username)

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
    
class AdminSearch(Resource):
    method_decorators=[login_required, admin_required]
    @cache.cached(timeout=60, key_prefix='admin_search_result', query_string=True)
    def get(self):
        query=request.args.get('q', '').strip().lower()
        if not query:
            return {"error": "Empty query"}, 400
        
        # User, Subject, Chapter, Quiz, Questions, Scores, Enrollments
        
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()

        subs = Subject.query.filter((Subject.sub_name.ilike(f"%{query}%")) | (Subject.sub_desc.ilike(f"%{query}%"))).all()

        chaps = Chapter.query.filter((Chapter.chap_name.ilike(f"%{query}%")) |(Chapter.chap_desc.ilike(f"%{query}%"))).all()

        quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{query}%")).all()

        search_result={
            "users":[{'username':u.username, 'email':u.email, 'user_id':u.user_id} for u in users] if users else [],
            "subjects":[{'id':s.sub_id, 'name':s.sub_name, 'desc':s.sub_desc} for s in subs] if subs else [],
            "chapters":[{'id':c.chap_id, 'name':c.chap_name, 'desc':c.chap_desc, 'parent':c.subject_id} for c in chaps] if chaps else [],
            "quizzes":[{'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.strftime('%Y-%m-%d'), 'parent':q.chapter_id} for q in quizzes] if quizzes else []
        }


        return search_result

class UserSearch(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=60, key_prefix='user_search_result', query_string=True)
    def get(self):
        query = request.args.get('q', '').strip().lower()
        if not query:
            return {"error": "Empty query"}, 400
        
        # May add heirarchial Quiz View for Users

        quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f"%{query}%")).all()

        search_result={
            "quizzes":[{'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.strftime('%Y-%m-%d'), 'parent':q.chapter_id} for q in quizzes] if quizzes else []
        }


        return search_result

class ChartGeneral(Resource):
    method_decorators=[login_required]
    def get(self):
        context=request.args.get('ctx', '').strip()
        if(context=="TopUsers"):
            latests=db.session.query(Scores.user_id, Scores.quiz_id, db.func.max(Scores.attempt_end).label("latest")).group_by(Scores.user_id, Scores.quiz_id).subquery()

            joined_set=db.session.query(Scores).join(latests, (Scores.user_id == latests.c.user_id) &(Scores.quiz_id == latests.c.quiz_id) &(Scores.attempt_end == latests.c.latest)).subquery()

            total_scores=db.session.query(User.username, db.func.sum(joined_set.c.total_scored).label('total_marks')
                                      ).join(User, User.user_id == joined_set.c.user_id
                                             ).group_by(User.username
                                                ).order_by(db.desc('total_marks')
                                                    ).limit(3).all()
        
            result={"labels": [r.username for r in total_scores], "data": [r.total_marks for r in total_scores]}

            return jsonify(result)
        elif(context=="TopAttempts"):
            attempts=db.session.query(User.user_id, User.username, func.count(Scores.sid).label("attempt_count")).join(Scores, Scores.user_id == User.user_id).group_by(User.user_id, User.username).order_by(desc("attempt_count")).all()

            result={
                "labels":[r.username for r in attempts][:6], "data":[r.attempt_count for r in attempts][:6]
            }
            return jsonify(result)

        elif(context=="TopQuizzes"):
            attempts=db.session.query(Quiz.quiz_id, Quiz.quiz_name, func.count(Scores.sid).label("attempt_count")).join(Scores, Scores.quiz_id == Quiz.quiz_id).group_by(Quiz.quiz_id, Quiz.quiz_name).order_by(desc("attempt_count")).all()

            result={
                "labels":[r.quiz_name for r in attempts][:6], "data":[r.attempt_count for r in attempts][:6]
            }
            return jsonify(result)
        elif(context=="userVAvg"):
            quiz_id=request.args.get('quiz_id')
            user_scores=db.session.query(Scores.total_scored).filter_by(user_id=current_user.user_id, quiz_id=quiz_id).order_by(Scores.attempt_start.asc()).all()

            user_score_list=[score[0] for score in user_scores]

            all_scores=db.session.query(Scores.user_id, Scores.total_scored, Scores.attempt_start).filter_by(quiz_id=quiz_id).order_by(Scores.user_id, Scores.attempt_start).all()

            from collections import defaultdict

            user_atts=defaultdict(list)
            for uid, marks, _ in all_scores:
                user_atts[uid].append(marks)

            max_attempts = max(len(attempts) for attempts in user_atts.values())

            avgs=[]
            for i in range(max_attempts):
                att_marks=[]
                for att in user_atts.values():
                    if i<len(att):
                        att_marks.append(att[i])
                if att_marks:
                    avgs.append(sum(att_marks)/len(att_marks))
                else:
                    avgs.append(None)
            return jsonify({
                "user_scores":user_score_list, "avg_scores":avgs
            })
        elif(context=="CSV"):
            from app.celery_app import csv_export
            csv_export.delay(current_user.user_id)
            return {"message": "Export started"},202
        
#--------------------------------------------CRUD RESOURCES--------------------------------------------

class DB_Subjects(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix='all_subjects')
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
        cache.delete('all_subjects')

        return {'message': 'Subject created successfully'}, 201

    def put(self):
        data=request.get_json()
        sub_name=data.get('name')
        sub_desc=data.get('desc')
        sub_id=data.get('sub_id')

        sub=Subject.query.filter_by(sub_id=sub_id).first()

        if not sub:
            return {"error":"Subject Not Found"}, 404
        
        sub.sub_name=sub_name
        sub.sub_desc=sub_desc

        db.session.commit()
        cache.delete('all_subjects')

        return {'message': 'Subject updated successfully'}, 200
    
    def delete(self, sub_id):

        subject=Subject.query.filter_by(sub_id=sub_id).first()
        if not subject:
            return {'error': 'Subject not found'}, 404

        chapters=Chapter.query.filter_by(subject_id=sub_id).all()
        for chap in chapters:
            quizzes=Quiz.query.filter_by(chapter_id=chap.chap_id).all()
            for quiz in quizzes:
                Questions.query.filter_by(quiz_id=quiz.quiz_id).delete()
                Enrollments.query.filter_by(quiz_id=quiz.quiz_id).delete()
                Scores.query.filter_by(quiz_id=quiz.quiz_id).delete()

                db.session.delete(quiz)
            db.session.delete(chap)
        db.session.delete(subject)

        db.session.commit()
        cache.delete('all_subjects')
        return {'message': 'Subject and all related data deleted successfully.'}, 200
   
class DB_Chapters(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix=lambda: f"child_chaps_{request.view_args['sub_id']}")
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
        cache.delete(f"child_chaps_{sub_id}")
        cache.delete('all_chap')

        return {'message': 'Chapter created successfully'}, 201
    
    def put(self, sub_id):
        data=request.get_json()
        chap_name=data.get('name')
        chap_desc=data.get('desc')
        chap_id=data.get('chap_id')

        chapter=Chapter.query.filter_by(chap_id=chap_id).first()

        if not chapter:
            return {"error":"Chapter Not Found"}, 404
        
        chapter.chap_name=chap_name
        chapter.chap_desc=chap_desc
        db.session.commit()
        cache.delete(f"child_chaps_{sub_id}")
        cache.delete('all_chap')
        return {'message': 'Chapter updated successfully'}, 200
    
    def delete(self, sub_id, chap_id):
        chapter=Chapter.query.filter_by(chap_id=chap_id).first()

        quizzes=Quiz.query.filter_by(chapter_id=chap_id).all()
        for quiz in quizzes:
            Questions.query.filter_by(quiz_id=quiz.quiz_id).delete()
            Enrollments.query.filter_by(quiz_id=quiz.quiz_id).delete()
            Scores.query.filter_by(quiz_id=quiz.quiz_id).delete()

            db.session.delete(quiz)

        db.session.delete(chapter)
        db.session.commit()
        cache.delete(f"child_chaps_{sub_id}")
        cache.delete('all_chap')
        return {'message': 'Chapter and all related data deleted successfully.'}, 200

class DB_Quizzes(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix=lambda: f"child_quiz_{request.view_args['chap_id']}")
    def get(self, chap_id):
        quizzes=Quiz.query.filter_by(chapter_id=chap_id)
        
        return [{'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.strftime('%Y-%m-%d'), 'parent':q.chapter_id} for q in quizzes]
    
    def post(self, chap_id):
        from app.celery_app import new_quiz_mail
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
        cache.delete(f"child_quiz_{chap_id}")
        cache.delete('all_quiz')

        new_quiz_mail.delay(new_quiz.quiz_name, Chapter.query.filter_by(chap_id=chap_id).first().chap_name)

        return {'message': 'Quiz created successfully'}, 201
    
    def put(self, chap_id):
        data=request.get_json()
        name=data.get('name')
        time=data.get('time')
        date_str=data.get('date')
        quiz_id=data.get('quiz_id')

        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()

        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        if not quiz:
            return {"error":"Quiz Not Found"}, 404
        
        quiz.quiz_name=name
        quiz.time=time
        quiz.date=date_obj
        db.session.commit()
        cache.delete(f"child_quiz_{chap_id}")
        cache.delete('all_quiz')
        return {'message': 'Quiz updated successfully'}, 200
    
    def delete(self, chap_id, quiz_id):
        

        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
        Questions.query.filter_by(quiz_id=quiz.quiz_id).delete()
        Enrollments.query.filter_by(quiz_id=quiz.quiz_id).delete()
        Scores.query.filter_by(quiz_id=quiz.quiz_id).delete()
        db.session.delete(quiz)
        db.session.commit()
        cache.delete(f"child_quiz_{chap_id}")
        cache.delete('all_quiz')

        return {'message': 'Quiz and all related data deleted successfully.'}, 200

class DB_Questions(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=30, key_prefix=lambda: f"quiz_questions_{request.view_args['quiz_id']}")
    def get(self, quiz_id):
        questions=Questions.query.filter_by(quiz_id=quiz_id)
        
        return [{'id':q.qid,'statement':q.question_statement, 'parent':q.quiz_id, 'correct':q.correct_option, 'marks':q.marks, 'options':[q.option_1,q.option_2,q.option_3,q.option_4]} for q in questions]
    
    def post(self, quiz_id):
        data=request.get_json()
        question_statement=data.get('question')
        correct=data.get('correct')
        marks=data.get('marks')
        options=data.get('options')
        quiz_id=data.get('quiz_id')

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
        cache.delete(f"quiz_questions_{quiz_id}")
        return {'message': 'Question created successfully'}, 201
    
    def put(self, quiz_id):
        data=request.get_json()
        question_statement=data.get('question')
        correct=data.get('correct')
        marks=data.get('marks')
        options=data.get('options')
        qid=data.get('q_id')
        ques=Questions.query.filter_by(qid=qid).first()

        if not ques:
            return {"error":"Question Not Found"}, 404
        
        ques.question_statement=question_statement
        ques.quiz_id=quiz_id
        ques.marks=marks
        ques.correct_option=correct
        ques.option_1=options[0] if options[0] else None
        ques.option_2=options[1] if options[1] else None 
        ques.option_3=options[2] if options[2] else None 
        ques.option_4=options[3] if options[3] else None
        db.session.commit()
        cache.delete(f"quiz_questions_{quiz_id}")
        return {'message': 'Question updated successfully'}, 200

    def delete(self, quiz_id, q_id):

        Questions.query.filter_by(qid=q_id).delete()
        db.session.commit()
        cache.delete(f"quiz_questions_{quiz_id}")
        return {'message': 'Question deleted successfully.'}, 200

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
        return {"id": chapter.chap_id, "name": chapter.chap_name, "desc": chapter.chap_desc, "parent":chapter.subject_id}
    pass

class QuizDetail(Resource):
    method_decorators=[login_required]
    def get(self, quiz_id):
        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
        if not quiz:
            return {"error":"Quiz Not Found"}, 404
        return {"id": quiz.quiz_id, "name": quiz.quiz_name, "time":quiz.time, "date":quiz.date.strftime('%Y-%m-%d'), "parent":quiz.chapter_id}
    
class QuestionDetail(Resource):
    method_decorators=[login_required]
    def get(self, q_id):
        q=Questions.query.filter_by(qid=q_id).first()
        if not q:
            return {"error":"Question Not Found"}, 404
        return {'id':q.qid,'statement':q.question_statement, 'parent':q.quiz_id, 'correct':q.correct_option, 'marks':q.marks, 'options':[q.option_1,q.option_2,q.option_3,q.option_4]}

class AllQuiz(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix='all_quiz')
    def get(self):
        quizzes=Quiz.query.all()
        res=[]
        for q in quizzes:
            chap=Chapter.query.filter_by(chap_id=q.chapter_id).first()
            ques=Questions.query.filter_by(quiz_id=q.quiz_id).all()
            total=0
            for que in ques:
                total+=que.marks
            res.append({'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.strftime('%Y-%m-%d'), 'parent':chap.chap_name, 'total':total})
        return res
    
class AllChapter(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix='all_chap')
    def get(self):
        chaps=Chapter.query.all()
        res=[]
        for c in chaps:
            p_sub=Subject.query.filter_by(sub_id=c.subject_id).first()
            res.append({'id':c.chap_id, 'name':c.chap_name, 'desc':c.chap_desc, 'parent':p_sub.sub_name})
 
        return res

#--------------------------------------------USER RESOURCES--------------------------------------------
class Enrollment(Resource):
    method_decorators=[login_required]
    @cache.cached(timeout=900, key_prefix='enroll')
    def get(self, user_id):
        enrolls=Enrollments.query.filter_by(user_id=user_id)
        quizzes=current_user.enrolled_quizzes

        return [{'id':q.quiz_id, 'name':q.quiz_name, 'time':q.time, 'date':q.date.strftime('%Y-%m-%d'), 'parent':q.chapter_id} for q in quizzes]

    def post(self):
        data=request.get_json()

        user_id=data.get("user_id")
        quiz_id=data.get("quiz_id")

        enroll=Enrollments.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
        if enroll:
            return {"error":"You have Already Enrolled to this Quiz"}, 409

        new_enroll=Enrollments(user_id=user_id, quiz_id=quiz_id)
        db.session.add(new_enroll)
        db.session.commit()
        cache.delete('enroll')
        return {"message": "Successfully Enrolled"}, 201
        
class Preparation(Resource):
    method_decorators=[login_required]
    def get(self, quiz_id):
        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
        user_id=current_user.user_id
        if not quiz:
            return {"error":"Quiz Not Found"}, 404
        questions=Questions.query.filter_by(quiz_id=quiz_id)
        marks=0
        for q in questions:
            marks+=q.marks
        chap_name=Chapter.query.filter_by(chap_id=quiz.chapter_id).first().chap_name

        scores=Scores.query.filter_by(quiz_id=quiz_id, user_id=user_id).all()
        counts=0
        for _ in scores:
            counts+=1


        return {"id": quiz.quiz_id, "name": quiz.quiz_name, "time":quiz.time, "date":quiz.date.strftime('%Y-%m-%d'), "parent":chap_name, 'total':marks, 'count':counts}

class AttemptQuiz(Resource):
    #packages questions excluding correct option and also sends the quiz time which will be used in timer
    method_decorators=[login_required]
    def get(self, quiz_id):
        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first()
        if not quiz:
            return {"error": "Quiz not found"}, 404
        
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        result=[]
        for q in questions:
            options=q.get_options()
            result.append({"id":q.qid, "question":q.question_statement, "options":options, "marks":q.marks})
        return {"questions": result, "quiz_time": quiz.time}, 200

class SubmitQuiz(Resource):
    method_decorators=[login_required]
    def post(self):
        from app.celery_app import post_quiz_mail
        data=request.get_json()
        quiz_id = data.get('quiz_id')
        answers = data.get('answers')
        att_start = parse(data.get('att_start'))
        att_end = parse(data.get('att_end'))
        user_id = current_user.user_id

        quiz=Quiz.query.filter_by(quiz_id=quiz_id).first().quiz_name

        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        total_score=0

        for q,slct in zip(questions, answers):
            if slct is not None and slct==q.correct_option:
                total_score+=q.marks

        score=Scores(user_id=user_id, quiz_id=quiz_id, attempt_start=att_start, attempt_end=att_end, total_scored=total_score)
        db.session.add(score)
        db.session.commit()

        # Celery
        post_quiz_mail.delay(current_user.email, current_user.username, att_end, quiz)

        return {'message': 'Quiz Successfully Submitted'}, 201

class Score(Resource):
    method_decorators=[login_required]
    def get(self, quiz_id):
        scores=Scores.query.filter_by(quiz_id=quiz_id, user_id=current_user.user_id).all()
        questions=Questions.query.filter_by(quiz_id=quiz_id).all()
        marks=0
        for q in questions:
            marks+=q.marks
        return [{'scored':s.total_scored, 'start':s.attempt_start.isoformat(), 'end':s.attempt_end.isoformat(), 'total':marks, 'id':s.sid} for s in scores]

class UserScores(Resource):
    method_decorators=[login_required]
    def get(self, user_id):
        user=User.query.filter_by(user_id=user_id).first()
        scores=Scores.query.filter_by(user_id=user_id).all()
        res=[]
        for s in scores:
            quiz=Quiz.query.filter_by(quiz_id=s.quiz_id).first()
            questions=Questions.query.filter_by(quiz_id=quiz.quiz_id).all()
            marks=0
            for q in questions:
                marks+=q.marks
            res.append({'scored':s.total_scored, 'start':s.attempt_start.isoformat(), 'end':s.attempt_end.isoformat(), 'total':marks, 'id':s.sid, 'quiz':quiz.quiz_name})
        return res, 200

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
    cache.delete('current_user')
    cache.delete('enroll')
    return redirect(url_for('main.login')) 

"""--------------------------------------------------------ADMIN ROUTES--------------------------------------------------------"""
@bp_main.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin_templates/admin_dashboard.html")

@bp_main.route('/admin/analytics')
@login_required
@admin_required
def analytics():
    return render_template("admin_templates/analytics.html")

@bp_main.route('/admin/chapters')
@login_required
@admin_required
def all_chapter():
    return render_template("admin_templates/all_chapters.html")

@bp_main.route('/admin/quizzes')
@login_required
@admin_required
def all_quiz():
    return render_template("admin_templates/all_quiz.html")

@bp_main.route('/admin/view_users')
@login_required
@admin_required
def all_user():
    return render_template("admin_templates/all_user.html")

@bp_main.route('/admin/search/results')
@login_required
@admin_required
def admin_search_result():
    return render_template("admin_templates/admin_search.html")

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

@bp_main.route('/admin/subjects/update/<int:sub_id>')
@login_required
@admin_required
def update_subject(sub_id):
    return render_template('admin_templates/update_subject.html')

@bp_main.route('/admin/chapters/update/<int:chap_id>')
@login_required
@admin_required
def update_chapter(chap_id):
    return render_template('admin_templates/update_chapter.html')

@bp_main.route('/admin/quizzes/update/<int:quiz_id>')
@login_required
@admin_required
def update_quiz(quiz_id):
    return render_template('admin_templates/update_quiz.html')

@bp_main.route('/admin/questions/update/<int:q_id>')
@login_required
@admin_required
def update_question(q_id):
    return render_template('admin_templates/update_question.html')

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

@bp_main.route('/admin/users/')
@login_required
@admin_required
def view_users(): 
    return render_template('admin_templates/view_users.html')

@bp_main.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def view_user_data(user_id): #Goes into Chapter to view Quizzes and options
    return render_template('admin_templates/view_user_data.html')

"""--------------------------------------------------------USER ROUTES--------------------------------------------------------"""
@bp_main.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template("user_templates/user_dashboard.html")

@bp_main.route('/user/to_enroll')
@login_required
def to_enroll():
    return render_template("user_templates/enroll_quiz.html")

@bp_main.route('/user/preparation/<int:quiz_id>')
@login_required
def prep(quiz_id):
    return render_template("user_templates/prep.html")

@bp_main.route('/user/attempt/<int:quiz_id>')
@login_required
def attempt(quiz_id):
    return render_template("user_templates/AttemptQuiz.html")

@bp_main.route('/user/quiz/thank')
@login_required
def thank():
    return render_template("user_templates/quiz_thank.html")

@bp_main.route('/user/scores/<int:quiz_id>')
@login_required
def score(quiz_id):
    return render_template("user_templates/user_score.html")

@bp_main.route('/user/search/results')
@login_required
def user_search_results():
    return render_template("user_templates/user_search.html")

@bp_main.route('/user/scores/all')
@login_required
def user_scores_all():
    return render_template("user_templates/user_all_scores.html")



