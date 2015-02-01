from package import app
from flask import Flask, flash, redirect, url_for, request, render_template, redirect, session
from flaskext.mysql import MySQL
from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, validators, SubmitField
from models import db,User,Note

class LoginForm(Form):
	email = TextField('Email',[validators.Required()])
	password = PasswordField('Password',[validators.Required()])
	submit = SubmitField("Login")
	def __init__(self,*args, **kwargs):
		Form.__init__(self,*args,**kwargs)
		self.user = None
	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False
		user = User.query.filter_by( email=self.email.data.lower() ).first()
		if user is None:
			self.email.errors.append('Unknown mail ID')
			return False
		if not user.check_password(self.password.data):
			self.password.errors.append('Invalid password')
			return False
		self.user = user
		return True

class RegistrationForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=25)])
	email = TextField('Email', [validators.Length(min=6, max=35)])
	password = PasswordField('Password', [
	validators.Required(),validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	submit = SubmitField("Register")
	def __init__(self, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
	def validate(self):
		if not Form.validate(self):
			return False
		user = User.query.filter_by(email = self.email.data.lower()).first()
		if user:
			self.email.errors.append("That email is already taken")
			return False
		else:
			return True

@app.route('/login',methods=['GET','POST'])
def login():
	if 'uid' in session:
		return redirect('/')
	form = LoginForm()
	if form.validate_on_submit():
		flash('Login successful.')
		#user = User.query.filter_by(email = form.email.data.lower()).first()
		session['uid'] = form.user.uid
		return redirect('/')
	return render_template('login.html', form=form)

@app.route('/register',methods=['GET','POST'])
def register():
    if 'uid' in session:
		return redirect('/')
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
	newuser = User(form.username.data, form.password.data, form.email.data)
	db.session.add(newuser)
	db.session.commit()        
	flash('Thanks for registering.')
        return redirect('/login')
    return render_template('register.html', form=form)

@app.route('/delete',methods=['POST'])
def delete():
	
	if 'uid' not in session:
		return redirect('/')
	note = Note.query.filter_by(nid = request.form['nid']).first()
	db.session.delete(note)
	db.session.commit()	
	#print "We are here!"
	return render_template("layout.html",Note = Note)
	
@app.route('/logout')
def logout():
	if 'uid' not in session:
		return redirect('/')
	session.pop('uid',None)
	return redirect('/')

@app.route('/')
def home():
	if 'uid' not in session:
		return render_template('home.html')
	return render_template('layout.html',Note = Note)

@app.route('/notes')
def notes():	
	return redirect('/')
	
@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/save',methods=['POST'])
def save():
	title = request.form['ntitle']
	body = request.form['nbody']
	note = Note(title,body,session['uid'])
	db.session.add(note)
	db.session.commit()
	flash('Note saved successfully.')
	return redirect("/")

