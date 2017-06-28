"""CoRR api module."""
import flask as fk
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel 
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import AccessModel
import tempfile
from io import StringIO
import zipfile
from io import BytesIO
import os
import simplejson as json
import difflib
import hashlib
import datetime
import traceback

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

import glob

# Flask app instance
app, storage_manager, access_manager = setup_app(__name__)

# The api's version
API_VERSION = 0.1
# The api base url
API_URL = '/corr/api/v{0}'.format(API_VERSION)


def secure_content(content):
    security = storage_manager.is_safe(json.dumps(content))
    if not security[0]:
        return fk.Response(security[1], status.HTTP_406_NOT_ACCEPTABLE)

def api_response(code, title, content):
    """Provides a common structure to represent the response
    from any api's endpoints.
        Returns:
            Flask response with a prettified json content.
    """
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

def data_pop(data=None, element=''):
    """Pop an element of a dictionary.
    """
    if data != None:
        try:
            del data[element]
        except:
            pass

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

MODE = app.config['MODE']
ACC_SEC = app.config['SECURITY_MANAGEMENT']['account']
CNT_SEC = app.config['SECURITY_MANAGEMENT']['content']

# import all the api endpoints.
import api.endpoints
