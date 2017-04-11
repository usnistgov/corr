import flask as fk
from corrdb.common import logAccess, logStat, logTraffic
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import RecordModel
from corrdb.common.models import BundleModel
from corrdb.common.models import VersionModel
from corrdb.common.models import AccessModel
from corrdb.common.models import FileModel
from corrdb.common.models import CommentModel
from corrdb.common.models import MessageModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import DiffModel

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

def query_parse(request=None):
    queries = []
    if request:
        query_parts = request.split("&")
        for query_index in range(len(query_parts)):
            query_pipes = []
            pipe_parts = query_parts[query_index].split("|")
            next_piped = False
            for pipe_index in range(len(pipe_parts)):
                query = {"values":None, "models":None, "tree":False, "piped":False}
                if next_piped:
                    query["piped"] = True
                    next_piped = False
                if len(pipe_parts) - pipe_index - 1 > 0:
                    next_piped = True
                blocks = pipe_parts[pipe_index].split("]")
                if len(blocks) == 3 and "~" in blocks[2]:
                    query["tree"] = True
                if "![" in blocks[0]:
                    index_val = 0
                    index_mod = 1
                else:
                    index_val = 1
                    index_mod = 0
                if blocks[index_val] != "![":
                    query["values"] = blocks[index_val].split("![")[1].split(",")
                if blocks[index_mod] != "?[":
                    query["models"] = blocks[index_mod].split("?[")[1].split(",")
                query_pipes.append(query)
            queries.append(query_pipes)
    return queries

# processRequest("![yannick,sumatra]?[0.user.email,1.file]~|![]?[profile]|![]?[profile]~")

allowed_models = ["user", "version", "record", "project", "file", "profile", "env", "diff", "tool", "bundle"]
relationships = {}
relationships["user"] = ["project", "file", "profile", "tool"]
relationships["version"] = ["env"]
relationships["record"] = ["diff"]
relationships["project"] = ["record"]
relationships["file"] = ["record", "project", "profile", "env", "diff", "tool"]
relationships["profile"] = []
relationships["env"] = ["project", "record"]
relationships["diff"] = []
relationships["tool"] = []
relationships["bundle"] = ["env"]

def query_analyse(queries=None):
    if len(queries) > 0 and len(queries[0]) > 0:
        included = []
        for querie in queries:
            included_here = []
            previous_models = []
            for pipe_index in range(len(querie)):
                pipe = querie[pipe_index]
                current_models = []
                if pipe["models"]:
                    for model_block in pipe["models"]:
                        if "." in model_block:
                            model = None
                            for bl in model_block.split("."):
                                if bl in allowed_models:
                                    model = bl
                                    break
                                else:
                                    try:
                                        value_index = int(bl)
                                        if pipe["values"]:
                                            if len(pipe["values"]) <= value_index:
                                                return (False, "Syntax error. Model referenced value {0} cannot be bigger than the size of the values: {1}.".format(bl, len(pipe["values"])), included)
                                        else:
                                            (False, "Syntax error. Model referenced value {0} does not exist.".format(bl), included)
                                    except:
                                        return (False, "Syntax error. Model referenced value {0} has to be an integer and not a {1}".format(bl, type(bl)), included)
                        else:
                            model = model_block
                        current_models.append(model)
                        if model not in allowed_models:
                            return (False, "Syntax error. Unknown model: {0}\n We only accept: {1}".format(model, allowed_models), included)
                if pipe_index > 0:
                    for model in current_models:
                        if model not in previous_models:
                            return (False, "Context error in piped query. The model: {0} is not in previous scope of models: {1}".format(model, previous_models), included)
                    previous_models = current_models
                else:
                    previous_models = current_models
                if pipe["tree"]:
                    for model in current_models:
                        previous_models.extend(relationships[model])
                    previous_models = list(set(previous_models))
                included_here.append(previous_models)
            included.append(included_here)
    return (True, "Query syntax is correct.", included)

def queryModelGeneric(objectModel, field, value):
    try:
        if field != "*" and value != "*":
            if "," in value:
                if objectModel == RecordModel:
                    return [el for el in objectModel.objects() if any(val.lower() in str(o.extended()["head"][field]).lower() or val.lower() in str(o.extended()["body"][field]).lower() for val in value.split(","))]
                else:
                    return [el for el in objectModel.objects() if any(val.lower() in str(el.info()[field]).lower() for val in value.split(","))]
            else:
                if objectModel == RecordModel:
                    return [o for o in objectModel.objects() if value.lower() in str(o.extended()["head"][field]).lower() or value.lower() in str(o.extended()["body"][field]).lower()]
                else:
                    return [o for o in objectModel.objects() if value.lower() in str(o.info()[field]).lower()]
        elif field == "*" and value != "*":
            if "," in value:
                if objectModel == RecordModel:
                    return [el for el in objectModel.objects() if any(val.lower() in str(el.extended()).lower() for val in value.split(","))]
                else:
                    return [el for el in objectModel.objects() if any(val.lower() in str(el.info()).lower() for val in value.split(","))]
            else:
                if objectModel == RecordModel:
                    return [o for o in objectModel.objects() if value.lower() in str(o.extended()).lower()]
                else:
                    return [o for o in objectModel.objects() if value.lower() in str(o.info()).lower()]
        elif field != "*" and value == "*":
            if objectModel == RecordModel:
                return [o for o in objectModel.objects() if o.extended()[field] != ""]
            else:
                return [o for o in objectModel.objects() if o.info()[field] != ""]
        else:
            return [el for el in objectModel.objects()]
    except:
        return []

