from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = b'1Fcxk9$kZm6c1pyfAXjjXrwn*egDFJl1Rqf9Ui!yN4$UbY%p0$'
    db_uri = 'postgresql://{}:{}@{}:5432/users'.format(
        os.getenv("db_root_username"),
        os.getenv("db_root_password"),
        os.getenv("postgres_host"),
        os.getenv("postgres_port")
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    db.init_app(app)

    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv("email_user") + "@gmail.com"
    app.config['MAIL_PASSWORD'] = os.getenv("email_password")
    app.config['MAIL_USE_TLS'] = True
    #app.config['MAIL_USE_SSL'] = True
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    db.create_all(app=app)

    # define how users are loaded
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for image display and labelling
    from .image_display import image_display as image_blueprint
    app.register_blueprint(image_blueprint)

    # blueprint for admin operations
    from .admin import admin_blueprint as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app
