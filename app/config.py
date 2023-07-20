class Config:
    SECRET_KEY = 'REDACTED'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'alertia2023@gmail.com'
    MAIL_DEFAULT_SENDER = 'alertia2023@gmail.com'
    MAIL_PASSWORD = 'REDACTED' # App password
    DEBUG = True
    PORT = 8080
    ENV = 'development'