def queryContextGeneric(context, name, field, value):
    try:
        if field != "*" and value != "*":
            if "," in value:
                if name == "record":
                    return [el for el in context if any(val.lower() in str(o.extended()['head'][field]).lower() or val.lower() in str(o.extended()['body'][field]).lower() for val in value.split(","))]
                else:
                    return [el for el in context if any(val in str(el.extended()[field]).lower() for val in value.split(","))]
            else:
                if name == "record":
                    return [o for o in context if value.lower() in str(o.extended()['head'][field]).lower() or value.lower() in str(o.extended()['body'][field]).lower()]
                else:
                    return [o for o in context if value.lower() in str(o.extended()[field]).lower()]
        elif field == "*" and value != "*":
            if "," in value:
                return [el for el in context if any(val in str(el.extended()).lower() for val in value.split(","))]
            else:
                return [o for o in context if value.lower() in str(o.extended()).lower()]
        elif field != "*" and value == "*":
            return [o for o in context if o.info()[field] != ""]
        else:
            return context
    except:
        return []

relationships["user"] = ["project", "file", "profile", "tool"]
relationships["version"] = ["env"]
relationships["record"] = ["diff"]
relationships["project"] = ["record"]
relationships["file"] = ["record", "project", "profile", "env", "diff", "tool"]
relationships["profile"] = []
relationships["env"] = ["project", "record"]
relationships["diff"] = []
relationships["tool"] = []
relationships["bundle"] = ["env"]

def fetchDependencies(name, obj):
    deps = {}
    if name == "user":
        profiles = [el for el in ProfileModel.objects(user=obj)]
        deps["profile"] = profiles
        files = [el for el in FileModel.objects(owner=obj)]
        deps["file"] = files
        projects = [el for el in ProjectModel.objects(owner=obj)]
        deps["project"] = projects
        tools = [el for el in ApplicationModel.objects(developer=obj)]
        deps["tool"] = tools
    elif name == "version":
        envs = [el for el in EnvironmentModel.objects(version=obj)]
        deps["env"] = envs
    elif name == "record":
        diffs_from = [el for el in DiffModel.objects(record_from=obj)]
        deps["diff"] = diffs_from
        diffs_to = [el for el in DiffModel.objects(record_to=obj)]
        for rec in diffs_to:
            if rec not in deps["diff"]:
                deps["diff"].append(rec)
    elif name == "project":
        records = [el for el in RecordModel.objects(project=obj)]
        deps["record"] = records
    elif name == "file":
        projects = [pr for pr in ProjectModel.objects() if str(obj.id) in pr.resources]
        logo_projects = [el for el in ProjectModel.objects(logo=obj)]
        for pr in logo_projects:
            if pr not in projects:
                projects.append(pr)
        deps["project"] = projects
        records = [rec for rec in RecordModel.objects() if str(obj.id) in rec.resources]
        deps["record"] = records
        tools = [el for el in ApplicationModel.objects(logo=obj)]
        deps["tool"] = tools
        envs = [env for env in EnvironmentModel.objects() if str(obj.id) in env.resources]
        deps["env"] = envs
        diffs = [dff for dff in DiffModel.objects() if str(obj.id) in dff.resources]
        deps["diff"] = diffs
        profiles = [el for el in ProfileModel.objects(picture=obj)]
        deps["profile"] = profiles
    elif name == "env":
        records = [el for el in RecordModel.objects(environment=obj)]
        deps["record"] = records
        projects = [pr for pr in ProjectModel.objects() if str(obj.id) in pr.history]
        deps["project"] = projects
    elif name == "bundle":
        envs = [el for el in EnvironmentModel.objects(bundle=obj)]
        deps["env"] = envs

    return deps

