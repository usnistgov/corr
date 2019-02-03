WTF_CSRF_ENABLED = True

DEBUG = True
FLASK_ENV = 'development'

# Verify that your docker host is 172.17.0.1
# If not replace it in the mongodb_host field.
# Change the mongodb port here if needed.
# Warning: Make sure the docker-compose port matches.
MONGODB_SETTINGS = {
    'db': 'corr-integrate',
    'host': '0.0.0.0',
    'port': 27017,
}

MODE = 'http'

VIEW_SETTINGS = {
    'host': '0.0.0.0',
    'port': 5000,
}

API_SETTINGS = {
    'host': '0.0.0.0',
    'port': 5100,
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
    'account': 'True',
    'content': 'True'
}

ENVIRONMENT = 'development'
