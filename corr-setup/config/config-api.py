DEBUG = True

FLASK_ENV = 'development'

MONGODB_SETTINGS = {
    'db': 'corr',
    'host': 'corrdb',
    'port': 27017
}

MODE = 'http'

ENVIRONMENT = 'development'

FILE_STORAGE = {
    'type': 'filesystem',
    'location': '/home/corradmin/',
    'name': 'corr-storage',
    'id': '',
    'key': ''
}

ACCOUNT_MANAGEMENT = {
    'type': 'api-token'
}

SECURITY_MANAGEMENT = {
    'account': 'True',
    'content': 'False'
}
