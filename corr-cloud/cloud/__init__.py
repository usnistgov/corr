# import jinja2
import flask as fk
from corrdb.common.core import setup_app
import tarfile
from StringIO import StringIO
from io import BytesIO
import zipfile
import json
import time
import boto3
import traceback

app = setup_app(__name__)

s3 =  boto3.resource('s3')

# Templates
# loader = jinja2.PackageLoader('cloud', 'templates')
# template_env = jinja2.Environment(autoescape=True, loader=loader)
# template_env.globals.update(url_for=fk.url_for)
# template_env.globals.update(get_flashed_messages=fk.get_flashed_messages)

#Remove templates
#include admin power everywhere here.

# Stormpath

from flask.ext.stormpath import StormpathManager

stormpath_manager = StormpathManager(app)

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


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and fk.request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = fk.make_response(f(*args, **kwargs))
            if not attach_to_all and fk.request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def load_bundle(record):
    # Include record files later.
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:

        try:
            bundle_buffer = StringIO()
            # with open(record.container.image['location'], 'rb') as fh:
            #     image_buffer.write(fh.read())
            # res = key.get_contents_to_filename(record.container.image['location'])   
            # s3_client = boto3.client('s3')
            # res = s3_client.get_object(Bucket='ddsm-bucket', Key=record.container.image['location']) 
            obj = s3.Object(bucket_name='reproforge-bundles', key=record.environment.bundle['location'])  
            res = obj.get()      
            bundle_buffer.write(res['Body'].read())
            bundle_buffer.seek(0)

            data = zipfile.ZipInfo("%s"%(record.project.name, record.environment.bundle['location'].split('_')))
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
            zf.writestr(data, bundle_buffer.read())
        except:
            print traceback.print_exc()

        try:
            json_buffer = StringIO()
            json_buffer.write(record.to_json())
            json_buffer.seek(0)

            data = zipfile.ZipInfo("%s_%s.json"%(record.project.name, str(record.id)))
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
            zf.writestr(data, json_buffer.read())
        except:
            print traceback.print_exc()
    memory_file.seek(0)


    # imz.append('record.tar', image_buffer.read()).append("record.json", json_buffer.read())

    # print record.container.image['location'].split("/")[-1].split(".")[0]+".zip"

    return [memory_file, record.environment.bundle['location'].split("/")[-1].split(".")[0]+".zip"]

def delete_project_files(project):
    s3_files = s3.Bucket('reproforge-pictures')
    s3_bundles = s3.Bucket('reproforge-bundles')

    from corrdb.common.models import ProjectModel
    from corrdb.common.models import RecordModel
    from corrdb.common.models import EnvironmentModel
    from corrdb.common.models import FileModel

    for record in project.records:
        for _file in record.files:
            s3_files.delete_key(_file.location)

    for environment_id in project.history:
        _environment = EnvironmentModel.objects.with_id(environment_id)
        if _environment.bundle["scope"] == "local":
            s3_bundles.delete_key(_environment.bundle["location"])
        del _environment

def delete_record_files(record):
    s3_files = s3.Bucket('reproforge-pictures')

    from corrdb.common.models import RecordModel
    from corrdb.common.models import FileModel

    for record in project.records:
        for _file in record.files:
            s3_files.delete_key(_file.location)

def delete_record_file(record_file):
    s3_files = s3.Bucket('reproforge-pictures')

    s3_files.delete_key(record_file.location)


def load_file(file_model):

    file_buffer = StringIO()
    obj = s3.Object(bucket_name='reproforge-files', key=file_model.location)  
    res = obj.get()      
    file_buffer.write(res['Body'].read())
    file_buffer.seek(0)

    return [file_buffer, file_model.location.split('_')[1]]

def load_picture(profile):

    picture_buffer = StringIO()
    obj = s3.Object(bucket_name='reproforge-pictures', key=profile.picture['location'])
    res = obj.get()      
    picture_buffer.write(res['Body'].read())
    picture_buffer.seek(0)

    return [picture_buffer, digest]

def upload_bundle(current_user, environment, file_obj):
    dest_filename = str(current_user.id)+"-"+str(environment.id)+"_%s"%file_obj.filename #kind is record| signature

    print "About to write..."
    try:
        s3.Bucket('reproforge-bundles').put_object(Key=str(current_user.id)+"-"+str(environment.id)+"_%s"%file_obj.filename, Body=file_obj.read())
        environment.bundle['location'] = dest_filename
        environment.bundle['size'] = file_obj.tell()
        print "%s saving..."%file_obj.filename
        environment.save()
        return True
    except:
        return False
        print traceback.print_exc()

def upload_file(current_user, file_model, file_obj):
    dest_filename = str(current_user.id)+"-"+str(file_model.record.id)+"_%s"%file_obj.filename #kind is record| signature

    print "About to write..."
    try:
        s3.Bucket('reproforge-files').put_object(Key=str(current_user.id)+"-"+str(record.id)+"_%s"%file_obj.filename, Body=file_obj.read())
        file_model.location = dest_filename
        file_model.size = file_obj.tell()
        print "%s saving..."%file_obj.filename
        file_model.save()
        return True
    except:
        return False
        print traceback.print_exc()

def upload_picture(current_user, file_obj):
    dest_filename = str(current_user.id) #kind is record| signature

    print "About to write..."
    try:
        s3.Bucket('reproforge-pictures').put_object(Key=str(current_user.id)+"."+file_obj.filename.split('.')[-1], Body=file_obj.read())
        print "%s saving..."%file_obj.filename
        return True
    except:
        return False
        print traceback.print_exc()

CLOUD_VERSION = 1
CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

from . import views
from corrdb.common import models
from . import filters
