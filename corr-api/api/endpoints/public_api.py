import json

from flask.ext.api import status
import flask as fk

from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from api import app, storage_manager, access_manager, API_URL, api_response, data_pop, merge_dicts
from corrdb.common.models import UserModel
from corrdb.common.models import AccessModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import FileModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import StatModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import RecordModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import DiffModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import CommentModel
from corrdb.common.models import MessageModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import BundleModel
from corrdb.common.models import VersionModel

import mimetypes
import simplejson as json
import traceback
import datetime
import random
import string
import os
import _thread

@app.route(API_URL + '/public/api/status', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_api_status():
    logTraffic(API_URL, endpoint='/public/api/status')
    if fk.request.method == 'GET':
        # Maybe perform some sanity checks
        return api_response(200, 'API reached', 'This CoRR API instance is up and running')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/app/show/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_app_show(app_id):
    logTraffic(API_URL, endpoint='/public/app/show/<app_id>')
    if fk.request.method == 'GET':
        app = ApplicationModel.objects.with_id(app_id)
        if app == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
        else:
            return api_response(200, 'Application %s'%app.name, app.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/app/logo/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_app_logo(app_id):
    logTraffic(API_URL, endpoint='/public/app/logo/<app_id>')
    if fk.request.method == 'GET':
        app = ApplicationModel.objects.with_id(app_id)
        if app != None:
            name = app.name if app.name != '' and app.name != None else 'unknown'
            logo = app.logo
            if logo.location == 'local' and ('http://' not in logo.storage and 'https://' not in logo.storage):
                logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                if logo_buffer == None:
                    return api_response(404, 'No logo found', 'We could not fetch the logo at [%s].'%logo.storage)
                else:
                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            elif logo.location == 'remote':
                logo_buffer = storage_manager.web_get_file(logo.storage)
                if logo_buffer != None:
                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            else:
                # solve the file situation and return the appropriate one.
                if 'http://' in logo.storage or 'https://' in logo.storage:
                    logo.location = 'remote'
                    logo.save()
                    logo_buffer = storage_manager.web_get_file(logo.storage)
                    if logo_buffer != None:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    logo.location = 'local'
                    logo.save()
                    logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
        else:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/users', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_users():
    logTraffic(API_URL, endpoint='/public/users')
    if fk.request.method == 'GET':
        users = UserModel.objects()
        users_dict = {'total_users':len(users), 'users':[]}
        for user in users:
            users_dict['users'].append(user.extended())
        return api_response(200, 'Users list', users_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/user/show/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_user_show(user_id):
    logTraffic(API_URL, endpoint='/public/user/show/<user_id>')
    if fk.request.method == 'GET':
        user = UserModel.objects.with_id(user_id)
        if user == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
        else:
            return api_response(200, 'User %s account'%user.email, user.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/user/profile/show/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_user_profile_show(user_id):
    logTraffic(API_URL, endpoint='/public/user/profile/show/<user_id>')
    if fk.request.method == 'GET':
        user = UserModel.objects.with_id(user_id)
        if user == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
        else:
            profile = ProfileModel.objects(user=user).first()
            if profile == None:
                return api_response(404, 'User %s profile is empty'%user.email, 'You have to create a profile for this user.')
            else:
                return api_response(200, 'User %s profile'%user.email, profile.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/user/picture/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_user_picture(user_id):
    logTraffic(API_URL, endpoint='/public/user/picture/<user_id>')
    if fk.request.method == 'GET':
        user = UserModel.objects.with_id(user_id)
        if user != None:
            profile = ProfileModel.objects(user=user).first()
            if profile == None:
                picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                if picture_buffer == None:
                    return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                else:
                    return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
            else:
                picture = profile.picture
                if picture == None:
                    picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                    if picture_buffer == None:
                        return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                elif picture.location == 'local' and ('http://' not in picture.storage and 'https://' not in picture.storage):
                    picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                    if picture_buffer == None:
                        return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%logo.storage)
                    else:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                elif picture.location == 'remote':
                    picture_buffer = storage_manager.web_get_file(picture.storage)
                    if picture_buffer != None:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                        if picture_buffer == None:
                            return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                else:
                    # solve the file situation and return the appropriate one.
                    if 'http://' in picture.storage or 'https://' in picture.storage:
                        picture.location = 'remote'
                        picture.save()
                        picture_buffer = storage_manager.web_get_file(picture.storage)
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                            if picture_buffer == None:
                                return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                            else:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        picture.location = 'local'
                        picture.save()
                        picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                        if picture_buffer == None:
                            return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
        else:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/user/projects/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_user_projects(user_id):
    logTraffic(API_URL, endpoint='/public/user/projects')
    if fk.request.method == 'GET':
        user = UserModel.objects.with_id(user_id)
        if user == None:
            return api_response(404, 'No user found', 'We could not fetch the user with id:%s.'%user_id)
        projects = ProjectModel.objects(owner=user)
        projects_dict = {'total_projects':len(projects), 'projects':[]}
        for project in projects:
            projects_dict['projects'].append(project.extended())
        return api_response(200, 'Projects list', projects_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_projects():
    logTraffic(API_URL, endpoint='/public/projects')
    if fk.request.method == 'GET':
        projects = ProjectModel.objects()
        projects_dict = {'total_projects':len(projects), 'projects':[]}
        for project in projects:
            if project.access == 'public':
                projects_dict['projects'].append(project.extended())
        return api_response(200, 'Projects list', projects_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_comments(project_id):
    logTraffic(API_URL, endpoint='/public/project/comments/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            comments = project._comments()
            comments_dict = {'total_comments':0, 'comments':[]}
            for comment_id in comments:
                comment = CommentModel.objects.with_id(comment_id)
                if comment != None:
                    comments_dict['comments'].append(comment.info())
            comments_dict['total_comments'] = len(comments_dict['comments'])
            return api_response(200, 'Project comment list', comments_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/comment/show/<comment_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_comment_show(comment_id):
    logTraffic(API_URL, endpoint='/public/comment/show/<comment_id>')
    if fk.request.method == 'GET':
        comment = CommentModel.objects.with_id(comment_id)
        if comment == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this comment.')
        else:
            return api_response(200, 'Project %s info'%comment_id, comment.info())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_records(project_id):
    logTraffic(API_URL, endpoint='/public/project/records/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            records = RecordModel.objects(project=project)
            records_dict = {'total_records':len(records), 'records':[]}
            for record in records:
                records_dict['records'].append(record.extended())
            return api_response(200, 'Project [%s] Records list'%project.name, records_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/show/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_show(project_id):
    logTraffic(API_URL, endpoint='/public/project/show/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            return api_response(200, 'Project %s'%project.name, project.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/logo/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_logo(project_id):
    logTraffic(API_URL, endpoint='/public/project/logo/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project != None:
            logo = project.logo
            if logo.location == 'local' and 'http://' not in logo.storage and 'https://' not in logo.storage:
                logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                if logo_buffer == None:
                    return api_response(404, 'No logo found', 'We could not fetch the logo at [%s].'%logo.storage)
                else:
                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            elif logo.location == 'remote':
                logo_buffer = storage_manager.web_get_file(logo.storage)
                if logo_buffer != None:
                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            else:
                # solve the file situation and return the appropriate one.
                if 'http://' in logo.storage or 'https://' in logo.storage:
                    logo.location = 'remote'
                    logo.save()
                    logo_buffer = storage_manager.web_get_file(logo.storage)
                    if logo_buffer != None:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    logo.location = 'local'
                    logo.save()
                    logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
        else:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/download/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_download(project_id):
    logTraffic(API_URL, endpoint='/public/project/download/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            prepared = storage_manager.prepare_project(project)
            if prepared[0] == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
            else:
                return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/history/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_history(project_id):
    logTraffic(API_URL, endpoint='/public/project/envs/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            history_dict = {'total_environments':0, 'environments':[]}
            for env_dict in project.history:
                env = EnvironmentModel.objects.with_id(env_dict)
                if env != None:
                    history_dict['environments'].append(env.info())
            history_dict['total_environments'] = len(history_dict['environments'])
            return api_response(200, 'Project %s environments'%project.name, history_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/envs/head/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_envs_head(project_id):
    logTraffic(API_URL, endpoint='/public/project/envs/head')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            head = {}
            if len(project.history) > 0:
                head = project.history[-1]
            return api_response(200, 'Project %s environments head'%project.name, head)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/env/show/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_env_show(project_id, env_id):
    logTraffic(API_URL, endpoint='/public/project/env/show/<project_id>/<env_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            if env_id not in project.history:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
            else:
                env = EnvironmentModel.objects.with_id(env_id)
                if env == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                else:
                    return api_response(200, 'Project %s environment %s'%(project.name, env_id), env.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/project/env/download/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_env_download(project_id, env_id):
    logTraffic(API_URL, endpoint='/public/project/env/download/<project_id>/<env_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
        else:
            if env_id not in project.history:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
            else:
                env = EnvironmentModel.objects.with_id(env_id)
                if env == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                else:
                    prepared = storage_manager.prepare_env(project, env)
                    if prepared[0] == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                    else:
                        return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/records', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_records():
    logTraffic(API_URL, endpoint='/public/records')
    if fk.request.method == 'GET':
        records = RecordModel.objects()
        records_dict = {'total_records':len(records), 'records':[]}
        for record in records:
            records_dict['records'].append(record.extended())
        return api_response(200, 'Records list', records_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/record/show/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_record_show(record_id):
    logTraffic(API_URL, endpoint='/public/record/show/<record_id>')
    if fk.request.method == 'GET':
        record = RecordModel.objects.with_id(record_id)
        if record == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
        else:
            return api_response(200, 'Record info', record.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/record/download/<project_id>/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_record_download(project_id, record_id):
    logTraffic(API_URL, endpoint='/public/record/download/<project_id>/<record_id>')
    if fk.request.method == 'GET':
        record = RecordModel.objects.with_id(record_id)
        if record == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
        else:
            if str(record.project.id) != project_id:
                return api_response(401, 'Unauthorized access to this record', 'This record is not part of the provided project.')
            else:
                prepared = storage_manager.prepare_record(record)
                if prepared[0] == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to retrieve a record to download.')
                else:
                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/diffs', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_diffs():
    logTraffic(API_URL, endpoint='/public/diffs')
    if fk.request.method == 'GET':
        diffs = DiffModel.objects()
        diffs_dict = {'total_diffs':len(diffs), 'diffs':[]}
        for diff in diffs:
            diffs_dict['diffs'].append(diff.extended())
        return api_response(200, 'Diffs list', diffs_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/diff/show/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_diff_show(diff_id):
    logTraffic(API_URL, endpoint='/public/diff/show/<diff_id>')
    if fk.request.method == 'GET':
        diff = DiffModel.objects.with_id(diff_id)
        if diff == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
        else:
            return api_response(200, 'Diff info', diff.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/files', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_files():
    logTraffic(API_URL, endpoint='/public/files')
    if fk.request.method == 'GET':
        files = FileModel.objects()
        files_dict = {'total_files':len(files), 'files':[]}
        for _file in files:
            files_dict['files'].append(_file.extended())
        return api_response(200, 'Files list', files_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_file_download(file_id):
    logTraffic(API_URL, endpoint='/public/file/download/<file_id>')
    if fk.request.method == 'GET':
        file_meta = FileModel.objects.with_id(file_id)
        if file_meta == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            file_obj = None
            if file_meta.location == 'remote':
                file_obj = storage_manager.web_get_file(file_meta.storage)
            elif file_meta.location == 'local':
                file_obj = storage_manager.storage_get_file(file_meta.group, file_meta.storage)

            if file_obj == None:
                return api_response(404, 'Request suggested an empty response', 'No content found for this file.')
            else:
                # return fk.send_file(
                #     file_obj,
                #     file_meta.mimetype,
                #     # as_attachment=True,
                #     attachment_filename=file_meta.name,
                # )
                if file_meta.group == 'logo' or file_meta.group == 'picture':
                    return fk.send_file(
                        file_obj,
                        file_meta.mimetype,
                        # as_attachment=True,
                        attachment_filename=file_meta.name,
                    )
                else:
                    if file_meta.name.split('.')[1] in ['jpg', 'pdf', 'txt']:
                        return fk.send_file(
                            file_obj,
                            file_meta.mimetype,
                            # as_attachment=True,
                            attachment_filename=file_meta.name,
                        )
                    else:
                        # Check the mimetype for media files to just provide them without attachment.
                        return fk.send_file(
                                file_obj,
                                file_meta.mimetype,
                                as_attachment=True,
                                attachment_filename=file_meta.name,
                            )

        if fk.request.data:
            data = json.loads(fk.request.data)
            encoding = data.get('developer', '')
            size = data.get('developer', 0)
            name = data.get('developer', '')
            path = data.get('developer', '')
            storage = data.get('developer', '')
            location = data.get('location', 'undefined')
            mimetype = data.get('developer', mimetypes.guess_type(location)[0])
            group = data.get('group', 'undefined')
            description = data.get('description', '')
            if storage == '' or name == '':
                return api_response(400, 'Missing mandatory fields', 'A file should have at least a name and a storage reference (s3 key or url).')
            else:
                _file, created = FileModel.objects.get_or_create(encoding=encoding, name=name, mimetype=mimetype, size=size, path=path, storage=storage, location=location, group=group, description=description)
                if not created:
                    return api_response(200, 'File already exists', _file.info())
                else:
                    return api_response(201, 'File created', _file.info())
        else:
            return api_response(204, 'Nothing created', 'You must provide the file information.')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/file/show/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_file_show(file_id):
    logTraffic(API_URL, endpoint='/public/file/show/<file_id>')
    if fk.request.method == 'GET':
        _file = FileModel.objects.with_id(file_id)
        if _file == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
        else:
            return api_response(200, 'File %s'%_file.name, _file.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/messages', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_messages():
    logTraffic(API_URL, endpoint='/public/messages')
    if fk.request.method == 'GET':
        messages = MessageModel.objects()
        messages_dict = {'total_messages':len(messages), 'messages':[]}
        for message in messages:
            messages_dict['messages'].append(message.extended())
        return api_response(200, 'Messages list', messages_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/message/show/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_message_show(message_id):
    logTraffic(API_URL, endpoint='/public/message/show/<message_id>')
    if fk.request.method == 'GET':
        message = MessageModel.objects.with_id(message_id)
        if message == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
        else:
            return api_response(200, 'Message %s'%str(message.id), message.extended())
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/search/<key_words>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_search(key_words):
    logTraffic(API_URL, endpoint='/public/search/<key_words>')
    if fk.request.method == 'GET':
        results = {'results':{}, 'total-results':0}
        results['results']['users'] = {'users-list':[], 'users-total':0}
        results['results']['apps'] = {'apps-list':[], 'apps-total':0}
        results['results']['projects'] = {'projects-list':[], 'projects-total':0}
        results['results']['records'] = {'records-list':[], 'records-total':0}
        results['results']['envs'] = {'envs-list':[], 'envs-total':0}
        results['results']['bundles'] = {'bundles-list':[], 'bundles-total':0}
        results['results']['files'] = {'files-list':[], 'files-total':0}
        results['results']['versions'] = {'versions-list':[], 'versions-total':0}

        words = key_words.split('-')

        for user in UserModel.objects():
            exists = [False for word in words]
            condition = [True for word in words]
            profile = ProfileModel.objects(user=user).first()
            index = 0
            for word in words:
                if word != '':
                    if profile != None:
                        try:
                            if word.lower() in user.email.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in profile.fname.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in profile.lname.lower():
                                exists[index] = True
                        except:
                            pass
                else:
                    exists[index] = True
                index += 1
            if exists == condition:
                results['results']['users']['users-list'].append({'user':user.info(), 'profile':profile.info()})
            results['results']['users']['users-total'] = len(results['results']['users']['users-list'])

        for app in ApplicationModel.objects():
            exists = [False for word in words]
            condition = [True for word in words]
            index = 0
            for word in words:
                if word != '':
                    try:
                        if word.lower() in app.possible_access.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in app.network.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in app.storage.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in app.about.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in app.name.lower():
                            exists[index] = True
                    except:
                        pass
                else:
                    exists[index] = True
                index += 1
            if exists == condition:
                results['results']['apps']['apps-list'].append(app.info())
            results['results']['apps']['apps-total'] = len(results['results']['apps']['apps-list'])

        for project in ProjectModel.objects():
            if project.access == "public":
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in project.name.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.description.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.goals.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(project.tags).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.access.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.group.lower():
                                exists[index] = True
                        except:
                            pass
                        
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['projects']['projects-list'].append(project.info())
                results['results']['projects']['projects-total'] = len(results['results']['projects']['projects-list'])

        for record in RecordModel.objects():
            if record.access == "public":
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in record.label.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.tags).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.system).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.execution).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.preparation).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.inputs).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.outputs).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.dependencies).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in record.status.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in record.access.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.rationels).lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['records']['records-list'].append(record.info())
                results['results']['records']['records-total'] = len(results['results']['records']['records-list'])

        for env in EnvironmentModel.objects():
            exists = [False for word in words]
            condition = [True for word in words]
            index = 0
            for word in words:
                if word != '':
                    try:
                        if word.lower() in env.group.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in env.system.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in str(env.specifics).lower():
                            exists[index] = True
                    except:
                        pass
                else:
                    exists[index] = True
                index += 1
            if exists == condition:
                results['results']['envs']['envs-list'].append(env.info())
            results['results']['envs']['envs-total'] = len(results['results']['envs']['envs-list'])

        for bundle in BundleModel.objects():
            exists = [False for word in words]
            condition = [True for word in words]
            index = 0
            for word in words:
                if word != '':
                    try:
                        if word.lower() in bundle.scope.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in bundle.location.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in bundle.mimetype.lower():
                            exists[index] = True
                    except:
                        pass
                else:
                    exists[index] = True
                index += 1
            if exists == condition:
                results['results']['bundles']['bundles-list'].append(bundle.info())
            results['results']['bundles']['bundles-total'] = len(results['results']['bundles']['bundles-list'])

        for file_ in FileModel.objects():
            if file_.owner == None:
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in file_.mimetype.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.name.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.path.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.storage.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.location.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.group.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.description.lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['files']['files-list'].append(file_.info())
                results['results']['files']['files-total'] = len(results['results']['files']['files-list'])

        for version in VersionModel.objects():
            exists = [False for word in words]
            condition = [True for word in words]
            index = 0
            for word in words:
                if word != '':
                    try:
                        if word.lower() in version.system.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in version.baseline.lower():
                            exists[index] = True
                    except:
                        pass
                    try:
                        if word.lower() in version.marker.lower():
                            exists[index] = True
                    except:
                        pass
                else:
                    exists[index] = True
                index += 1
            if exists == condition:
                results['results']['versions']['versions-list'].append(version.info())
            results['results']['versions']['versions-total'] = len(results['results']['versions']['versions-list'])

        results['total-results'] += results['results']['users']['users-total']
        results['total-results'] += results['results']['apps']['apps-total']
        results['total-results'] += results['results']['projects']['projects-total']
        results['total-results'] += results['results']['records']['records-total']
        results['total-results'] += results['results']['envs']['envs-total']
        results['total-results'] += results['results']['bundles']['bundles-total']
        results['total-results'] += results['results']['files']['files-total']
        results['total-results'] += results['results']['versions']['versions-total']

        return api_response(200, 'Search results for: [%s]'%key_words, results)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/app/search/<app_name>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_app_search(app_name):
    if fk.request.method == 'GET':
        apps = ApplicationModel.objects(name__icontains=app_name)
        apps_dict = {'total_apps':0, 'apps':[]}
        for application in apps:
            if application.developer == current_user:
                apps_dict['apps'].append(application.info())
            else:
                # Only visible apps from other researchers can be searched for.
                if application.visibile:
                    apps_dict['apps'].append(application.info())
        apps_dict['total_apps'] = len(apps_dict['apps'])
        return api_response(200, 'Search results for application with name: %s'%app_name, apps_dict)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/public/apps/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_user_apps(user_id):
    current_user = UserModel.objects.with_id(user_id)
    if current_user is not None:
        if current_user.group == "developer":
            if fk.request.method == 'GET':
                apps = ApplicationModel.objects(developer=current_user)
                apps_json = {'total_apps':len(apps), 'apps':[]}
                for application in apps:
                    apps_json['apps'].append(application.extended())
                return api_response(200, 'Developer\'s applications', apps_json)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
        else:
            return api_response(404, 'Request suggested an empty response', 'This user is not allowed to create applications.')
    else:
        return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')

@app.route(API_URL + '/public/apps', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_apps():
    if fk.request.method == 'GET':
        apps = ApplicationModel.objects()
        apps_json = {'total_apps':len(apps), 'apps':[]}
        for application in apps:
            apps_json['apps'].append(application.extended())
        return api_response(200, 'Applications', apps_json)
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/public/resolve/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_resolve_item(item_id):
    logTraffic(API_URL, endpoint='/public/resolve/<item_id>')
    if fk.request.method == 'GET':
        resolution = {'class':'', 'endpoints':[]}
        if item_id == 'root':
            resolution['type'] = 'Public'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['users', '--us'], 'endpoint':'/public/users'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['projects', '--pr'], 'endpoint':'/public/projects'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/public/files'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['diffs', '--di'], 'endpoint':'/public/diffs'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['apps', '--ap'], 'endpoint':'/public/apps'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['token', '--tk'], 'endpoint':'/private/<credential.api_token>/<credential.app_token>/*'})
            resolution['endpoints'].append({'methods':['POST'], 'struct':{'email':'<credential.email>', 'password':'<credential.password>'}, 'meta':['login', '--lg'], 'endpoint':'/public/user/login'})
            return api_response(200, 'Public default resolution result', resolution)
        item = UserModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'User'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/user/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['picture', '--pc'], 'endpoint':'/public/user/picture/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['profile', '--pf'], 'endpoint':'/public/user/profile/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['projects', '--pj'], 'endpoint':'/public/user/projects/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['apps', '--ap'], 'endpoint':'/public/user/apps/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['token', '--tk'], 'endpoint':'/private/<credential.api_token>/<credential.app_token>/*'})
            resolution['endpoints'].append({'methods':['POST'], 'struct':{'email':'<credential.email>', 'password':'<credential.password>'}, 'meta':['login', '--lg'], 'endpoint':'/public/user/login'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = MessageModel.objects.with_id(item_id)
        if item != None:
            return api_response(404, 'Message items cannot be resolved in public', 'Please load your account API token.')

        item = CommentModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Comment'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/comment/show/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = ProjectModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Project'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/project/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['history', '--hi'], 'endpoint':'/public/project/history/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/public/project/comments/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['records', '--re'], 'endpoint':'/public/project/records/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/public/project/files/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/public/project/download/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['logo', '--lo'], 'endpoint':'/public/project/logo/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = RecordModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Record'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/record/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['env', '--en'], 'endpoint':'/public/record/env/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/public/record/comments/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['diffs', '--di'], 'endpoint':'/public/record/diffs/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/public/record/files/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/public/record/download/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = EnvironmentModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Environment'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/env/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/public/env/download/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = DiffModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Diff'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/diff/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/public/diff/comments/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/public/diff/files/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/public/diff/download/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = FileModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'File'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/file/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/public/file/download/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        item = ApplicationModel.objects.with_id(item_id)
        if item != None:
            resolution['type'] = 'Application'
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/public/app/show/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['search', '--se'], 'endpoint':'/public/app/search/<query>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['connectivity', '--co'], 'endpoint':'/public/app/connectivity/<selected.id>'})
            resolution['endpoints'].append({'methods':['GET','POST','PUT','UPDATE','DELETE','POST'], 'struct':{}, 'meta':['logo', '--lo'], 'endpoint':'/public/app/logo/<selected.id>'})
            return api_response(200, 'Item %s resolution results'%item_id, resolution)

        if item == None:
            return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
    else:
        return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
