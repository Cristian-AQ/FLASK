class Config(object):
    SECRET_KEY = '1qA23wesd'
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/flask'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/flask.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
