from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Development


app = Flask(__name__)
app.config.from_object(Development)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

from view import index, register, login

    
from model_admin import admin
from model_users import users


app.register_blueprint(admin)
app.register_blueprint(users)