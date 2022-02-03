class Config(object):
    SECRET_KEY = '1qA23wesd'
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost:5432/DDBBIMG'
    MAX_CONTENT_LENGTH = 100*1000*1000 #tamano maximo permitido
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/flask.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False