from celery import Celery
from celery.schedules import crontab
from app.mail import send_basic_mail
from app.models import User
from . import flask_app
from datetime import datetime, timedelta

def create_celery(app):
    celery=Celery(app.import_name)
    celery.conf.update(app.config)

    celery.conf.timezone = 'Asia/Kolkata'
    celery.conf.enable_utc = False

    celery.conf.beat_schedule = {
        "daily-reminders":{
            'task':'app.celery_app.daily_reminder_all',
            'schedule':crontab(hour=7, minute=0),
        },
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
@celery.task(name='app.tasks.daily_reminder_all')
def daily_reminder_all():
    users=User.query.all()[1::]
    for u in users:
        send_basic_mail(
            subject="Daily Quiz Reminder",
            recipients=[u.email],
            body=f"Good Morning, {u.username},\nDon't Forget to take Quizzes today and have a great day ahead"
        )

@celery.task(name='app.tasks.registration_mail')
def registration_mail(email, username):
    send_basic_mail(
        subject="Welcome to QuizMaster!",
        recipients=[email],
        body=f"Hello {username}, thanks for joining QuizMaster. Good luck!"
    )

@celery.task(name='app.tasks.post_quiz_mail')
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

    
        