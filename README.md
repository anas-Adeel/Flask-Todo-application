# Flask-Todo-application

This is a simple Flask application that will run on your own http://127.0.0.1:5000/.
This is a app on which you can create, delete and update certain tasks. It also has a built in database made via flask_SQLAlchemy.
To initialize the database you will need to go to terminal, change directories into the fill where the app is stored and run the command "python".
Then run the command "db.create_all()". This will create your database file which will store all of your Todo instances.
(Todo is a internal class which inherits from flask_SQLAlchemy and stores the time, date and content of things to do.)
