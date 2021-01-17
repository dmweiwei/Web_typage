import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'web-typage.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
