import logging 
import requests
from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from flask_admin.menu import MenuLink
from config import Config
from app.utils.decorators import admin_required

# init SQLAlchemy
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    SLACK_WEBHOOK_URL = app.config['SLACK_WEBHOOK_URL']
    class SlackLogHandler(logging.Handler):
        def __init__(self, webhook_url):
            super().__init__()
            self.webhook_url = webhook_url

        def emit(self, record):
            log_entry = self.format(record)
            payload = {
                "text": log_entry
            }
            try:
                response = requests.post(self.webhook_url, json=payload)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                # Log an error if the Slack post fails
                print(f"Failed to send log to Slack: {e}")

    slack_handler = SlackLogHandler(SLACK_WEBHOOK_URL)
    slack_handler.setLevel(logging.INFO)  #specific to the slack handler
    flask_env = app.config['FLASK_ENV']
    if flask_env == 'production': 
        formatter = logging.Formatter('%(levelname)s [PROD] %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')
        slack_handler.setLevel(logging.WARNING)
    else:
        formatter = logging.Formatter('%(levelname)s [DEV] %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')
        slack_handler.setLevel(logging.WARNING)
        
    #formatter = logging.Formatter('%(levelname)s [%(flag)s] %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S')
    slack_handler.setFormatter(formatter)
    app.logger.addHandler(slack_handler)

    # Set the Flask app logger level
    app.logger.setLevel(logging.DEBUG) 

    #app.config['SECRET_KEY'] = SECRET_KEY # moved to config.py 
    #app.secret_key = APP_SECRET_KEY  # Needed for CSRF protection, also in config.py
    csrf = CSRFProtect(app)

    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    uri = app.config['DATABASE_URL']  #os.getenv("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri  #os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User
    from .models import UserView
    with app.app_context():
        db.create_all()
    
    fadmin = Admin(app, name="dbadmin", endpoint="dbadmin", template_mode='bootstrap3', url='/dbadmin')
    fadmin.add_link(MenuLink(name="Back to App", url="/manage"))
    fadmin.add_view(UserView(User, db.session, name='User'))

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # blueprint for non-auth parts of app
    from .main import main_bp
    app.register_blueprint(main_bp)

    # blueprint for admin routes
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    # Add the context processor
    @app.context_processor
    def inject_pending_actions():
        pending_user_count = User.query.filter_by(role='pending').count()
        return dict(pending_user_count=pending_user_count)

    return app

# Create app and get the application context
app = create_app()

for rule in app.url_map.iter_rules():
    print(rule)

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
    
# TODO Add a custom error handler for 404 errors
