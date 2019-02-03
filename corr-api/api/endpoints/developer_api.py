import json

from flask_api import status
import flask as fk

from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from api import app, storage_manager, access_manager, API_URL, ACC_SEC, CNT_SEC, api_response
from corrdb.common.models import UserModel
from corrdb.common.models import AccessModel
from corrdb.common.models import FileModel
from corrdb.common.models import ApplicationModel

import mimetypes
import simplejson as json
import traceback

# In 0.1 allow user to have same privileges as developer

@app.route(API_URL + '/developer/<api_token>/apps', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def apps_get(api_token):
    logTraffic(API_URL, endpoint='/developer/<api_token>/apps')
    current_user = access_manager.check_api(api_token, ACC_SEC, CNT_SEC)
    if current_user is not None:
        logAccess(fk, current_user, API_URL, 'api', '/developer/<api_token>/apps')
        print(current_user.group)
        if current_user.group == "developer" or current_user.group == "user":
            if fk.request.method == 'GET':
                apps = ApplicationModel.objects(developer=current_user)
                apps_json = {'total_apps':len(apps), 'apps':[]}
                for application in apps:
                    apps_json['apps'].append(application.extended())
                return api_response(200, 'Developer\'s applications', apps_json)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
        elif current_user.group == "admin": # An admin is a meta developer.
            apps = ApplicationModel.objects
            apps_json = {'total_apps':len(apps), 'apps':[]}
            for application in apps:
                apps_json['apps'].append(application.extended())
            return api_response(200, 'Developer\'s applications', apps_json)
        else:
            return api_response(401, 'Unauthorized access to the API', 'This is not a developer account.')
    else:
        return api_response(401, 'Unauthorized access to the API', 'This API token is not authorized.')

@app.route(API_URL + '/developer/<api_token>/app/logo/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_logo(api_token, app_id):
    logTraffic(API_URL, endpoint='/developer/<api_token>/app/logo/<app_id>')
    current_user = access_manager.check_api(api_token, ACC_SEC, CNT_SEC)
    if current_user is not None:
        logAccess(fk, current_user, API_URL, 'api', '/developer/<api_token>/app/logo/<app_id>')
        if current_user.group == "developer" or current_user.group == "user" or current_user.group == "admin":
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
        else:
            return api_response(401, 'Unauthorized access to the API', 'This is not a developer account.')
    else:
        return api_response(401, 'Unauthorized access to the API', 'This API token is not authorized.')

@app.route(API_URL + '/developer/<api_token>/app/access/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_access(api_token, app_id):
    logTraffic(API_URL, endpoint='/developer/<api_token>/app/access/<app_id>')
    current_user = access_manager.check_api(api_token, ACC_SEC, CNT_SEC)
    if current_user is not None:
        if current_user.group == "developer" or current_user.group == "user" or current_user.group == "admin":
            logAccess(fk, current_user, API_URL, 'api', '/developer/<api_token>/app/access/<app_id>')
            if fk.request.method == 'GET':
                app = ApplicationModel.objects.with_id(app_id)
                if app != None:
                    if app.developer == current_user or current_user.group == "user" or current_user.group == "admin":
                        app_access = AccessModel.application_access(app)
                        name = app.name if app.name != '' and app.name != None else 'unknown'
                        # print name
                        return api_response(200, 'Application %s access history'%name, app_access)
                    else:
                        return api_response(405, 'Application access request denied', 'You are not the developer of this application.')
                else:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
        else:
            return api_response(401, 'Unauthorized access to the API', 'This is not a developer account.')
    else:
        return api_response(401, 'Unauthorized access to the API', 'This API token is not authorized.')

@app.route(API_URL + '/developer/<api_token>/app/search/<app_name>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_search(api_token, app_name):
    logTraffic(API_URL, endpoint='/developer/<api_token>/app/search/<app_name>')
    current_user = access_manager.check_api(api_token, ACC_SEC, CNT_SEC)
    if current_user is not None:
        if current_user.group == "developer" or current_user.group == "user" or current_user.group == "admin":
            logAccess(fk, current_user, API_URL, 'api', '/developer/<api_token>/app/search/<app_name>')
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
        else:
            return api_response(401, 'Unauthorized access to the API', 'This is not a developer account.')
    else:
        return api_response(401, 'Unauthorized access to the API', 'This API token is not authorized.')

# Link for the application tool to test connectivity
@app.route(API_URL + '/<app_token>/app/connectivity', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_connectivity(app_token):
    logTraffic(API_URL, endpoint='/<app_token>/app/connectivity')
    current_app = access_manager.check_app(app_token)
    if current_app is not None:
        logAccess(fk, current_user, API_URL, 'api', '/<app_token>/app/connectivity', current_app)
        if fk.request.method == 'GET':
            name = current_app.name if current_app.name != '' and current_app.name != None else 'unknown'
            return api_response(200, 'Application %s is accessible'%name, current_app.info())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')
    else:
        return api_response(401, 'Unauthorized access to the API', 'This is not an app token.')