def queryModel(context, name, field, value):
    if name == "user":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            print(queryModelGeneric(UserModel, field, value))
            return queryModelGeneric(UserModel, field, value)
    elif name == "version":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(VersionModel, field, value)
    elif name == "record":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(RecordModel, field, value)
    elif name == "project":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(ProjectModel, field, value)
    elif name == "file":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(FileModel, field, value)
    elif name == "profile":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(ProfileModel, field, value)
    elif name == "env":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(EnvironmentModel, field, value)
    elif name == "diff":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(DiffModel, field, value)
    elif name == "tool":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(ApplicationModel, field, value)
    elif name == "bundle":
        if context:
            return queryContextGeneric(context[name], name, field, value)
        else:
            return queryModelGeneric(BundleModel, field, value)
    else:
        if context:
            return context
        else:
            return []

def executeQuery(context, query):
    context_current = context
    if query["models"]:
        for model in query["models"]:
            target_value = None
            target_field = None
            target_model = None
            if "." in model:
                blocks = model.split(".")
                for bl_index in range(len(blocks)):
                    if blocks[bl_index] in allowed_models:
                        target_model = blocks[bl_index]
                        if len(blocks) == 2:
                            if bl_index == 0:
                                target_field = blocks[bl_index+1]
                                if query["values"]:
                                    target_value = query["values"]
                                else:
                                    target_value = "*"
                            else:
                                if query["values"]:
                                    target_value = query["values"][bl_index-1]
                                else:
                                    target_value = "*"
                                target_field = "*"
                        if len(blocks) == 3:
                            target_field = blocks[bl_index+1]
                            if query["values"]:
                                target_value = query["values"][bl_index-1]
                            else:
                                target_value = "*"
            else:
                target_model = model
                target_field = "*"
                if query["values"]:
                    target_value = query["values"]
                else:
                    target_value = "*"
            if not query["piped"]:
                objs = queryModel(None, target_model, target_field, target_value)
                for obj in objs:
                    if obj not in context_current[target_model]:
                        context_current[target_model].append(obj)
                        if query["tree"]:
                            deps = fetchDependencies(target_model, obj)
                            for key, value in deps.items():
                                context_current[key].extend(deps[key])
            else:
                context_current[target_model] = queryModel(context_current, target_model, target_field, target_value)
                if query["tree"]:
                    for obj in context_current[target_model]:
                        deps = fetchDependencies(target_model, obj)
                        for key, value in deps.items():
                            context_current[key].extend(deps[key])
            print("?{0}.{1} == {2}".format(target_model, target_field, target_value))
    else:
        target_model = "*"
        target_field = "*"
        if query["values"]:
            target_value = query["values"]
        else:
            target_value = "*"
        if not query["piped"]:
            if target_model == "*":
                for model in allowed_models:
                    objs = queryModel(None, model, target_field, target_value)
                    for obj in objs:
                        if obj not in context_current[model]:
                            context_current[model].append(obj)
                            if query["tree"]:
                                deps = fetchDependencies(model, obj)
                                for key, value in deps.items():
                                    context_current[key].extend(deps[key])
            else:
                objs = queryModel(None, target_model, target_field, target_value)
                for obj in objs:
                    if obj not in context_current[target_model]:
                        context_current[target_model].append(obj)
                        if query["tree"]:
                            deps = fetchDependencies(target_model, obj)
                            for key, value in deps.items():
                                context_current[key].extend(deps[key])
        else:
            if target_model == "*":
                for model in allowed_models:
                    context_current[model] = queryModel(context_current, model, target_field, target_value)
                    if query["tree"]:
                        for obj in context_current[model]:
                            deps = fetchDependencies(model, obj)
                            for key, value in deps.items():
                                context_current[key].extend(deps[key])
            else:
                context_current[target_model] = queryModel(context_current, target_model, target_field, target_value)
                if query["tree"]:
                    for obj in context_current[target_model]:
                        deps = fetchDependencies(target_model, obj)
                        for key, value in deps.items():
                            context_current[key].extend(deps[key])
        print("?{0}.{1} == {2}".format(target_model, target_field, target_value))
    return context_current


def processRequest(request):
    queries = query_parse(request)
    valid, message, included = query_analyse(queries)
    contexts = []
    if valid:
        for query_index in range(len(queries)):
            context = {}
            context["user"] = []
            context["version"] = []
            context["record"] = []
            context["project"] = []
            context["file"] = []
            context["profile"] = []
            context["env"] = []
            context["diff"] = []
            context["tool"] = []
            context["bundle"] = []
            query = queries[query_index]
            for pipe_index in range(len(query)):
                pipe = query[pipe_index]
                context = executeQuery(context, pipe)
            contexts.append(context)
        for context in contexts:
            for key, value in context.items():
                    context[key] = list(set(value))
        return (message, contexts)
    else:
        return (message, None)

def queryResponseDict(contexts):
    contexts_json = []
    if contexts:
        for context in contexts:
            context_json = {}
            for key, value in context.items():
                if key == "record":
                    context_json[key] = [val.extended() for val in value]
                else:
                    context_json[key] = [val.info() for val in value]
            contexts_json.append(context_json)
    return contexts_json


from . import views
from corrdb.common import models
from . import filters
