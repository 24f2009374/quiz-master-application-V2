from celery import Celery
from celery.schedules import crontab
from app.mail import send_basic_mail, send_html_mail
from app.models import User, Quiz, Scores, Chapter, Questions
from flask import render_template_string, current_app
from . import flask_app
from datetime import datetime, timedelta
import csv, os

def create_celery(app):
    celery=Celery(app.import_name)
    celery.conf.update(app.config)

    celery.conf.timezone = 'Asia/Kolkata'
    celery.conf.enable_utc = False

    celery.conf.beat_schedule = {
        "daily-reminders":{
            'task':'daily_reminder_all',
            'schedule':crontab(hour=7, minute=0),
        },
        "monthly-user-report":{
            'task':'monthly_report',
            'schedule':crontab(day_of_month=1, hour=7, minute=0)
        }
    }

    #USE FOR TEST AND SHOWING CELERY FUNCTIONAITY
    """celery.conf.beat_schedule = {
        'heartbeat-every-10s': {
        'task': 'debug_heartbeat',
        'schedule': 10.0,
        },
    }"""


    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task=ContextTask
    return celery

celery=create_celery(flask_app)

#------Tasks------
@celery.task(name='daily_reminder_all')
def daily_reminder_all():
    users=User.query.all()[1::]
    for u in users:
        send_basic_mail(
            subject="Daily Quiz Reminder",
            recipients=[u.email],
            body=f"Good Morning, {u.username},\nDon't Forget to take Quizzes today and have a great day ahead"
        )

@celery.task(name='registration_mail')
def registration_mail(email, username):
    send_basic_mail(
        subject="Welcome to QuizMaster!",
        recipients=[email],
        body=f"Hello {username}, thanks for joining QuizMaster. Good luck!"
    )

@celery.task(name='post_quiz_mail')
def post_quiz_mail(email, username, end_stamp, quiz_name):
    send_basic_mail(
        subject=f"Completion of Quiz: {quiz_name}",
        recipients=[email],
        body=f"Hello {username}, your attempt of quiz, {quiz_name}, has been submitted successfully.\nTime Stamp: {end_stamp}\nPlease refer to dashboard for Results"
    )
@celery.task(name='debug_heartbeat')
def debug_heartbeat():
    print("Heartbeat:", datetime.now())
    send_basic_mail(
        subject="TEST",
        recipients=["neal@neal.com"],
        body="SEND EVERY 10S"
    )

@celery.task(name='new_quiz_mail')
def new_quiz_mail(quiz_name, chap_name):
    users=User.query.all()[1::]
    for u in users:
        send_basic_mail(
            subject=f"New Quiz Made under Chapter {chap_name}",
            recipients=[u.email],
            body=f"Quiz is named {quiz_name}"
        )
    
@celery.task(name='monthly_report')
def monthly_report():
    print("[CELERY] Monthly Mail Worker Running [CELERY]")

    users=User.query.all()
    now=datetime.now()

    #The Dates below are used for the current month details for TESTING
    start_date=datetime(now.year, now.month if now.month>1 else 12, 1)
    end_date=datetime(now.year, now.month+1, 1)

    #For an ACTUAL monthly report, this is used.
    #start_date=datetime(now.year, now.month-1 if now.month>1 else 12, 1)
    #end_date=datetime(now.year, now.month, 1)


    print(start_date, end_date)
    for user in users:
        scores=Scores.query.filter(Scores.user_id==user.user_id, Scores.attempt_start>=start_date, Scores.attempt_end<end_date).all()
        if not scores:
            continue
            
        total_score=sum(s.total_scored for s in scores)
        avg_score=round(total_score/len(scores), 2)
        quiz_count=len(set(s.quiz_id for s in scores))

        quiz_details=[]
        for s in scores:
            quiz=Quiz.query.get(s.quiz_id)
            quiz_details.append({"name":quiz.quiz_name, "marks":s.total_scored})

            

        # HTML Format
        html_content=render_template_string("""
        <h2>Monthly Activity Report - {{month}}</h2>
        <p>Hello {{ name }},</p>
        <p>This is your Monthly Report for the month of {{month}}</p>
        <ul>
            <li><strong>Quizzes Taken: </strong>{{quizzes}}</li>
            <li><strong>Average Score: </strong>{{average}}</li>
        </ul>
        <h4>Individual Quiz Scores</h4>
        <ul>
            {% for q in quiz_details %}
                <li>{{q.name}} : {{ q.marks }}</li>
            {% endfor %}
        </ul>                                                                      
        """, name=user.username, quizzes=quiz_count, average=avg_score, quiz_details=quiz_details, month=start_date.strftime("%B %Y"))




        send_html_mail(subject=f"Your Monthly Report - {start_date.strftime('%B %Y')}", recipients=[user.email], html_body=html_content)
    

    print("[CELERY] Monthly Mail Worker COMPLETED [CELERY]\t[MAIL] Mail Successfully Sent [MAIL]")


@celery.task(name="csv_export")
def csv_export(user_id):
    print("[CELERY] CSV Export Worker Running [CELERY]")
    user=User.query.get(user_id)
    if not user:
        return
    
    scores=Scores.query.filter_by(user_id=user_id).all()
    result=[]
    for s in scores:
        quiz=Quiz.query.get(s.quiz_id)
        result.append({"quiz_id":s.quiz_id, "quiz_name":quiz.quiz_name, "date":s.attempt_end.strftime("%Y-%m-%d"), "score":s.total_scored})

    export_dir=os.path.join(current_app.root_path, "static", "exports")
    os.makedirs(export_dir, exist_ok=True)
    timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
    filename=f"user_{user_id}_export_{timestamp}.csv"
    filepath=os.path.join(export_dir, filename)

    with open(filepath, mode="w", newline="") as file:
        writer=csv.writer(file)
        writer.writerow(["Quiz ID", "Quiz Name", "Date", "Score"])
        for obj in result:
            writer.writerow([obj["quiz_id"], obj["quiz_name"], obj["date"], obj["score"]])

    send_basic_mail(subject="Your Quiz CSV Export is Ready", 
                    recipients=[user.email], 
                    body=f"Dear {user.username},\n\nYour quiz export is ready. You can download it here:\n"f"{current_app.config['BASE_URL']}/static/exports/{filename}")
    print("[CELERY] CSV Export Worker COMPLETED [CELERY]\t[MAIL] Mail Successfully Sent [MAIL]")
