from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_login.utils import login_required
import datetime
from forum.models import User, Post, Subforum, error, valid_title, valid_content, db, generateLinkPath, Comment

auth_bp = Blueprint('auth', __name__, template_folder='templates')

# Add these helper functions
def username_taken(username):
    return User.query.filter(User.username == username).first() is not None

def email_taken(email):
    return User.query.filter(User.email == email).first() is not None

def valid_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    return username.replace('_', '').replace('-', '').isalnum()

@auth_bp.route('/action_login', methods=['POST'])
def action_login():
	username = request.form['username']
	password = request.form['password']
	user = User.query.filter(User.username == username).first()
	if user and user.check_password(password):
		login_user(user)
	else:
		errors = []
		errors.append("Username or password is incorrect!")
		return render_template("login.html", errors=errors)
	return redirect("/")


@login_required
@auth_bp.route('/action_logout')
def action_logout():
	#todo
	logout_user()
	return redirect("/")

@auth_bp.route('/action_createaccount', methods=['POST'])
def action_createaccount():
	username = request.form['username']
	password = request.form['password']
	email = request.form['email']
	errors = []
	retry = False
	if username_taken(username):
		errors.append("Username is already taken!")
		retry=True
	if email_taken(email):
		errors.append("An account already exists with this email!")
		retry = True
	if not valid_username(username):
		errors.append("Username is not valid!")
		retry = True
	# if not valid_password(password):
	# 	errors.append("Password is not valid!")
	# 	retry = True
	if retry:
		return render_template("login.html", errors=errors)
	user = User(email, username, password)
	if user.username == "admin":
		user.admin = True
	db.session.add(user)
	db.session.commit()
	login_user(user)
	return redirect("/")

@auth_bp.route('/loginform')
def loginform():
	return render_template("login.html")


