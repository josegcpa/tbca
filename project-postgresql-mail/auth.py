from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db, mail
from flask_mail import Message
import os
import string,random
import re

email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('main.profile'))
    return render_template('login.html')

@auth.route('/signup-successful')
def signup_successful():
    if current_user.is_authenticated == True:
        return redirect(url_for('main.profile'))
    return render_template('signup-successful.html')

@auth.route('/signup')
def signup():
    if current_user.is_authenticated == True:
        return redirect(url_for('main.profile'))
    return render_template('signup.html')

@auth.route('/password-recovery')
def password_recovery():
    return render_template('password-recovery.html')

@auth.route('/send-token',methods=['POST'])
def send_token():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email not found.','error')
        return redirect(url_for('auth.password_recovery')) # if the user doesn't exist reload the page
    else:
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
        with mail.connect() as conn:
            msg = Message(subject="TBCA password recovery token".encode('utf-8'),
                          body="Your token for password recovery is {}".format(token),
                          recipients=[email.encode('utf-8')])

            conn.send(msg)
        cur = conn_users.cursor()
        sql = 'INSERT INTO password_recovery (email,token) VALUES (%s, %s);'
        param = [email,token]
        curs.execute(sql,param)
        flash('Token has been emailed','info')

@auth.route('/new-password',methods=['POST'])
def new_password():
    email = request.form.get('email')
    token = request.form.get('token')
    password = request.form.get('password')
    password_confirm = request.form.get('password-confirm')

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Email not found.','error')
        return redirect(url_for('auth.password_recovery')) # if the user doesn't exist reload the page
    cur = conn_users.cursor()
    sql = "SELECT token FROM password_recovery WHERE email = %s;"
    param = [email]
    curs.execute(sql,param)
    token = curs.fetchall()

    if len(token) == 0:
        flash('No token was requested.','error')
        return redirect(url_for('auth.password_recovery')) # if the user didn't request a token reload the page

    if password != password_confirm:
        flash('Passwords do not match.','error')
        return redirect(url_for('auth.password_recovery')) # if the user didn't request a token reload the page

    else:
        user.password = generate_password_hash(password, method='sha256')
        db.session.commit()
        flash('Password has been updated.','info')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    institute = request.form.get('institute')
    password = request.form.get('password')

    if len(password) < 8: # checks password length
        flash('Password too short')
        return redirect(url_for('auth.signup'))
    if email_regex.match(email) is None:
        flash('Email is not valid')
        return redirect(url_for('auth.signup'))
    if len(institute) < 2:
        flash('Institute name is too short')
        return redirect(url_for('auth.signup'))

    User.query.filter_by(email=email).first()
    user = User.query.filter_by(email=email).first()

    if user: # checks if user exists
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    new_user = User(
        email=email, name=name,
        password=generate_password_hash(password, method='sha256'),
        institute=institute,n_cells=0,is_admin=False,is_authorised=False)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.signup_successful'))

@auth.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    if user.is_authorised == False:
        flash("""
              Please wait for admin authorisation to use The Blood Cell Atlas.
              For more details please contact us via josegcpa@ebi.ac.uk.
              """)
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user)
    return redirect(url_for('main.profile'))
