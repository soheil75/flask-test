from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from redis import Redis
from config import Development


app = Flask(__name__)
app.config.from_object(Development)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)
redis = Redis.from_url(app.config['REDIS_SERVER_URL'])

from view import index

    
from model_admin import admin
from model_users import users
from model_blog import blog
from model_uploads import uploads


app.register_blueprint(admin)
app.register_blueprint(users)
app.register_blueprint(blog)
app.register_blueprint(uploads)