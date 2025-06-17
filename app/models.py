from app import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash




class User(db.Model, UserMixin):
    user_id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    username=db.Column(db.String(150), unique=True, nullable=False)
    email=db.Column(db.String(150), unique=True, nullable=False)
    password_hash=db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def is_admin(self):
        return self.role=='admin'
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role
        }
    
    def __repr__(self):
        return f"Users(username={self.username}, email={self.email})"
    
    """@login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))"""
    
    enrolled_quizzes = db.relationship('Quiz', secondary='enrollments', back_populates='enrolled_users') #relates to quiz and enrolled_users
    
class Subject(db.Model):
    sub_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    sub_name=db.Column(db.String(150), unique=True, nullable=False)
    sub_desc=db.Column(db.Text)


class Chapter(db.Model):
    chap_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    chap_name=db.Column(db.String(150), unique=True, nullable=False)
    chap_desc=db.Column(db.Text)
    subject_id=db.Column(db.Integer, db.ForeignKey('subject.sub_id'), nullable=False)

class Quiz(db.Model):
    quiz_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_name=db.Column(db.String(150), unique=True, nullable=False)
    chapter_id=db.Column(db.Integer, db.ForeignKey('chapter.chap_id'), nullable=False)
    date=db.Column(db.DateTime)
    time=db.Column(db.Integer) #mins

    enrolled_users = db.relationship('User', secondary='enrollments', back_populates='enrolled_quizzes') #relates to usrs and enrolled quizzes 


class Questions(db.Model):
    qid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    question_statement=db.Column(db.Text, nullable=False)
    option_1=db.Column(db.String(255), nullable=True)
    option_2=db.Column(db.String(255), nullable=True)
    option_3=db.Column(db.String(255), nullable=True)
    option_4=db.Column(db.String(255), nullable=True)
    correct_option=db.Column(db.Integer, nullable=False)
    marks=db.Column(db.Integer, nullable=False)


    def get_options(self):
        return [opt for opt in [self.option_1, self.option_2, self.option_3, self.option_4] if opt]

class Scores(db.Model):
    sid=db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    attempt_stamp=db.Column(db.Integer, nullable=False)
    total_scored=db.Column(db.Integer, nullable=False)

class Enrollments(db.Model): #when enro button is pressed on quiz, it adds a student and quiz id related entry to the table and is used to display the quiz for the user
    quiz_id=db.Column(db.Integer, db.ForeignKey('quiz.quiz_id'), nullable=False, primary_key=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False, primary_key=True)