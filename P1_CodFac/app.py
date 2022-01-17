from flask import Flask
from routes.login import logeo
from flask_sqlalchemy import SQLAlchemy
from config.config import DevelopmentConfig
from models.User import db

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)

# app.register_blueprint(listar)
app.register_blueprint(logeo)

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run()