# test_email.py
from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject="HealthTrack AI - Test Email",
            recipients=["your_personal_email@gmail.com"],  # Change to your email
            sender=app.config['MAIL_DEFAULT_SENDER'],
            body="This is a test email from HealthTrack AI. Your email configuration is working!"
        )
        mail.send(msg)
        print(f"✅ Test email sent successfully from {app.config['MAIL_DEFAULT_SENDER']}")
        print(f"   Check your inbox at your_personal_email@gmail.com")
    except Exception as e:
        print(f"❌ Failed: {e}")