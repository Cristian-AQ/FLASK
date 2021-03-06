from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(40),unique=True)
    password = db.Column(db.String(66))
    create_date = db.Column(db.DateTime,default=datetime.datetime.now)
    
    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = self.create_password(password)
    
    def create_password(self,password):
        return generate_password_hash(password)
    def verify_password(self,password):
        return check_password_hash(self.password, password)