import os

class Config:

    SECRET_KEY = "smart_employee_secret_key"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "employee.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = "sganta119@gmail.com"
    MAIL_PASSWORD = "gdsz blfo ufmx wwbq"
    MAIL_DEFAULT_SENDER = "sganta119@gmail.com"