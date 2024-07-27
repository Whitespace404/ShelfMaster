import os
import smtplib
import ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
PORT = 587
EMAIL = os.environ.get("EMAIL_ADRESS")
PASSWORD = os.environ.get("APP_PASSWORD_GMAIL")


def send_html_email(subject, receiver_email, html):
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL
    message["To"] = receiver_email
    message["Subject"] = subject

    part2 = MIMEText(html, "html")
    message.attach(part2)
    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, receiver_email, text)
