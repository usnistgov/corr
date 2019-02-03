WTF_CSRF_ENABLED = True

DEBUG = True
FLASK_ENV = 'development'

MONGODB_SETTINGS = {
    'db': 'corr',
    'host': 'corrdb',
    'port': 27017,
}

MODE = 'http'

VIEW_SETTINGS = {
    'host': '0.0.0.0',
    'port': 443,
}

API_SETTINGS = {
    'host': '0.0.0.0/api',
    'port': 443,
}

FILE_STORAGE = {
    'type': 'filesystem',
    'location': '/home/corradmin/',
    'name': 'corr-storage',
    'id': '',
    'key': ''
}

ACCOUNT_MANAGEMENT = {
    'type': 'mongodb'
}

SECURITY_MANAGEMENT = {
    'account': True,
    'content': True
}

ENVIRONMENT = 'development'
