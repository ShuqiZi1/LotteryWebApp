# IMPORTS
import socket
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_ECHO'] = True

# initialise database
db = SQLAlchemy(app)


# HOME PAGE VIEW 123
@app.route('/')
def index():
    return render_template('index.html')

#ERROR PAGE VIEWS
@app.errorhandler(400)
def bad_request(error):
    return render_template('400.html'),400

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