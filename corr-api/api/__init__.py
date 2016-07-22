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
import tarfile
from StringIO import StringIO
import zipfile
from io import BytesIO
import os
import json
import difflib
import hashlib
import datetime
import boto3
import traceback

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

from flask.ext.restful import  Api
from flask_restful_swagger import swagger

# Flask app instance
app = setup_app(__name__)

# Boto s3 instance
s3 =  boto3.resource('s3')

# S3 bucket location
try:
    S3_BUCKET = app.config['S3_BUCKET']
except:
    S3_BUCKET = ""

# The api's version
API_VERSION = 0.1
# The api base url
API_URL = '/api/v{0}'.format(API_VERSION)

api = swagger.docs(Api(app), apiVersion='{0}'.format(API_VERSION))

def check_api(token):
    """Get the user object instance from its api token.
        Returns:
            The user object instance.
    """
    return UserModel.objects(api_token=token).first()

def check_app(token):
    """Get the application object instance from its api token.
        Returns:
            The application object instance.
    """
    if token == "no-app":
        return None
    else:
        for application in ApplicationModel.objects():
            print "%s -- %s." %(str(application.developer.id), application.name)
        return ApplicationModel.objects(app_token=token).first()

def check_admin(token):
    """Check if a user is an admin from his token.
        Returns:
            - None if the user does not exist or not an Admin.
            - Otherwise, return the user instance object.
    """
    user_model = UserModel.objects(api_token=token).first()
    if user_model == None:
        return None
    else:
        print user_model.group
        return user_model if user_model.group == "admin" else None

