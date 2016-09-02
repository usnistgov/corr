# from .. import logAccess
from flask.ext.stormpath import StormpathManager

class AccessManager:
    def __init__(self, app):
        self.config = app.config['ACCOUNT_MANAGEMENT']

        if self.config == 'stormpath':
            self.manager = StormpathManager(app)
            self.type = 'stormpath'
        elif self.config == 'api-token':
            self.manager = self
            self.type = 'api-token'

