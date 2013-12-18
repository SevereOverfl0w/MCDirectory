from flask.ext.wtf import Form
from wtforms import (
    TextField,
    SelectField,
    SubmitField,
    PasswordField,
    DateTimeField,
    BooleanField,
    TextAreaField,
    ValidationError,
)

from flask.ext.wtf.html5 import EmailField, URLField

from wtforms.validators import (
    Required,
    Length,
    EqualTo,
)

from .constants import PROFESSIONS
from .models import User

class PasswordMixin(object):
    password = PasswordField(u'Password', [Required(), Length(8, 255)])

class PasswordAgainMixin(object):
    password_again = PasswordField(u'Password (again)', [EqualTo('password')])

class SignupForm(Form, PasswordMixin, PasswordAgainMixin):
    first_name = TextField(u'First name', [Required(), Length(1, 40)])
    last_name = TextField(u'Last name', [Required(), Length(1, 40)])
    is_listed = BooleanField(u'List me in the directory', default=True)
    email = EmailField(u'Email', [Required(), Length(5, 255)])
    submit = SubmitField(u'Sign up')

    def validate_email(self, field):
        if User.email_taken(field.data):
            raise ValidationError(u'This email is already taken')

class SigninForm(Form, PasswordMixin):
    email = EmailField(u'Email', [Required()])
    remember = BooleanField(u'Remember me')
    submit = SubmitField(u'Sign in')

    def validate_email(self, field):
        if not User.email_taken(field.data):
            raise ValidationError(u'No such email exists')

class ChangePasswordForm(Form, PasswordMixin, PasswordAgainMixin):
    old_password = PasswordField(u'Old Password', [Required()])
    submit = SubmitField(u'Change')

    def validate_old_password(self, field):
        if not User.check_password(field.data):
            raise ValidationError(u'Your old password is wrong')

class RecoverPasswordForm(Form):
    email = EmailField(u'Email', [Required()])
    submit = SubmitField(u'Recover')

    def validate_email(self, field):
        if not User.email_taken(field.data):
            raise ValidationError(u'Email isn\'t registered')

class SetPasswordForm(Form, PasswordMixin, PasswordAgainMixin):
    submit = SubmitField(u'Change')

class ProfileForm(Form):
    skype = TextField(u'Skype', [Length(0, 64)])
    profession_id = SelectField(u'Profession', choices = PROFESSIONS.items(), coerce=int)
    bio = TextAreaField(u'Bio', [Length(0, 1024)])
    website = URLField(u'Website', [Length(0, 255)])
    is_listed = BooleanField(u'List me in the directory')
    submit = SubmitField(u'Update')

stars = [(0, 'Horrific'), (1, 'Bad'), (2, 'Poor'), (3, 'OK'), (4, 'Good'), (5, 'Great')]
class CommentForm(Form):
    comment = TextAreaField(u'Comment', [Required()])
    stars = SelectField(u'Rating', choices=stars, coerce=int)
    submit = SubmitField(u'Comment')
