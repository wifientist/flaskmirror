from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, current_app, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from .utils.zemail import send_ztemplate, send_zemail
import random
import string

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user: # or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    
    if user.resetting_pw:
        # If user needs to reset password, redirect to OTP verification
        return redirect(url_for('auth.verify_otp'))
    
    if user.password is None:
        # Handle the case where the password is None
        flash('Invalid password or user does not exist. Please try again.')
        return redirect(url_for('auth.login'))
    
    if not check_password_hash(user.password, password):
        flash('Invalid password. Please try again.')
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        current_user.name = new_name
        if current_user.email != new_email:
            current_user.email = new_email
            current_user.resetting_pw = True
            current_user.otp = generate_otp()
            #TODO Here you would add your email sending logic to send the OTP to the new email
            flash('Email changed! A new OTP has been sent to your new email address.')
            logout_user()
            db.session.commit()
            return redirect(url_for('auth.verify_otp'))
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('auth.profile'))
    
    return render_template('profile.html', user=current_user)


@auth_bp.route('/signup')
def signup():
    return render_template('signup.html')

@auth_bp.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    #name = request.form.get('name')
    #password = request.form.get('password')
    role = 'pending'

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # Generate OTP and send via email
    otp = generate_otp()  # You'll need to implement this function

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    #new_user = User(email=email, name=name, role=role, password=generate_password_hash(password, method='pbkdf2:sha256'))
    new_user = User(name=email, email=email, role=role, otp=otp, resetting_pw=True)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    #return redirect(url_for('auth.login'))
    
    #send_email('Verify your email',sender='yourapp@example.com',recipients=[email],text_body=otp,html_body=otp)
    ZEPTO_KEY = current_app.config['ZEPTO_KEY']
    ZEPTO_OTP_ID = current_app.config['ZEPTO_OTP_ID']
    merge = {'name':'User', 'product_name':'Flask Mirror', 'OTP':otp}
    send_ztemplate(ZEPTO_KEY, [email], [], ZEPTO_OTP_ID, merge)

    flash('A verification email has been sent with an OTP. Please check your inbox.')
    return redirect(url_for('auth.verify_otp'))

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = request.form.get('email')
        otp_entered = request.form.get('otp')

        user = User.query.filter_by(email=email).first()
        if user:
            # Validate OTP
            if otp_is_valid(user, otp_entered):  # Implement this function to verify OTP
                # Log in the user
                login_user(user)
                # Redirect to the password set page
                flash('OTP verified. Please set your password.')
                return redirect(url_for('auth.set_password'))
            flash('Invalid OTP, please try again.')
            return redirect(url_for('auth.verify_otp'))
            #current_user.resetting_pw = False
            #db.session.commit()
            #flash('Email verified. Please set your password.')
            #return redirect(url_for('auth.set_password'))
        flash('Error: User not found.')
        return redirect(url_for('auth.verify_otp'))

        #flash('Invalid OTP. Please try again or request a new OTP.')
        #return redirect(url_for('auth.verify_otp'))

    return render_template('verify_otp.html')

@auth_bp.route('/set_password', methods=['GET', 'POST'])
@login_required
def set_password():
    if request.method == 'POST':
        password = request.form.get('password')
        current_user.password = generate_password_hash(password, method='pbkdf2:sha256')
        current_user.resetting_pw = False
        current_user.otp = None
        db.session.commit()
        flash('Password set successfully. You can now login with your new password.')
        return redirect(url_for('auth.profile'))

    return render_template('set_password.html')

@auth_bp.route('/lost_password', methods=['GET', 'POST'])
def lost_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate OTP and send via email
            otp = generate_otp()  # You'll need to implement this function
            #send_email('Reset your password', sender='yourapp@example.com',
            #           recipients=[email], text_body=otp, html_body=otp)
            ZEPTO_KEY = current_app.config['ZEPTO_KEY']
            ZEPTO_RESET_ID = current_app.config['ZEPTO_RESET_ID']
            merge = {'name':user.name, 'product_name':'Flask Mirror', 'OTP':otp}
            send_ztemplate(ZEPTO_KEY, [email], [], ZEPTO_RESET_ID, merge)

            user.resetting_pw = True
            user.otp = otp
            db.session.commit()

            flash('A password reset email has been sent. Please check your inbox.')
            return redirect(url_for('auth.verify_otp'))

        flash('Email address not found.')
        return redirect(url_for('auth.lost_password'))

    return render_template('lost_password.html')

def generate_otp():
    # Implement OTP generation logic
    #return '123456'  # Example OTP; replace with actual implementation
    return ''.join(random.choices(string.digits, k=6))

def otp_is_valid(user, otp_entered):
    # Implement OTP validation logic
    #return otp_entered == '123456'  # Example validation; replace with actual implementation
    return otp_entered == user.otp

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
