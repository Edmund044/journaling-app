import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '12233_747744_3838_23456789abcdef'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://trial-db_owner:u2DemFOhR4WL@ep-silent-wood-a5ndpfqn.us-east-2.aws.neon.tech/journal-app?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or '12233_747744_3838_23456789abcdef'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
