""" Object id converter.
This is taken from 
http://flask.pocoo.org/snippets/106/
"""

from flask import Flask
from werkzeug.routing import BaseConverter, ValidationError
from itsdangerous import base64_encode, base64_decode
from bson.objectid import ObjectId
from bson.errors import InvalidId

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        """Object ID converter to Python
            Returns:
                ObjectId from the base64
        """
        try:
            return ObjectId(base64_decode(value))
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        """Object ID converter to url
            Returns:
                Base64
        """
        return base64_encode(value.binary)

