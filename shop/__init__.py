from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
import os
from flask_login import LoginManager
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/myshop4'
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user='lmzmukpyharrik',pw='a334089832744e3280289b61f1c3dc821407562c6ff6bc6d87638453b43f04cf',url='ec2-35-175-155-248.compute-1.amazonaws.com',db='myshop4')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SECRET_KEY'] = 'hfouewhfoiwefoquw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "mysql":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'customer_login'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = "Please login first"

from shop.admin import routes
from shop.products import routes
from shop.carts import routes
from shop.customers import routes
