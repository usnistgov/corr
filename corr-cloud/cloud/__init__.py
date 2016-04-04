# import jinja2
import flask as fk
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import AccessModel
import tarfile
from StringIO import StringIO
from io import BytesIO
import zipfile
import json
import time
import boto3
import traceback 
import datetime

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

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

def cloud_response(code, title, content):
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    # print response
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

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

def s3_get_file(group='', key=''):
    file_buffer = StringIO()
    try:
        obj = None
        if key != '':
            obj = s3.Object(bucket_name='corr-%ss'%group, key=key)
        else:
            if group == 'picture' or group == 'logo':
                obj = s3.Object(bucket_name='corr-%ss'%group, key='default-%s.png'%group)
    except:
        if group == 'picture' or group == 'logo':
            obj = s3.Object(bucket_name='corr-logos', key='default-%s.png'%group)

    try:
        res = obj.get()
        file_buffer.write(res['Body'].read())
        file_buffer.seek(0)
        return file_buffer
    except:
        return None

def s3_upload_file(file_meta=None, file_obj=None):
    if file_meta != None and file_obj != None:
        if file_meta.location == 'local':
            dest_filename = file_meta.storage
            try:
                group = 'corr-resources'
                if file_meta.group != 'descriptive':
                    group = 'corr-%ss'%file_meta.group
                print group
                s3_files = s3.Bucket(group)
                s3_files.put_object(Key=dest_filename, Body=file_obj.read())
                return [True, "File uploaded successfully"]
            except:
                return [False, traceback.format_exc()]
        else:
            return [False, "Cannot upload a file that is remotely set. It has to be local targeted."]
    else:
        return [False, "file meta data does not exist or file content is empty."]

def s3_delete_file(group='', key=''):
    deleted = False
    if key not in ["default-logo.png", "default-picture.png"]:
        s3_files = s3.Bucket('corr-%ss'%group)
        for _file in s3_files.objects.all():
            if _file.key == key: 
                _file.delete()
                print "File deleted!"
                deleted = True
                break
        if not deleted:
            print "File not deleted"
    return deleted



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

def logTraffic(endpoint=''):
    # created_at=datetime.datetime.utcnow()
    (traffic, created) = TrafficModel.objects.get_or_create(service="cloud", endpoint="%s%s"%(CLOUD_URL, endpoint))
    if not created:
        traffic.interactions += 1 
        traffic.save()
    else:
        traffic.interactions = 1
        traffic.save()

def logAccess(scope='root', endpoint=''):
    (traffic, created) = AccessModel.objects.get_or_create(scope=scope, endpoint="%s%s"%(CLOUD_URL, endpoint))


def logStat(deleted=False, user=None, message=None, application=None, project=None, record=None, diff=None, file_obj=None, comment=None):
    category = ''
    periode = ''
    traffic = 0
    interval = ''
    today = datetime.date.today()
    last_day = monthrange(today.year, today.month)[1]

    if user != None:
        category = 'user'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if project != None:
        category = 'project'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if application != None:
        category = 'application'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if message != None:
        category = 'message'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if record != None:
        category = 'record'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if diff != None:
        category = 'collaboration'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)

    if file_obj != None:
        category = 'storage'
        periode = 'daily'
        traffic = file_obj.size * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if comment != None:
        category = 'comment'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    #created_at=datetime.datetime.utcnow()
    (stat, created) = StatModel.objects.get_or_create(interval=interval, category=category, periode=periode)
    print "Stat Traffic {0}".format(traffic)
    if not created:
        print "Not created stat"
        if (stat.traffic + traffic) >= 0:
            stat.traffic += traffic
        stat.save()
    else:
        print "Created stat"
        stat.traffic = traffic
        stat.save()

CLOUD_VERSION = 0.1
CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

from . import views
from corrdb.common import models
from . import filters
