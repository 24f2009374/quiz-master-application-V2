from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='8b027a0ff5f1320f'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///quizmaster.db'

    db.init_app(app)

    from app.routes import bp_main
    app.register_blueprint(bp_main)

    with app.app_context():
        db.create_all()
        #create_admin_account()
    
    return app