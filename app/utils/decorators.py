from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user, login_required

def approved_login_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Redirect to login page if user is not authenticated
            return redirect(url_for('auth.login', next=request.url))
        
        # Add your custom checks here
        if current_user.role == 'pending':
            flash("Your account is not approved yet. Please contact the admin.")
            return redirect(url_for('auth.profile'))

        # You can add more conditions based on your user model, roles, etc.

        return f(*args, **kwargs)
    
    return login_required(decorated_function)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function


def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'manager':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function