def prepare_env(project=None, env=None):
    """Bundle a project's environment.
        Returns:
            Zip file buffer of the environment's content.
    """
    if project == None or env == None:
        return [None, '']
    else:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            if env.bundle.location != '':
                try:
                    bundle_buffer = StringIO()
                    if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                        bundle_buffer = web_get_file(env.bundle.location)
                    else:
                        bundle_buffer = s3_get_file('bundle', env.bundle.location)

                    data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()

            try:
                json_buffer = StringIO()
                json_buffer.write(env.to_json())
                json_buffer.seek(0)

                data = zipfile.ZipInfo("env.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
        memory_file.seek(0)

    return [memory_file, "project-%s-env-%s.zip"%(str(project.id), str(env.id))]

def prepare_project(project=None):
    """Bundle an entire project
        Returns:
            Zip file buffer of the project's content.
    """
    if project == None:
        return [None, '']
    else:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            project_dict = project.compress()
            comments = project_dict['comments']
            del project_dict['comments']
            resources = project_dict['resources']
            del project_dict['resources']
            history = project_dict['history']
            del project_dict['history']
            records = project_dict['records']
            del project_dict['records']
            diffs = project_dict['diffs']
            del project_dict['diffs']
            application = project_dict['application']
            del project_dict['application']
            try:
                project_buffer = StringIO()
                project_buffer.write(json.dumps(project_dict, sort_keys=True, indent=4, separators=(',', ': ')))
                project_buffer.seek(0)
                data = zipfile.ZipInfo("project.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, project_buffer.read())
            except:
                print traceback.print_exc()
            try:
                comments_buffer = StringIO()
                comments_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                comments_buffer.seek(0)
                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, comments_buffer.read())
            except:
                print traceback.print_exc()
            try:
                resources_buffer = StringIO()
                resources_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                resources_buffer.seek(0)
                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, resources_buffer.read())
            except:
                print traceback.print_exc()
            try:
                history_buffer = StringIO()
                history_buffer.write(json.dumps(history, sort_keys=True, indent=4, separators=(',', ': ')))
                history_buffer.seek(0)
                data = zipfile.ZipInfo("environments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, history_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("records.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(diffs, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("diffs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
        memory_file.seek(0)

    return [memory_file, "project-%s.zip"%str(project.id)]

def prepare_record(record=None):
    """Bundle a record.
        Returns:
            Zip file buffer of a record's content.
    """
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
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(inputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("inputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(outputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("outputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(dependencies, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("dependencies.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(parent, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("parent.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(body, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("body.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(execution, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("execution.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(environment, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("environment.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(record_dict, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)
                data = zipfile.ZipInfo("record.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
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
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()
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
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()
            
        memory_file.seek(0)

    return [memory_file, "project-%s-record-%s.zip"%(str(record.project.id), str(record.id))]

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    """Allow crossdomain calls from other domains and port.
        Returns:
            decorator to wrap on the endpoints.
    """
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

def delete_project_files(project):
    """Delete a project files.
    """
    from corrdb.common.models import ProjectModel
    from corrdb.common.models import RecordModel
    from corrdb.common.models import EnvironmentModel
    from corrdb.common.models import FileModel

    for _file in project.resources:
        file_ = FileModel.objects.with_id(_file)
        if file_:
            result = s3_delete_file(file_.group, file_.storage)
            if result:
                logStat(deleted=True, file_obj=file_)
                file_.delete()

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

def delete_record_files(record):
    """Delete a record files.
        Returns:
            True if all files are deleted.
    """
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
    """Delete a record file and log the stats.
        Returns:
            Return of the s3_delete_file call.
    """
    result = s3_delete_file(record_file.group, record_file.storage)
    if result:
        logStat(deleted=True, file_obj=record_file)
        record_file.delete()
    return result

def api_response(code, title, content):
    """Provides a common structure to represent the response
    from any api's endpoints.
        Returns:
            Flask response with a prettified json content.
    """
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

def s3_get_file(group='', key=''):
    """Retrive a file from the s3 bucket.
        Returns:
            File buffer.
    """
    file_buffer = StringIO()
    try:
        obj = None
        if key != '':
            obj = s3.Object(bucket_name=S3_BUCKET, key='corr-{0}s/{1}'.format(group,key))
        else:
            if group == 'picture' or group == 'logo':
                obj = s3.Object(bucket_name=S3_BUCKET, key='corr-{0}s/default-{1}.png'.format(group,key))
    except:
        if group == 'picture' or group == 'logo':
            obj = s3.Object(bucket_name=S3_BUCKET, key='corr-logos/default-{0}.png'.format(group))

    try:
        res = obj.get()
        file_buffer.write(res['Body'].read())
        file_buffer.seek(0)
        return file_buffer
    except:
        return None

def s3_upload_file(file_meta=None, file_obj=None):
    """Upload a file into the s3 bucket.
        Returns:
            an array of two elements. one is the status
            of the upload and the other is a message 
            accompanying it.
    """
    if file_meta != None and file_obj != None:
        if file_meta.location == 'local':
            dest_filename = file_meta.storage
            try:
                group = 'corr-resources'
                if file_meta.group != 'descriptive':
                    group = 'corr-%ss'%file_meta.group
                print group
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
    """Delete a file from the s3 bucket.
        Returns:
            The status of the deletion. True for success
            and False for failure.
    """
    deleted = False
    if key not in ["default-logo.png", "default-picture.png"]:
        s3_files = s3.Bucket(S3_BUCKET)
        for _file in s3_files.objects.all():
            if _file.key == 'corr-{0}s/{1}'.format(group, key): 
                _file.delete()
                print "File deleted!"
                deleted = True
                break
        if not deleted:
            print "File not deleted"
    return deleted

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

def web_get_file(url):
    """Retrieve a externaly hosted file.
        Returns:
            File buffer.
    """
    try:
        response = requests.get(url)
        file_buffer = StringIO(response.content)
        file_buffer.seek(0)
        return file_buffer
    except:
        return None


def logTraffic(endpoint=''):
    """Log the traffic on an endpoint.
    """
    (traffic, created) = TrafficModel.objects.get_or_create(service="api", endpoint="%s%s"%(API_URL, endpoint))
    if not created:
        traffic.interactions += 1 
        traffic.save()
    else:
        traffic.interactions = 1
        traffic.save()

def logAccess(app=None, scope='root', endpoint=''):
    """Log the access to the backend.
    """
    (traffic, created) = AccessModel.objects.get_or_create(application=app, scope=scope, endpoint="%s%s"%(API_URL, endpoint))

def logStat(deleted=False, user=None, message=None, application=None, project=None, record=None, diff=None, file_obj=None, comment=None):
    """Log various statistics about different objects:
    number of users, number of projects, number of
    applications, number of messages, number of records,
    number of collaborations, storage usage and number
    of comments. 
    """
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


# import all the api endpoints.
import endpoints
