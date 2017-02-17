import flask as fk
from corrdb.common import logAccess, logStat, logTraffic
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import AccessModel
from io import StringIO
from io import BytesIO
import zipfile
import simplejson as json
import time
import traceback 
import datetime

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

app, storage_manager, access_manager = setup_app(__name__)

CLOUD_VERSION = 0.1
CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

# Stormpath

# from flask.ext.stormpath import StormpathManager

# stormpath_manager = StormpathManager(app)

from datetime import date, timedelta
from functools import update_wrapper


def get_week_days(year, week):
    d = date(year,1,1)
    if(d.weekday()>3):
        d = d+timedelta(7-d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days = (week-1)*7)
    return d + dlt,  d + dlt + timedelta(days=6)

def find_week_days(year, current):
    index  = 1
    while True:
        if index == 360:
            break
        interval = get_week_days(year, index)
        if current > interval[0] and current < interval[1]:
            return interval
        index +=1

class InMemoryZip(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = StringIO()

    def append(self, filename_in_zip, file_contents):
        '''Appends a file with name filename_in_zip and contents of 
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        # Write the file to the in-memory zip
        zf.writestr(filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0        

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        f = file(filename, "w")
        f.write(self.read())
        f.close()

def cloud_response(code, title, content):
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    # print response
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
VIEW_HOST = '{0}://{1}'.format(MODE, app.config['VIEW_SETTINGS']['host'])
VIEW_PORT = app.config['VIEW_SETTINGS']['port']

API_HOST = '{0}://{1}'.format(MODE, app.config['API_SETTINGS']['host'])
API_PORT = app.config['API_SETTINGS']['port']

ACC_SEC = app.config['SECURITY_MANAGEMENT']['account']
CNT_SEC = app.config['SECURITY_MANAGEMENT']['content']

from . import views
from corrdb.common import models
from . import filters
