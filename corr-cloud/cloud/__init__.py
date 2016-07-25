import flask as fk
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import AccessModel
import tarfile
from io import StringIO
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

S3_BUCKET = app.config['S3_BUCKET']

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
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
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

    return [memory_file, record.environment.bundle['location'].split("/")[-1].split(".")[0]+".zip"]

def delete_project_files(project):
    from corrdb.common.models import ProjectModel
    from corrdb.common.models import RecordModel
    from corrdb.common.models import EnvironmentModel
    from corrdb.common.models import FileModel

    # print s3_files
    # project resources
    for _file in project.resources:
        file_ = FileModel.objects.with_id(_file)
        if file_:
            # print file_.to_json()
            result = s3_delete_file(file_.group, file_.storage)
            if result:
                logStat(deleted=True, file_obj=file_)
                file_.delete()

    # project records resources
    for record in project.records:
        result = delete_record_files(record)
        if result:
            logStat(deleted=True, record=record)
            record.delete()

    for environment_id in project.history:
        _environment = EnvironmentModel.objects.with_id(environment_id)
        if _environment.bundle["scope"] == "local":
            s3_bundles.delete_key(_environment.bundle.location)
            result = s3_delete_file('bundle', _environment.bundle.location)
            if result:
                logStat(deleted=True, bundle=_environment.bundle)
                logStat(deleted=True, environment=_environment)
                _environment.bundle.delete()
                _environment.delete()
        else:
            logStat(deleted=True, environment=_environment)
            _environment.delete()

def cloud_response(code, title, content):
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    # print response
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

def delete_record_files(record):
    # s3_files = s3.Bucket('reproforge-files')

    from corrdb.common.models import RecordModel
    from corrdb.common.models import FileModel
    final_result = True
    for _file_id in record.resources:
        _file = FileModel.objects.with_id(_file_id)
        result = delete_record_file(_file)
        if not result:
            final_result = result
    return final_result

def delete_record_file(record_file):
    result = s3_delete_file(record_file.group, record_file.storage)
    if result:
        logStat(deleted=True, file_obj=record_file)
        record_file.delete()
    return result

def s3_get_file(group='', key=''):
    file_buffer = StringIO()
    print('corr-{0}s/{1}'.format(group,key))
    try:
        obj = None
        if key != '':
            obj = s3.Object(bucket_name=S3_BUCKET, key='corr-{0}s/{1}'.format(group,key))
        else:
            if group == 'picture' or group == 'logo':
                obj = s3.Object(bucket_name=S3_BUCKET, key='corr-{0}s/default-{1}.png'.format(group,key))
    except:
        print('corr-{0}s/{1}'.format(group,key))
        print(traceback.print_exc())
        if group == 'picture' or group == 'logo':
            obj = s3.Object(bucket_name=S3_BUCKET, key='corr-logos/default-{0}.png'.format(group))

    try:
        res = obj.get()
        file_buffer.write(res['Body'].read())
        file_buffer.seek(0)
        return file_buffer
    except:
        print('corr-{0}s/{1}'.format(group,key))
        print(traceback.print_exc())
        return None

def s3_upload_file(file_meta=None, file_obj=None):
    if file_meta != None and file_obj != None:
        if file_meta.location == 'local':
            dest_filename = file_meta.storage
            try:
                group = 'corr-resources'
                if file_meta.group != 'descriptive':
                    group = 'corr-%ss'%file_meta.group
                print(group)
                s3_files = s3.Bucket(S3_BUCKET)
                s3_files.put_object(Key='{0}/{1}'.format(group, dest_filename), Body=file_obj.read())
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
        s3_files = s3.Bucket(S3_BUCKET)
        for _file in s3_files.objects.all():
            if _file.key == 'corr-{0}s/{1}'.format(group, key): 
                _file.delete()
                print("File deleted!")
                deleted = True
                break
        if not deleted:
            print("File not deleted")
    return deleted

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

def prepare_record(record=None):
    if record == None:
        return [None, '']
    else:
        env = record.environment
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            record_dict = record.extended()
            environment = record_dict['head']['environment']
            del record_dict['head']['environment']
            comments = record_dict['head']['comments']
            del record_dict['head']['comments']
            resources = record_dict['head']['resources']
            del record_dict['head']['resources']
            inputs = record_dict['head']['inputs']
            del record_dict['head']['inputs']
            outputs = record_dict['head']['outputs']
            del record_dict['head']['outputs']
            dependencies = record_dict['head']['dependencies']
            del record_dict['head']['dependencies']
            application = record_dict['head']['application']
            del record_dict['head']['application']
            parent = record_dict['head']['parent']
            del record_dict['head']['parent']
            body = record_dict['body']
            del record_dict['body']
            execution = record_dict['head']['execution']
            del record_dict['head']['execution']
            project = record.project.info()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("project.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(inputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("inputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(outputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("outputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(dependencies, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("dependencies.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(parent, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("parent.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(body, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("body.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(execution, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("execution.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(environment, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("environment.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(record_dict, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)
                data = zipfile.ZipInfo("record.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
            if env != None and env.bundle.location != '':
                try:
                    bundle_buffer = StringIO()
                    if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                        bundle_buffer = web_get_file(env.bundle.location)
                    else:
                        bundle_buffer = s3_get_file('bundle', env.bundle.location)

                    data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print(traceback.print_exc())
            for resource in resources:
                try:
                    bundle_buffer = StringIO()
                    data = None
                    if 'http://' in resource['storage'] or 'https://' in resource['storage']:
                        bundle_buffer = web_get_file(resource['storage'])
                        data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage'].split('/')[-1]))
                    else:
                        bundle_buffer = s3_get_file(resource['group'], resource['storage'])
                        data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage']))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print(traceback.print_exc())
            
        memory_file.seek(0)

    return [memory_file, "project-%s-record-%s.zip"%(str(record.project.id), str(record.id))]

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
    print("Stat Traffic {0}".format(traffic))
    if not created:
        print("Not created stat")
        if (stat.traffic + traffic) >= 0:
            stat.traffic += traffic
        stat.save()
    else:
        print("Created stat")
        stat.traffic = traffic
        stat.save()

CLOUD_VERSION = 0.1
CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

VIEW_HOST = app.config['VIEW_SETTINGS']['host']
VIEW_PORT = app.config['VIEW_SETTINGS']['port']

API_HOST = app.config['VIEW_SETTINGS']['host']
API_PORT = app.config['VIEW_SETTINGS']['port']


from . import views
from corrdb.common import models
from . import filters
