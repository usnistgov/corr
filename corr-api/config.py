DEBUG = True

FLASK_ENV = 'development'

# In the case of OSX or Windows,
# Verify that your docker host is 172.17.0.1
# If not replace it in the mongodb_host field.
# In case of ubuntu leave the host to 0.0.0.0
MONGODB_SETTINGS = {
    'db': 'corr-integrate',
    'host': '0.0.0.0',
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
    'content': 'True'
}
