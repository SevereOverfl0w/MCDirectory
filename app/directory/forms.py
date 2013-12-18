from flask.ext.wtf import Form
from wtforms import (
    TextField,
    SelectField,
    SubmitField,
    TextAreaField,
)

from ..user.constants import PROFESSIONS

sPROFESSIONS = PROFESSIONS.copy()
sPROFESSIONS[0] = 'Any'
class SearchForm(Form):
    id = SelectField(u'Profession', choices=sPROFESSIONS.items())
    q = TextField(u'', description='Search...')
    submit = SubmitField(u'Search')


