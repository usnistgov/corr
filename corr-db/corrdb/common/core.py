"""CoRR inter-entity flask instance share."""
from flask import Flask
from .tools.converters import ObjectIDConverter
from flask_mongoengine import MongoEngine

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
    app.debug = True

    # Flask-MongoEngine instance
    db.init_app(app)
    
    # Custom Converters
    app.url_map.converters['objectid'] = ObjectIDConverter

    return app

