from app import bcrypt, db, app
import flask.ext.whooshalchemy as whooshalchemy
from flask.ext.login import UserMixin
from .constants import PROFESSIONS
import datetime
import urllib, hashlib

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    and_,
    func,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import case
from math import sqrt

class User(UserMixin, db.Model):
    __searchable__ = ['bio', 'email', 'skype', 'website', 'first_name', 'last_name']
    id = Column(Integer, primary_key=True)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    email = Column(String(255), nullable=False)
    _password = Column(String(64), nullable=False)
    activation_key = Column(String(64), nullable=True)
    _is_active = Column(Boolean, nullable=False, default=False)
    created = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow())

    ## Profile ##
    skype = Column(String(64), nullable=True)
    profession_id = Column(Integer, default=0, nullable=False)
    bio = Column(String(1024), nullable=True)
    website = Column(String(255), nullable=True)
    is_listed = Column(Boolean, default=True)

    ## Score ##
    ups = Column(Integer, default=0, nullable=False)
    downs = Column(Integer, default=0, nullable=False)
    votes_made = relationship('Vote', backref='voter', foreign_keys='[Vote.voter_id]', lazy='dynamic')
    voted_for = relationship('Vote', backref='user', foreign_keys='[Vote.user_id]', lazy='dynamic')


    ## Comments ##
    comments_made = relationship('Comment', backref='commenter', foreign_keys='[Comment.commenter_id]', lazy='dynamic')
    comments_for = relationship('Comment', backref='user', foreign_keys='[Comment.user_id]', lazy='dynamic', order_by='Comment.time.desc()')

    def has_upvoted(self, user):
        vote = self.votes_made.filter_by(voter_id=self.id, user_id=user.id, up=True).first()
        if vote:
            return True
        else:
            return False

    def has_downvoted(self, user):
        vote = self.votes_made.filter_by(voter_id=self.id, user_id=user.id, up=False).first()
        if vote:
            return True
        else:
            return False

    @hybrid_property
    def confidence(self):
        n = self.ups + self.downs
        if n == 0:
            return 0
        z = 1.0 # 85% confidence
        phat = float(self.ups) / n
        #print db.session.query(type(self).confidence).filter_by(id=self.id).one()[0] <-- Test
        return sqrt(phat+z*z/(2*n)-z*((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)

    @confidence.expression
    def confidence(cls):
        n = cls.ups + cls.downs
        z = 1.0
        phat = func.cast(cls.ups, Float) / n
        return case([(n == 0, 0)], else_=func.sqrt(phat+z*z/(2*n)-z*((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n))

    @property
    def profession(self):
        try:
            return PROFESSIONS[self.profession_id]
        except KeyError:
            return ""

    def is_active(self):
        return self._is_active

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(and_(
            cls.email == email, cls._is_active == True)).first()
        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def by_id(cls, id):
        return cls.query.filter_by(id=id).one()

    @classmethod
    def email_taken(cls, email):
        instance = cls.query.filter_by(email=email).first()
        if instance:
            return True
        return False

    def avatar_url(self, size):
        gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'s': str(size), 'default': 'retro'})
        return gravatar_url
whooshalchemy.whoosh_index(app, User)

class Vote(db.Model):
    id = Column(Integer, primary_key=True)
    voter_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    up = Column(Boolean, nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())

    @property
    def down(self):
        return not self.up

    @down.setter
    def down(self, value):
        self.up = not value

class Comment(db.Model):
    id = Column(Integer, primary_key=True)
    commenter_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    comment = Column(Text, nullable=False)
    stars = Column(Integer, nullable=False)
