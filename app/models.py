from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Enum, event
from . import db
from datetime import datetime
from flask import redirect, url_for
from flask_login import current_user
from flask_wtf import FlaskForm

class AdminModelView(ModelView):
    def is_accessible(self):
        # Check if the user is logged in and is an admin
        return current_user.is_authenticated and (current_user.role == 'admin' or current_user.role == 'super')

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if the user doesn't have access
        return redirect(url_for('login'))


###
### Models ###
###

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    role = db.Column(db.String(100), default='pending', nullable=False)
    resetting_pw = db.Column(db.Boolean, default=True, nullable=False)
    otp = db.Column(db.String(16), nullable=True)
    def __repr__(self):
        return f"<User (id={self.id}, name={self.name})>"

###
### Views ###
###
  
class UserView(AdminModelView):
    column_list = ('id', 'name', 'email', 'role', 'resetting_pw', 'otp')
    page_size = 50
    column_default_sort = ('name', False)
