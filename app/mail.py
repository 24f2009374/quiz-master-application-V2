from flask_mail import Mail, Message

mail=Mail()

def init_mail(app):
    app.config.update(
        MAIL_SERVER='localhost',
        MAIL_PORT=1025,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=False,
        MAIL_USERNAME='',        
        MAIL_PASSWORD='',
        MAIL_DEFAULT_SENDER=('QuizMaster', 'admin@quizmaster.com')
    )
    mail.init_app(app)

#Mails
def send_test_mail(subject:str, recipients: list[str], body: str):
    msg=Message(subject=subject, recipients=recipients, body=body)
    mail.send(msg)