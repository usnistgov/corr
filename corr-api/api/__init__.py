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
            print("{0} -- {1}.".format(str(application.developer.id), application.name))
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
        print(user_model.group)
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
                        bundle_buffer = storage_get_file('bundle', env.bundle.location)

                    data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print(traceback.print_exc())

            try:
                json_buffer = StringIO()
                json_buffer.write(env.to_json())
                json_buffer.seek(0)

                data = zipfile.ZipInfo("env.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print(traceback.print_exc())
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
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, project_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                comments_buffer = StringIO()
                comments_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                comments_buffer.seek(0)
                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, comments_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                resources_buffer = StringIO()
                resources_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                resources_buffer.seek(0)
                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, resources_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                history_buffer = StringIO()
                history_buffer.write(json.dumps(history, sort_keys=True, indent=4, separators=(',', ': ')))
                history_buffer.seek(0)
                data = zipfile.ZipInfo("environments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, history_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("records.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print(traceback.print_exc())
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(diffs, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("diffs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print(traceback.print_exc())
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
                        bundle_buffer = storage_get_file('bundle', env.bundle.location)

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
                        bundle_buffer = storage_get_file(resource['group'], resource['storage'])
                        data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage']))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print(traceback.print_exc())
            
        memory_file.seek(0)

    return [memory_file, "project-%s-record-%s.zip"%(str(record.project.id), str(record.id))]

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    """Allow crossdomain calls from other domains and port.
        Returns:
            decorator to wrap on the endpoints.
    """
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




# import all the api endpoints.
import api.endpoints
