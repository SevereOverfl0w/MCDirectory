from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate
from flask.ext.bcrypt import Bcrypt
from flask.ext.login import LoginManager
from flask.ext.principal import Principal
from flask.ext.mail import Mail
from flask.ext.assets import Environment, Bundle

app = Flask(__name__)
app.config.from_object('app.config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
lm = LoginManager(app)
lm.login_view = 'user.signin'
principal = Principal(app)
mail = Mail(app)
assets = Environment(app)

scss = Bundle('scss/foundation.scss', 'scss/normalize.scss', filters='scss',
              depends=('scss/foundation/*', 'scss/foundation/components/*'))
css = Bundle(scss, 'css/rateit/*.css', output='gen/all.css')
assets.register('css', css)

js = Bundle('js/vendor/jquery.js', 'js/foundation/foundation.js', 'js/foundation/*.*.js', 'js/jquery.rateit.min.js', output='all.js')
assets.register('js', js)

from .user import user
from .frontend import frontend
from .directory import directory

blueprints = ( user, frontend, directory )

for blueprint in blueprints:
    app.register_blueprint(blueprint)
