import flask as fk
from flask_api import status
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
from mongoengine.queryset.visitor import Q

app, storage_manager, access_manager = setup_app(__name__)

CLOUD_VERSION = 0.2
CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

# Stormpath

# from flask.ext.stormpath import StormpathManager

# stormpath_manager = StormpathManager(app)

from datetime import date, timedelta
from functools import update_wrapper

pagination_logs = []

def secure_content(content):
    # security = None
    # for key, value in json.loads(content).items():
    #     security = storage_manager.is_safe(str(value).encode('utf-8'))
    #     if not security[0]:
    #         return security
    # return security
    return [True, "No content. So it is very safe."]

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

def filter2filters(filtr):
    filtrs = []
    if filtr[0] == "true":
        filtrs.append("user")
    if filtr[1] == "true":
        filtrs.append("tool")
    if filtr[2] == "true":
        filtrs.append("project")
    if filtr[3] == "true":
        filtrs.append("record")
    if filtr[4] == "true":
        filtrs.append("diff")
    if filtr[5] == "true":
        filtrs.append("env")
    pagination_logs.append("{0} -- filter2filters: {1}".format(datetime.datetime.utcnow(), filtrs))
    return filtrs

def raw2dict(raw, page):
    block_size = 45
    begin = page*block_size
    end = begin + block_size
    results = {'user':[], 'tool':[], 'project':[], 'record':[], 'diff':[], 'env':[]}
    if begin > len(raw):
        return 0, results
    else:
        if end > len(raw):
            page_block = raw[begin:]
        else:
            page_block = raw[begin:end]
        for r in page_block:
            if isinstance(r, UserModel):
                results['user'].append(r)
            elif isinstance(r, ApplicationModel):
                results['tool'].append(r)
            elif isinstance(r, ProjectModel):
                results['project'].append(r)
            elif isinstance(r, RecordModel):
                results['record'].append(r)
            elif isinstance(r, DiffModel):
                results['diff'].append(r)
            elif isinstance(r, EnvironmentModel):
                results['env'].append(r)
        pagination_logs.append("{0} -- raw2dict: {1}, {2}".format(datetime.datetime.utcnow(), len(page_block), results))
        return len(page_block), results


def query_basic(words, page, filtr, current_user):
    filtrs = filter2filters(filtr)
    raw = []
    if "user" not in filtrs:
        raw.extend([u for u in UserModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words)])
        # _users = UserModel.objects(Q(email__in=words)|Q(email__in=words)|)
        # _users_P = ProfileModel.objects()
        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    if "tool" not in filtrs:
        raw.extend([u for u in ApplicationModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words)])
        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    if "project" not in filtrs:
        raw.extend([u for u in ProjectModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words) and (u.access == 'public' or current_user and (current_user == u.owner or current_user.group == "admin"))])

        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    if "record" not in filtrs:
        raw.extend([u for u in RecordModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words) and (u.access == 'public' or (current_user and u.project) and (current_user == u.project.owner or current_user.group == "admin"))])
        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    if "diff" not in filtrs:
        raw.extend([u for u in DiffModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words) and ((u.record_from.access == 'public' and u.record_to.access == 'public') or (current_user and (current_user.group == "admin" or current_user == u.record_from.project.owner or current_user == u.record_to.project.owner)))])
        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    if "env" not in filtrs:
        raw.extend([u for u in EnvironmentModel.objects().order_by('+created_at') if all(w in str(u.extended()).lower() for w in words) and (len(ProjectModel.objects(history=str(u.id))) > 0 and (ProjectModel.objects(history=str(u.id))[0].access == 'public' or current_user and (current_user == ProjectModel.objects(history=str(u.id))[0].owner or current_user.group == "admin")))])
        pagination_logs.append("{0} -- query_basic: {1}".format(datetime.datetime.utcnow(), raw))
    return raw2dict(raw, page)


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

# allowed_models = ["user", "version", "record", "project", "file", "profile", "env", "diff", "tool", "bundle"]
allowed_models = ["user", "tool", "project", "record", "env", "diff"]

relationships = {}
# relationships["user"] = ["project", "file", "profile", "tool"]
relationships["user"] = ["tool", "project"]
relationships["version"] = ["env"]
relationships["record"] = ["diff"]
relationships["project"] = ["record"]
# relationships["file"] = ["record", "project", "profile", "env", "diff", "tool"]
# relationships["profile"] = []
relationships["env"] = ["project", "record"]
relationships["diff"] = []
relationships["tool"] = []
# relationships["bundle"] = ["env"]

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

