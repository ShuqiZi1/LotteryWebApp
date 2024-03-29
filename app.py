# IMPORTS
import logging
import socket
from flask import Flask, render_template, session, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_talisman import Talisman
import ssl


# LOGGING
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()

# create file handler to log security messages to file
fh = logging.FileHandler('lottery.log', 'a')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

# add handlers to root logger
logger = logging.getLogger('')
logger.propagate = False
if not logger.handlers:
    logger.addHandler(fh)


# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_ECHO'] = True


# initialise database
db = SQLAlchemy(app)

# Security Headers
csp = {
    'default-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'
    ],
    'script-src': [
        '\'self\'',
        '\'unsafe-inline\''
    ]
}
talisman = Talisman(app, content_security_policy=csp)


# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# HOME PAGE VIEW
@app.route('/')
def index():
    print(request.headers)
    return render_template('index.html')


# ERROR PAGE VIEWS
@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'), 400

@app.errorhandler(403)
def page_forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.errorhandler(503)
def service_unavailable(error):
    return render_template('503.html'), 503


if __name__ == "__main__":

    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # avoid unauthorized user access certain pages
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    # search database and return the user matched ID
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from lottery.views import lottery_blueprint

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(lottery_blueprint)

    app.run(host=my_host, port=free_port, debug=True)
