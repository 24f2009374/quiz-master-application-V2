from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api
from flask_login import LoginManager
from flask_caching import Cache


db=SQLAlchemy()
login_manager=LoginManager()
cache=Cache()

def create_app():
    app=Flask(__name__)

    app.config['SECRET_KEY']='8b027a0ff5f1320f'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quizmaster.db'

    app.config['CACHE_TYPE']='RedisCache'
    app.config['CACHE_REDIS_HOST']='localhost'
    app.config['CACHE_REDIS_PORT']=6379
    app.config['CACHE_DEFAULT_TIMEOUT']=300  

    cache.init_app(app)
    db.init_app(app)
    api=Api(app)

    login_manager.init_app(app)
    login_manager.login_view="main.login"
    login_manager.login_message_category = "info"


    from app.routes import bp_main, Users, Register, Login, DB_Subjects, DB_Questions, DB_Chapters, DB_Quizzes, QuizDetail, ChapterDetail, SubjectDetail, QuestionDetail, Enrollment, AllQuiz, AllChapter, Preparation, AttemptQuiz, SubmitQuiz
    from app.models import User

    app.register_blueprint(bp_main)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        create_admin_account()

    
    api.add_resource(Users, '/api/users/', '/api/users/<int:user_id>')
    api.add_resource(Register, '/api/register')
    api.add_resource(Login, '/api/login')

    api.add_resource(DB_Subjects, '/api/subjects/crud', '/api/subjects/crud/<int:sub_id>')
    api.add_resource(SubjectDetail, '/api/subjects/<int:sub_id>')

    api.add_resource(DB_Chapters, '/api/subjects/<int:sub_id>/chapters/crud', '/api/subjects/<int:sub_id>/chapters/crud/<int:chap_id>')
    api.add_resource(ChapterDetail, '/api/chapters/<int:chap_id>')
    api.add_resource(AllChapter, '/api/chapters')

    api.add_resource(DB_Quizzes, '/api/chapters/<int:chap_id>/quizzes/crud', '/api/chapters/<int:chap_id>/quizzes/crud/<int:quiz_id>')
    api.add_resource(QuizDetail, '/api/quizzes/<int:quiz_id>')
    api.add_resource(AllQuiz, '/api/quizzes')

    api.add_resource(DB_Questions, '/api/quizzes/<int:quiz_id>/questions/crud', '/api/quizzes/<int:quiz_id>/questions/crud/<int:q_id>')
    api.add_resource(QuestionDetail, '/api/questions/<int:q_id>')

    api.add_resource(Enrollment, '/api/enrolls/crud/<int:user_id>', '/api/enrolls/crud')
    api.add_resource(Preparation, '/api/prepare/<int:quiz_id>')
    api.add_resource(AttemptQuiz, '/api/attempt')
    api.add_resource(SubmitQuiz, '/api/attempt/submit')



    
    return app

def create_admin_account():
    from app.models import User
    admin=User.query.filter_by(role='admin').first()
    if not admin:
        hashed=generate_password_hash('admin123')
        admin=User(username='admin', email='admin@quizmaster.com', password_hash=hashed, role='admin')
        db.session.add(admin) 
        db.session.commit()
        print("admin created and indexed with username (admin@quizmaster.com) and password (admin123)")