def queryModelGeneric(objectModel, field, value, offset, leftover):
    # try:
    if field != "*" and value != "*":
        if len(value) > 0:
            if objectModel == RecordModel:
                els = [el for el in objectModel.objects if any(val.lower() in str(o.extended()["head"][field]).lower() or val.lower() in str(o.extended()["body"][field]).lower() for val in value)]
            else:
                els = [el for el in objectModel.objects if any(val.lower() in str(el.info()[field]).lower() for val in value)]
        else:
            if objectModel == RecordModel:
                els = [o for o in objectModel.objects if value.lower() in str(o.extended()["head"][field]).lower() or value.lower() in str(o.extended()["body"][field]).lower()]
            else:
                els = [o for o in objectModel.objects if value.lower() in str(o.info()[field]).lower()]
    elif field == "*" and value != "*":
        if len(value) > 0:
            if objectModel == RecordModel:
                els = [el for el in objectModel.objects if any(val.lower() in str(el.extended()).lower() for val in value)]
            else:
                els = [el for el in objectModel.objects if any(val.lower() in str(el.info()).lower() for val in value)]
        else:
            if objectModel == RecordModel:
                els = [o for o in objectModel.objects if value.lower() in str(o.extended()).lower()]
            else:
                els = [o for o in objectModel.objects if value.lower() in str(o.info()).lower()]
    elif field != "*" and value == "*":
        if objectModel == RecordModel:
            els = [o for o in objectModel.objects if o.extended()[field] != ""]
        else:
            els = [o for o in objectModel.objects if o.info()[field] != ""]
    else:
        els = [el for el in objectModel.objects]

    if objectModel == ProfileModel:
        els = [el.user for el in els]

    size = len(els)
    if size == 0:
        return [], size
    else:
        if size > offset:
            if offset > 0:
                left = size-offset
                if left > leftover:
                    return els[offset:offset+leftover], offset
                else:
                    return els[offset:offset+left], offset
            else:
                if size > leftover:
                    return els[:leftover], leftover
                else:
                    return els, size
        else:
            return [], size

    # except:
    #     return []

def queryContextGeneric(context, name, field, value, offset, leftover):
    # try:
    if field != "*" and value != "*":
        if len(value) > 0:
            if name == "record":
                els = [el for el in context if any(val.lower() in str(o.extended()['head'][field]).lower() or val.lower() in str(o.extended()['body'][field]).lower() for val in value)]
            else:
                els = [el for el in context if any(val in str(el.extended()[field]).lower() for val in value)]
        else:
            if name == "record":
                els = [o for o in context if value.lower() in str(o.extended()['head'][field]).lower() or value.lower() in str(o.extended()['body'][field]).lower()]
            else:
                els = [o for o in context if value.lower() in str(o.extended()[field]).lower()]
    elif field == "*" and value != "*":
        if len(value) > 0:
            els = [el for el in context if any(val in str(el.extended()).lower() for val in value)]
        else:
            els = [o for o in context if value.lower() in str(o.extended()).lower()]
    elif field != "*" and value == "*":
        els = [o for o in context if o.info()[field] != ""]
    else:
        els = []
    # if name == "profile":
    #     els = [el.user for el in els]
    size = len(els)
    if size == 0:
        return [], size
    else:
        if size > offset:
            if offset > 0:
                left = size-offset
                if left > leftover:
                    return els[offset:offset+leftover], offset
                else:
                    return els[offset:offset+left], offset
            else:
                if size > leftover:
                    return els[:leftover], leftover
                else:
                    return els, size
        else:
            return [], size

# relationships["user"] = ["project", "file", "profile", "tool"]
# # relationships["version"] = ["env"]
# relationships["record"] = ["diff"]
# relationships["project"] = ["record"]
# # relationships["file"] = ["record", "project", "profile", "env", "diff", "tool"]
# relationships["profile"] = []
# relationships["env"] = ["project", "record"]
# relationships["diff"] = []
# relationships["tool"] = []
# relationships["bundle"] = ["env"]

def paginate(query, offset, leftover, size):
    if leftover == 0:
        return [], size + 0, offset, leftover
    else:
        if len(query) > offset:
            end = offset + leftover
            if len(query) >= end:
                filtered = query[offset:end]
                return filtered, size + leftover, end, 0
            else:
                filtered = query[offset:]
                return filtered, size + len(filtered), end, leftover-len(filtered)
        else:
            return [], size + len(query), offset, leftover


