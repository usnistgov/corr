"""CoRR inter-entity flask instance share."""
from flask import Flask
from .tools.converters import ObjectIDConverter
from flask.ext.mongoengine import MongoEngine
from .managers import StorageManager
from .managers import AccessManager



db = MongoEngine()

def setup_app(name, config='config'):
    """Setup a flask app instance with a config file.
    Each application has to provide its python config
    parameters.
        Returns:
            The flask app instance.
    """
    app = Flask(name)
    app.config.from_object(config)
    app.logger_name = "flask.app"

    # Flask-MongoEngine instance
    db.init_app(app)
    
    # Custom Converters
    app.url_map.converters['objectid'] = ObjectIDConverter

    storage_manager = StorageManager(app)
    access_manager = AccessManager(app)

    return app, storage_manager, access_manager