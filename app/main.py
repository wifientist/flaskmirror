from flask import Blueprint, render_template, current_app
from flask_login import current_user
from .utils.decorators import approved_login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated: current_app.logger.info(f'User {current_user.email} accessed the index page')
    else: current_app.logger.info('An anonymous user accessed the index page')

    return render_template('index.html')

@main_bp.route('/help')
@approved_login_required
def help():
    current_app.logger.info(f'User {current_user.email} accessed the help page')
    return render_template('help.html')