def fetchDependencies(name, obj, offset, leftover, filtrs):
    deps = {}
    size = 0
    if name == "user":
        # profiles, size, offset, leftover = paginate(ProfileModel.objects(user=obj), offset, leftover, size)
        # deps["profile"] = profiles
        if "file" not in filtrs:
            files, size, offset, leftover = paginate(FileModel.objects(owner=obj), offset, leftover, size)
            deps["file"] = files
        if "project" not in filtrs:
            projects, size, offset, leftover = paginate(ProjectModel.objects(owner=obj), offset, leftover, size)
            deps["project"] = projects
        if "tool" not in filtrs:
            tools, size, offset, leftover = paginate(ApplicationModel.objects(developer=obj), offset, leftover, size)
            deps["tool"] = tools
    # elif name == "version":
    #     if "env" not in filtrs:
    #         envs, size, offset, leftover = paginate(EnvironmentModel.objects(version=obj), offset, leftover, size)
    #         deps["env"] = envs
    elif name == "record":
        if "diff" not in filtrs:
            diffs_from, size, offset, leftover = paginate(DiffModel.objects(record_from=obj), offset, leftover, size)
            deps["diff"] = diffs_from
            diffs_to = [el for el in DiffModel.objects(record_to=obj)]
            diffs_more = []
            for rec in diffs_to:
                if rec not in deps["diff"]:
                    diffs_more.append(rec)
            diffs_more, size, offset, leftover = paginate(diffs_more, offset, leftover, size)
            deps["diff"].extend(diffs_more)
    elif name == "project":
        if "record" not in filtrs:
            records, size, offset, leftover = paginate(RecordModel.objects(project=obj), offset, leftover, size)
            deps["record"] = records
    # elif name == "file":
    #     projects = [pr for pr in ProjectModel.objects() if str(obj.id) in pr.resources]
    #     logo_projects = [el for el in ProjectModel.objects(logo=obj)]
    #     for pr in logo_projects:
    #         if pr not in projects:
    #             projects.append(pr)
    #     projects, size, offset, leftover = paginate(projects, offset, leftover, size)
    #     deps["project"] = projects

    #     records = [rec for rec in RecordModel.objects() if str(obj.id) in rec.resources]
    #     records, size, offset, leftover = paginate(records, offset, leftover, size)
    #     deps["record"] = records

    #     tools, size, offset, leftover = paginate(ApplicationModel.objects(logo=obj), offset, leftover, size)
    #     deps["tool"] = tools

    #     envs = [env for env in EnvironmentModel.objects() if str(obj.id) in env.resources]
    #     envs, size, offset, leftover = paginate(envs, offset, leftover, size)
    #     deps["env"] = envs

    #     diffs = [dff for dff in DiffModel.objects() if str(obj.id) in dff.resources]
    #     diffs, size, offset, leftover = paginate(diffs, offset, leftover, size)
    #     deps["diff"] = diffs

    #     profiles, size, offset, leftover = paginate(ProfileModel.objects(picture=obj), offset, leftover, size)
    #     deps["profile"] = profiles
    elif name == "env":
        if "record" not in filtrs:
            records, size, offset, leftover = paginate(RecordModel.objects(environment=obj), offset, leftover, size)
            deps["record"] = records

        if "project" not in filtrs:
            projects = [pr for pr in ProjectModel.objects if str(obj.id) in pr.history]
            projects, size, offset, leftover = paginate(projects, offset, leftover, size)
            deps["project"] = projects
    # elif name == "bundle":
    #     envs, size, offset, leftover = paginate(EnvironmentModel.objects(bundle=obj), offset, leftover, size)
    #     deps["env"] = envs
    pagination_logs.append("{0} -- fetchDependencies: {1}, {2}, {3}, {4}".format(datetime.datetime.utcnow(), size, offset, leftover))
    return deps, size, offset, leftover

