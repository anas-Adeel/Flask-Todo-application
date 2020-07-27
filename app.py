from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
db.create_all()



class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(200), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Task %r>' % self.id

 
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		task_content = request.form['content']
		new_task = Todo(content=task_content)

		try:
			db.session.add(new_task)
			db.session.commit()
			return redirect('/')
		except Exception as e:
			return "Failed to add task to database"

	else:
		tasks = Todo.query.order_by(Todo.date_created).all()
		return render_template('index.html', tasks=tasks)


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