from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = 'dgbsdpgbapdbnpa'
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)



class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(90), nullable=False)
	password_hash = db.Column(db.String(100), nullable=False)
	all_tasks = db.relationship('Todo', backref='user', lazy=True)

	def __repr__(self):
		return "<User %r>" % self.id


class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(200), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Task %r>' % self.id



@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		task_content = request.form['new_content']
		admin = User.query.filter_by(username='admin').first()
		new_task = Todo(content=task_content, user=admin, user_id=admin.id)
		admin.all_tasks.append(new_task)

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect('/')
		except Exception as e:
			return "Failed to add task to database"

	else:
		user = User.query.filter_by(username='admin').first()
		if user is None:
			user = User(username='admin', password='admin', password_hash=generate_password_hash('admin'))

		return render_template('index.html', tasks=user.all_tasks)


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
	task = Todo.query.get_or_404(todo_id)
	try:
		db.session.delete(task)
		db.session.commit()
		return redirect('/')

	except Exception as e:
		return 'Task was not deleted'


@app.route('/update/<int:todo_id>', methods=['GET', 'POST'])
def update(todo_id):
	task = Todo.query.get_or_404(todo_id)
	
	if request.method == 'POST':
		updated_content = request.form['new_content']

		try:
			task.content = updated_content
			db.session.commit()
			return redirect('/')

		except Exception as e:
			return 'Task was not able to be updated'

	else:
		return render_template('update.html', task=task)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		error = None

		if username == '':
			error = "Invalid username. Cannot be empty"

		elif User.query.filter_by(username=username).first() is None:
			error = "Invalid username. Doesn't exist"

		elif password == '':
			error = "Invalid password. Cannot be blank"

		else:
			user = User.query.filter_by(username=username).first()

			if not check_password_hash(user.password_hash, password):
				error = "Invalid username, password combo. Please try again."


		if error is None:
			user = User.query.filter_by(username=username).first()

			if check_password_hash(user.password_hash, password):
				return redirect(f'/{user.id}/tasks')

		else:
			flash(error)
			return render_template('login.html')


	return render_template('login.html')


@app.route('/sign up', methods=['GET', 'POST'])
def sign_up():
	if request.method == 'POST':
		user_name = request.form['username']
		user_password = request.form['password']
		dob = request.form['dob']
		error = None
		
		if user_name == '':
			error = 'Invalid Username. It cannot be blank'

		elif user_password == '':
			error = 'Invalid Password. It cannot be blank'

		elif User.query.filter_by(username=user_name).first() is not None:
			error = 'Username is already taken.'

		if error is None:
			new_user = User(username=user_name, password=user_password, password_hash=generate_password_hash(user_password))
			db.session.add(new_user)
			db.session.commit()

			return redirect(f'/{new_user.id}/tasks')
		else:
			flash(error)
			return render_template('sign_up.html')


	return render_template('sign_up.html')


@app.route('/<int:user_id>/tasks', methods=['GET', 'POST'])
def user_tasks(user_id):
	if request.method == 'POST':
		task_content = request.form['new_content']
		user = User.query.get_or_404(user_id)
		new_task = Todo(content=task_content, user_id=user_id)
		user.all_tasks.append(new_task)

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect(f'/{user_id}/tasks')

		except Exception as e:
			return "Failed to add new task to database"

	else:
		user = User.query.get_or_404(user_id)
		return render_template('user.html', user=user)


@app.route('/<int:user_id>/<int:task_id>/delete')
def user_delete(user_id, task_id):
	task = Todo.query.get_or_404(task_id)
	db.session.delete(task)
	db.session.commit()
	return redirect(f'/{user_id}/tasks')


@app.route('/<int:user_id>/<int:task_id>/update', methods=['GET', 'POST'])
def user_update(user_id, task_id):
	if request.method == 'POST':
		task = Todo.query.get_or_404(task_id)

		try:
			task.content = request.form['new_content']
			db.session.commit()
			return redirect(f'/{user_id}/tasks')
		except:
			return "Failed to make changes"
	else:
		user = User.query.get_or_404(user_id)
		task = Todo.query.get_or_404(task_id)
		return render_template('user_update.html', user=user, task=task)