def queryModel(context, name, field, value, offset, leftover, filtrs):
    if name in filtrs:
        if context:
            els = context
            size = 0
        else:
            els = []
            size = 0
        return els, size
    else:
        if name == "user":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(UserModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        # elif name == "version":
        #     if context:
        #         els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        #     else:
        #         els, size = queryModelGeneric(VersionModel, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        elif name == "record":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(RecordModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        elif name == "project":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(ProjectModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        # elif name == "file":
        #     if context:
        #         els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        #     else:
        #         els, size = queryModelGeneric(FileModel, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        # elif name == "profile":
        #     if context:
        #         els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        #     else:
        #         els, size = queryModelGeneric(ProfileModel, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        elif name == "env":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(EnvironmentModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        elif name == "diff":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(DiffModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        elif name == "tool":
            if context:
                els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
            else:
                els, size = queryModelGeneric(ApplicationModel, field, value, offset, leftover)
                pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        # elif name == "bundle":
        #     if context:
        #         els, size = queryContextGeneric(context[name], name, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryContextGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        #     else:
        #         els, size = queryModelGeneric(BundleModel, field, value, offset, leftover)
        #         pagination_logs.append("{0} -- queryModelGeneric: {1}, {2}".format(datetime.datetime.utcnow(), els, size))
        else:
            if context:
                els = context
                size = 0
            else:
                els = []
                size = 0
        return els, size

def executeQuery(context, query, page, history, leftover, filtrs):
    context_current = context
    block_size = 45
    offset = page * block_size
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
            if leftover > 0:
                if not query["piped"]:
                    objs, size = queryModel(None, target_model, target_field, target_value, offset, leftover, filtrs)
                    counter = 0
                    for obj in objs:
                        if obj not in context_current[target_model]:
                            # if target_model == "profile":
                            #     context_current["user"].append(obj)
                            # else:
                            context_current[target_model].append(obj)
                            counter = counter + 1
                    leftover = leftover - counter
                    history = history + size + counter
                    offset = page * block_size - history
                    if query["tree"]:
                        for obj in context_current[target_model]:
                            deps, size, offset, leftover = fetchDependencies(target_model, obj, offset, leftover, filtrs)
                            for key, value in deps.items():
                                # if key == "profile":
                                #     context_current["user"].append(deps[key])
                                # else:
                                context_current[key].extend(deps[key])
                                counter = counter + 1
                            leftover = leftover - counter
                            history = history + size + counter
                            offset = page * block_size - history
                else:
                    context_current[target_model], size = queryModel(context_current, target_model, target_field, target_value, offset, leftover, filtrs)
                    if query["tree"]:
                        counter = 0
                        for obj in context_current[target_model]:
                            deps, size, offset, leftover = fetchDependencies(target_model, obj, offset, leftover, filtrs)
                            for key, value in deps.items():
                                # if key == "profile":
                                #     context_current["user"].append(deps[key])
                                # else:
                                context_current[key].extend(deps[key])
                                counter = counter + 1
                            leftover = leftover - counter
                            history = history + size + counter
                            offset = page * block_size - history
            pagination_logs.append("{0} -- executeQuery: {1}, {2}, {3}".format(datetime.datetime.utcnow(), leftover, history, offset))
            print("?{0}.{1} == {2}".format(target_model, target_field, target_value))
    else:
        target_model = "*"
        target_field = "*"
        if query["values"]:
            target_value = query["values"]
        else:
            target_value = "*"

        if not query["piped"]:
            for model in allowed_models:
                counter = 0
                objs, size = queryModel(None, model, target_field, target_value, offset, leftover, filtrs)
                for obj in objs:
                    if obj not in context_current[model]:
                        # if target_model == "profile":
                        #     context_current["user"].append(obj)
                        # else:
                        context_current[model].append(obj)
                        counter = counter + 1
                leftover = leftover - counter
                history = history + size + counter
                offset = page * block_size - history
                if query["tree"]:
                    for obj in context_current[model]:
                        deps, size, offset, leftover = fetchDependencies(model, obj, offset, leftover, filtrs)
                        for key, value in deps.items():
                            # if key == "profile":
                            #     context_current["user"].append(deps[key])
                            # else:
                            context_current[key].extend(deps[key])
                            counter = counter + 1
                        leftover = leftover - counter
                        history = history + size + counter
                        offset = page * block_size - history
        else:
            for model in allowed_models:
                counter = 0
                context_current[model], size = queryModel(context_current, model, target_field, target_value, offset, leftover, filtrs)
                if query["tree"]:
                    for obj in context_current[model]:
                        deps, size, offset, leftover = fetchDependencies(model, obj, offset, leftover, filtrs)
                        for key, value in deps.items():
                            # if key == "profile":
                            #     context_current["user"].append(deps[key])
                            # else:
                            context_current[key].extend(deps[key])
                            counter = counter + 1
                        leftover = leftover - counter
                        history = history + size + counter
                        offset = page * block_size - history
        pagination_logs.append("{0} -- executeQuery: {1}, {2}, {3}".format(datetime.datetime.utcnow(), leftover, history, offset))
    return context_current, history, leftover


def processRequest(request, page, filtr):
    queries = query_parse(request)
    valid, message, included = query_analyse(queries)
    contexts = []
    history = 0
    leftover = 45
    if valid:
        for query_index in range(len(queries)):
            context = {}
            context["user"] = []
            # context["version"] = []
            context["tool"] = []
            context["project"] = []
            context["record"] = []

            # context["file"] = []
            # context["profile"] = []
            context["env"] = []
            context["diff"] = []

            # context["bundle"] = []
            filtrs = []

            if filtr[0] == "true":
                filtrs.append("user")
            if filtr[1] == "true":
                filtrs.append("tool")
            if filtr[2] == "true":
                filtrs.append("project")
            if filtr[3] == "true":
                filtrs.append("record")
            if filtr[4] == "true":
                filtrs.append("diff")
            if filtr[5] == "true":
                filtrs.append("env")

            query = queries[query_index]
            for pipe_index in range(len(query)):
                pipe = query[pipe_index]
                context, history, leftover = executeQuery(context, pipe, page, history, leftover, filtrs)
                if leftover == 0:
                    break
            contexts.append(context)
        for context in contexts:
            for key, value in context.items():
                    context[key] = list(set(value))
        return ("{0} {1}".format(message,queries), contexts, leftover)
    else:
        return ("{0} {1}".format(message,queries), None, leftover)

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
