SECRET_KEY = 'changeme'

import os
basedir = os.path.abspath( os.path.join(os.path.dirname(__file__), '../'))

SQLALCHEMY_DATABASE_URI = 'postgresql://overfl0w@localhost:5432/minecraftdb'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

MAIL_SERVER = 'smtp.mandrillapp.com'
MAIL_PORT = 587
MAIL_USERNAME = 'overfl0w@narna.co'
MAIL_PASSWORD = 'lolyeahk'
MAIL_DEFAULT_SENDER = MAIL_USERNAME

ADMINS = ['overfl0w@narna.co']
