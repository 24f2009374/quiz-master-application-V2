from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Api
from flask_login import LoginManager

db=SQLAlchemy()
login_manager=LoginManager()

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='8b027a0ff5f1320f'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quizmaster.db'
    

    db.init_app(app)
    api=Api(app)

    login_manager.init_app(app)
    login_manager.login_view="main.login"
    login_manager.login_message_category = "info"


    from app.routes import bp_main, Users, Register, Login
    from app.models import User

    app.register_blueprint(bp_main)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        create_admin_account()

    
    api.add_resource(Users, '/api/users/')
    api.add_resource(Register, '/api/register')
    api.add_resource(Login, '/api/login')


    
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
