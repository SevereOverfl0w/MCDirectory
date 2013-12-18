from flask.ext.mail import Message
from app import mail
from threading import Thread
def _send_async_email(msg):
    mail.send(msg)

def send_async_email(msg):
    thr = Thread(target = _send_async_email, args = [msg])
    thr.start()
