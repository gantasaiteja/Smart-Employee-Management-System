import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "employee.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")