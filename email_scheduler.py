# email_service.py
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_email(subject, recipient, body):
    print("Mail sending!!!")
    print(f"{recipient}","email_scheduler")
    msg = Message(subject,recipients=[recipient])
    msg.body = body
    with current_app.app_context():
        mail.send(msg)
