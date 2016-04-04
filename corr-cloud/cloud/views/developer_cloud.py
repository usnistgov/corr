import json

from flask.ext.api import status
import flask as fk

from api import app, API_URL, crossdomain, check_api, check_app, api_response, s3_delete_file, s3_get_file, web_get_file, s3_upload_file, data_pop, merge_dicts, logStat, logTraffic, logAccess, prepare_env, prepare_record, prepare_project
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
import json
import traceback
import datetime
import random
import string
import os
import thread

#User info
@app.route(API_URL + '/private/<api_token>/<app_token>/user/status', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_status(api_token, app_token):
    logTraffic(endpoint='<api_token>/<app_token>/user/status')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
        	return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '<api_token>/<app_token>/user/status')
            if fk.request.method == 'GET':
                return api_response(200, 'User %s credentials are authorized'%str(current_user.id), current_user.info())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/connectivity', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
def user_app_connectivity(api_token, app_token):
    logTraffic(endpoint='<api_token>/<app_token>/connectivity')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/<app_token>/connectivity')
            if fk.request.method == 'GET':
                name = current_app.name if current_app.name != '' and current_app.name != None else 'unknown'
                return api_response(200, 'Application %s is accessible'%name, current_app.info())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/user/search/<user_name>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
def user_search(api_token, app_token, user_name):
    logTraffic(endpoint='<api_token>/<app_token>/user/search/<user_name>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '<api_token>/<app_token>/user/search/<user_name>')
            if fk.request.method == 'GET':
                names = user_name.split('-')
                users = []
                for user in UserModel.objects():
                    exists = [False for name in names]
                    condition = [True for name in names]
                    profile = ProfileModel.objects(user=user).first()
                    index = 0
                    for name in names:
                        if name != '':
                            if name in profile.fname or name in profile.lname:
                                exists[index] = True
                        else:
                            exists[index] = True
                        index += 1
                    if exists == condition:
                        users.append(user)

                # for name in names:
                #     users_1 = ProfileModel.objects(fname__icontains=name)
                #     for pf in users_1:
                #         if pf.user not in users:
                #             users.append(pf.user)
                #     users_2 = ProfileModel.objects(lname__icontains=name)
                #     for pf in users_2:
                #         if pf.user not in users:
                #             users.append(pf.user)
                users_dict = {'total_users':len(users), 'users':[user.info() for user in users]}
                return api_response(200, 'Search results for user with name containing: %s'%user_name.split('-'), users_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/user/picture', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_picture(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/user/picture')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            if fk.request.method == 'GET':
                profile = ProfileModel.objects(user=current_user).first()
                if profile == None:
                    picture_buffer = s3_get_file('picture', 'default-picture.png')
                    if picture_buffer == None:
                        return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                else:
                    picture = profile.picture
                    if picture.location == 'local' and 'http://' not in picture.storage:
                        picture_buffer = s3_get_file('picture', picture.storage)
                        if picture_buffer == None:
                            return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%logo.storage)
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    elif picture.location == 'remote':
                        picture_buffer = web_get_file(picture.storage)
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture_buffer = s3_get_file('picture', 'default-picture.png')
                            if picture_buffer == None:
                                return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                            else:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        # solve the file situation and return the appropriate one.
                        if 'http://' in picture.storage:
                            picture.location = 'remote'
                            picture.save()
                            picture_buffer = web_get_file(picture.storage)
                            if picture_buffer != None:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                            else:
                                picture_buffer = s3_get_file('picture', 'default-picture.png')
                                if picture_buffer == None:
                                    return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                                else:
                                    return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture.location = 'local'
                            picture.save()
                            picture_buffer = s3_get_file('picture', picture.storage)
                            if picture_buffer == None:
                                return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                            else:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/user/home', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_home(api_token, app_token):
    logTraffic(endpoint='<api_token>/<app_token>/user/home')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '<api_token>/<app_token>/user/home')
            if fk.request.method == 'GET':
                return api_response(200, 'User %s Home'%str(current_user.id), current_user.home())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/private/<api_token>/<app_token>/profile/show', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_user_profile_show(api_token, app_token):
    logTraffic(endpoint='<api_token>/<app_token>/profile/show')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '<api_token>/<app_token>/profile/show')
            if fk.request.method == 'GET':
                profile = ProfileModel.objects(user=current_user).first()
                if profile == None:
                    return api_response(404, 'User %s profile is empty'%current_user.email, 'You have to create a profile for this user.')
                else:
                    return api_response(200, 'User %s profile'%current_user.email, profile.extended())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# User picture:
# http://0.0.0.0:5100/api/v1/private/07366337c49a026cda30d1cb99679a1b86f7dffb9a44cf9765975a5991d6a849/dad86479d3f0e4b1c6ed17b8ab02a9df4fa65e61761d5952f45770c19fb5194a/user/picture

#Messages
@app.route(API_URL + '/private/<api_token>/<app_token>/messages', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_messages(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/messages')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/messages')
            if fk.request.method == 'GET':
                messages = []
                messages.extend(MessageModel.objects(sender=current_user))
                messages.extend(MessageModel.objects(receiver=current_user))
                messages_dict = {'total_messages':len(messages), 'messages':[]}
                for message in messages:
                    messages_dict['messages'].append(message.extended())
                return api_response(200, 'Messages list', messages_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/message/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_message_create(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/message/create')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/message/create')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    receiver_id = data.get('receiver', None)
                    title = data.get('title', '')
                    content = data.get('content', '')
                    attachments = data.get('attachments', [])
                    if receiver_id == '':
                        return api_response(400, 'Missing mandatory fields', 'A message should have a receiver.')
                    else:
                        if title == '' and content == '':
                            return api_response(400, 'Missing mandatory fields', 'A message cannot have title and content empty.')
                        
                        receiver = UserModel.objects.with_id(receiver_id)
                        message, created = MessageModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), sender=current_user, receiver=receiver, title=title, attachments=attachments, content=content)
                        if receiver == None:
                            return api_response(400, 'Missing mandatory fields', 'A message should have an existing receiver.')
                        if not created:
                            # Impossible only if the time field fails
                            return api_response(200, 'Message already exists', message.info())
                        else:
                            logStat(message=message)
                            return api_response(201, 'Message created', message.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the message information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/message/show/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_message_show(api_token, app_token, message_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/message/show/<message_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/message/create')
            if fk.request.method == 'GET':
                message = MessageModel.objects.with_id(message_id)
                if message == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
                else:
                    if message.sender == current_user or message.receiver == current_user:
                        return api_response(200, 'Message %s'%str(message.id), message.extended())
                    else:
                        return api_response(401, 'Unauthorized action', 'You must be part of the conversation to read it.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/message/delete/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_message_delete(api_token, app_token, message_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/message/delete/<message_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/message/create')
            if fk.request.method == 'GET':
                message = MessageModel.objects.with_id(message_id)
                if message == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
                else:
                    if message.sender == current_user or message.receiver == current_user:
                        # Delete attachements maybe??
                        message.delete()
                        logStat(deleted=True, message=message)
                        return api_response(200, 'Deletion succeeded', 'The message %s was succesfully deleted.'%str(message.id))
                    else:
                        return api_response(401, 'Unauthorized action', 'You must be part of the conversation to read it.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/message/update/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_message_update(api_token, app_token, message_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/message/update/<message_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/message/create')
            if fk.request.method == 'POST':
                message = MessageModel.objects.with_id(message_id)
                if message == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
                else:
                    if message.sender == current_user or message.receiver == current_user:
                        if fk.request.data:
                            data = json.loads(fk.request.data)
                            sender_id = data.get('sender', None)
                            receiver_id = data.get('receiver', None)
                            title = data.get('title', message.title)
                            content = data.get('content', message.content)
                            attachments = data.get('attachments', [])
                            sender = None
                            receiver = None
                            if sender_id == None:
                                sender = message.sender
                            else:
                                sender = UserModel.objects(session=sender_id).first()
                                if sender == None:
                                    sender = message.sender
                            if receiver_id == None:
                                receiver = message.receiver
                            else:
                                receiver = UserModel.objects.with_id(receiver_id)
                                if receiver == None:
                                    receiver = message.receiver
                            message.sender = sender
                            message.receiver = receiver
                            message.title = title
                            message.content = content
                            message.attachments.extend(attachments)
                            message.save()
                            return api_response(201, 'Message updated', message.info())
                        else:
                            return api_response(204, 'Nothing created', 'You must provide the message information.')
                    else:
                        return api_response(401, 'Unauthorized action', 'You must be part of the conversation to read it.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

# Files
@app.route(API_URL + '/private/<api_token>/<app_token>/files', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_files(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/files')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/files')
            if fk.request.method == 'GET':
                files = []
                for _file in FileModel.objects():
                    info = _file.info()
                    if info['owner'] == 'public' or info['owner'] == str(current_user.id):
                        files.append(_file.info())

                files_dict = {'total_files':len(files), 'files':[]}
                for _file in files:
                    files_dict['files'].append(_file)
                return api_response(200, 'Files list', files_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/upload/<group>/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_upload(api_token, app_token, group, item_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/upload/<group>/<item_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user == None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/upload/<group>/<item_id>')
            if fk.request.method == 'POST':
                if group not in ["input", "output", "dependencie", "file", "descriptive", "diff", "resource-record", "resource-env", "resource-app", "attach-comment", "attach-message", "picture" , "logo-project" , "logo-app" , "resource", "bundle"]:
                    return api_response(405, 'Method Group not allowed', 'This endpoint supports only a specific set of groups.')
                else:
                    if fk.request.files:
                        file_obj = fk.request.files['file']
                        filename = '%s_%s'%(item_id, file_obj.filename)
                        _file, created = FileModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), name=filename)
                        if not created:
                            return api_response(200, 'File already exists with same name for this item', _file.info())
                        else:
                            encoding = ''
                            if file_obj != None:
                                old_file_position = file_obj.tell()
                                file_obj.seek(0, os.SEEK_END)
                                size = file_obj.tell()
                                file_obj.seek(old_file_position, os.SEEK_SET)
                            else:
                                size = 0
                            storage = '%s_%s'%(item_id, file_obj.filename)
                            location = 'local'
                            mimetype = mimetypes.guess_type(storage)[0]
                            group_ = group
                            description = ''
                            item = None
                            owner = None
                            if group == 'input':
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is an input file for the record %s'%(file_obj.filename, str(item.id))
                            elif group == 'output':
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is an output file for the record %s'%(file_obj.filename, str(item.id))
                            elif group == 'dependencie':
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is an dependency file for the record %s'%(file_obj.filename, str(item.id))
                            elif group == 'descriptive':
                                item = ProjectModel.objects.with_id(item_id)
                                owner = item.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is a resource file for the project %s'%(file_obj.filename, str(item.id))
                            elif group == 'diff':
                                item = DiffModel.objects.with_id(item_id)
                                owner1 = item.sender
                                owner2 = item.targeted
                                if current_user != owner1 and current_user != owner2:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is a resource file for the collaboration %s'%(file_obj.filename, str(item.id))
                            elif 'attach' in group:
                                if 'message' in group:
                                    item = MessageModel.objects.with_id(item_id)
                                    owner1 = item.sender
                                    owner2 = item.receiver
                                    if current_user != owner1 and current_user != owner2:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is an attachement file for the message %s'%(file_obj.filename, str(item.id))
                                elif 'comment' in group:
                                    item = CommentModel.objects.with_id(item_id)
                                    owner = item.sender
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is an attachement file for the comment %s'%(file_obj.filename, str(item.id))
                                group_ = group.split('-')[0]
                            elif group == 'bundle':
                                item = BundleModel.objects.with_id(item_id)
                                env = EnvironmentModel.objects(bundle=item).first()
                                rec_temp = RecordModel.objects(environment=env).first()
                                if rec_temp == None: # No record yet performed.
                                    for project in ProjectModel.objects():
                                        if str(env.id) in project.history:
                                            owner = project.owner
                                            break
                                else:
                                    owner = rec_temp.project.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            elif group == 'picture':
                                item = ProfileModel.objects.with_id(item_id)
                                owner = item.user
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is the picture file of the profile %s'%(file_obj.filename, str(item.id))
                                _file.delete()
                                _file = item.picture
                            elif 'logo' in group:
                                if 'app' in group:
                                    item = ApplicationModel.objects.with_id(item_id)
                                    owner = item.developer
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is the logo file of the application %s'%(file_obj.filename, str(item.id))
                                elif 'project' in group:
                                    item = ProjectModel.objects.with_id(item_id)
                                    owner = item.owner
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is the logo file of the project %s'%(file_obj.filename, str(item.id))
                                _file.delete()
                                _file = item.logo
                            elif 'resource' in group:
                                if 'record' in group:
                                    item = RecordModel.objects.with_id(item_id)
                                    owner = item.project.owner
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is an resource file for the record %s'%(file_obj.filename, str(item.id))
                                elif 'env' in group:
                                    item = EnvironmentModel.objects.with_id(item_id)
                                    rec_temp = RecordModel.objects(environment=item).first()
                                    owner = rec_temp.project.owner
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is a resource file for the environment %s'%(file_obj.filename, str(item.id))
                                elif 'app' in group:
                                    item = ApplicationModel.objects.with_id(item_id)
                                    owner = item.developer
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    description = '%s is a resource file for the app %s'%(file_obj.filename, str(item.id))
                                group_ = group.split('-')[0]

                            if item == None:
                                if group != 'picture' or group != 'logo':
                                    return api_response(400, 'Missing mandatory instance', 'A file should reference an existing item.')
                            else:
                                _file.description = description
                                _file.encoding = encoding
                                _file.size = size
                                # _file.path = path
                                _file.owner = current_user
                                _file.storage = storage
                                _file.location = location
                                _file.mimetype = mimetype
                                _file.group = group_
                                _file.save()
                                uploaded = s3_upload_file(_file, file_obj)
                                if not uploaded[0]:
                                    _file.delete()
                                    return api_response(500, 'An error occured', "%s"%uploaded[1])
                                else:
                                    if group == 'input':
                                        item.resources.append(str(_file.id))
                                    elif group == 'output':
                                        item.resources.append(str(_file.id))
                                    elif group == 'dependencie':
                                        item.resources.append(str(_file.id))
                                    elif group == 'descriptive':
                                        item.resources.append(str(_file.id))
                                    elif group == 'diff':
                                        item.resources.append(str(_file.id))
                                    elif group == 'bundle':
                                        _file.delete()
                                        if item.location != storage:
                                            s3_delete_file('bundle',item.location)
                                        item.encoding = encoding
                                        item.size = size
                                        item.scope = 'local'
                                        item.location = storage
                                        item.mimetype = mimetype
                                        item.save()
                                    elif 'attach' in group:
                                        item.attachments.append(str(_file.id))
                                    elif group == 'picture':
                                        if item.picture.location != storage:
                                            s3_delete_file('picture',item.picture.storage)
                                        if item != None:
                                            item.picture = _file
                                    elif 'logo' in group:
                                        if item.logo.location != storage:
                                            s3_delete_file('logo',item.logo.storage)
                                        if item != None:
                                            item.logo = _file
                                    elif 'resource' in group:
                                        item.resources.append(str(_file.id))
                                    if item != None:
                                        item.save()
                                    logStat(file_obj=_file)
                                    return api_response(201, 'New file created', _file.info())
                    else:
                        return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_download(api_token, app_token, file_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/download/<file_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/download/<file_id>')
            if fk.request.method == 'GET':
                # print [f.extended() for f in FileModel.objects()]
                file_meta = FileModel.objects.with_id(file_id)
                if file_meta == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
                else:
                    info = file_meta.info()
                    print info
                    print str(current_user.id)
                    if info['owner'] != 'public' and info['owner'] != str(current_user.id):
                        return api_response(401, 'Unauthorized access', 'This file is private and you are not the owner.')
                    else:
                        file_obj = None
                        if file_meta.location == 'remote':
                            file_obj = web_get_file(file_meta.storage)
                        elif file_meta.location == 'local':
                            file_obj = s3_get_file(file_meta.group, file_meta.storage)

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
                                # if file_meta.name.split('.')[1] in ['jpg', 'pdf', 'txt']:
                                #     return fk.send_file(
                                #         file_obj,
                                #         file_meta.mimetype,
                                #         # as_attachment=True,
                                #         attachment_filename=file_meta.name,
                                #     )
                                # else:
                                    # Check the mimetype for media files to just provide them without attachment.
                                return fk.send_file(
                                        file_obj,
                                        file_meta.mimetype,
                                        as_attachment=True,
                                        attachment_filename=file_meta.name,
                                    )
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_create(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/create')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/create')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    encoding = data.get('encoding', '')
                    size = data.get('size', 0)
                    name = data.get('name', '')
                    access = data.get('access', 'public') # Allow the creation of public files.
                    storage = data.get('storage', '')
                    location = data.get('location', 'undefined')
                    mimetype = data.get('mimetype', mimetypes.guess_type(location)[0])
                    group = data.get('group', 'undefined')
                    description = data.get('description', '')
                    owner = current_user
                    if storage == '' or name == '':
                        return api_response(400, 'Missing mandatory fields', 'A file should have at least a name and a storage reference (s3 key or url).')
                    else:
                        
                        if 'http://' in storage or 'https://' in storage:
                            file_buffer = web_get_file(storage)
                            location = 'remote'
                        else:
                            file_buffer = s3_get_file(group, storage)
                            location = 'local'
                        if file_buffer != None:
                            old_file_position = file_buffer.tell()
                            file_buffer.seek(0, os.SEEK_END)
                            size = file_buffer.tell()
                            file_buffer.seek(old_file_position, os.SEEK_SET)
                        else:
                            return api_response(400, 'Could not reach the file location', 'We could not find the file raw content at the location provided.')
                        if access == 'public':
                            _file, created = FileModel.objects.get_or_create(encoding=encoding, name=name, mimetype=mimetype, size=size, storage=storage, location=location, group=group, description=description)
                        else:
                            _file, created = FileModel.objects.get_or_create(owner=owner, encoding=encoding, name=name, mimetype=mimetype, size=size, storage=storage, location=location, group=group, description=description)
                        if not created:
                            return api_response(200, 'File already exists', _file.info())
                        else:
                            logStat(file_obj=_file)
                            return api_response(201, 'File created', _file.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/show/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_show(api_token, app_token, file_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/show/<file_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/show/<file_id>')
            if fk.request.method == 'GET':
                # print [f.extended() for f in FileModel.objects()]
                _file = FileModel.objects.with_id(file_id)
                if _file == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
                else:
                    info = _file.info()
                    if info['owner'] != 'public' and info['owner'] != str(current_user.id):
                        return api_response(401, 'Unauthorized access', 'This file is private and you are not the owner.')
                    else:
                        return api_response(200, 'File %s'%_file.name, _file.extended())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/delete/<item_id>/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_delete(api_token, app_token, item_id, file_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/delete/<item_id>/<file_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/delete/<item_id>/<file_id>')
            if fk.request.method == 'GET':
                _file = FileModel.objects.with_id(file_id)
                if _file == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
                else:
                    item = None
                    if _file.group == 'input':
                        item = RecordModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.project.owner
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                _file.delete()
                                item.inputs.remove(file_id)
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                    elif _file.group == 'output':
                        item = RecordModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.project.owner
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                _file.delete()
                                item.outputs.remove(file_id)
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                    elif _file.group == 'dependencie':
                        item = RecordModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.project.owner
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                _file.delete()
                                item.dependencies.remove(file_id)
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                    elif _file.group == 'diff':
                        item = DiffModel.objects.with_id(item_id)
                        if item != None:
                            owner1 = item.sender
                            owner2 = item.targeted
                            if current_user != owner1 and current_user != owner2:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                _file.delete()
                                item.resources.remove(file_id)
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                    elif _file.group == 'attach':
                        item = MessageModel.objects.with_id(item_id)
                        if item != None:
                            owner1 = item.sender
                            owner2 = item.receiver
                            if current_user != owner1 and current_user != owner2:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                _file.delete()
                                item.attachments.remove(file_id)
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                        else:
                            item = CommentModel.objects.with_id(item_id)
                            if item != None:
                                owner = item.sender
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                try:
                                    _file.delete()
                                    item.attachments.remove(file_id)
                                    if _file.location == 'local':
                                        s3_delete_file(_file.group, _file.storage)
                                except ValueError:
                                    pass
                    elif _file.group == 'picture':
                        item = ProfileModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.user
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            _file.storage = 'default-picture.png'
                            picture_buffer = s3_get_file('picture', 'default-picture.png')
                            _file.name = 'default-picture.png'
                            _file.location = 'local'
                            _file.group = 'picture'
                            _file.description = 'This is the default image used for the user profile picture in case none is provided.'
                            if picture_buffer != None:
                                old_file_position = picture_buffer.tell()
                                picture_buffer.seek(0, os.SEEK_END)
                                p_file.size = picture_buffer.tell()
                                picture_buffer.seek(old_file_position, os.SEEK_SET)
                            else:
                                _file.size = 0
                            _file.save()
                            if _file.location == 'local':
                                s3_delete_file(_file.group, _file.storage)

                    elif _file.group == 'logo':
                        item = ApplicationModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.developer
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            _file.storage = 'default-logo.png'
                            logo_buffer = s3_get_file('logo', 'default-logo.png')
                            _file.name = 'default-logo.png'
                            _file.location = 'local'
                            _file.group = 'logo'
                            _file.description = 'This is the default image used for the app logo in case none is provided.'
                            if logo_buffer != None:
                                old_file_position = logo_buffer.tell()
                                logo_buffer.seek(0, os.SEEK_END)
                                p_file.size = logo_buffer.tell()
                                logo_buffer.seek(old_file_position, os.SEEK_SET)
                            else:
                                _file.size = 0
                            _file.save()
                            if _file.location == 'local':
                                s3_delete_file(_file.group, _file.storage)
                        else:
                            item = ProjectModel.objects.with_id(item_id)
                            if item != None:
                                owner = item.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                _file.storage = 'default-project.png'
                                logo_buffer = s3_get_file('logo', 'default-project.png')
                                _file.name = 'default-project.png'
                                _file.location = 'local'
                                _file.group = 'logo'
                                _file.description = 'This is the default image used for the project logo in case none is provided.'
                                if logo_buffer != None:
                                    old_file_position = logo_buffer.tell()
                                    logo_buffer.seek(0, os.SEEK_END)
                                    p_file.size = logo_buffer.tell()
                                    logo_buffer.seek(old_file_position, os.SEEK_SET)
                                else:
                                    _file.size = 0
                                _file.save()
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)

                    elif _file.group == 'resource':
                        item = RecordModel.objects.with_id(item_id)
                        if item != None:
                            owner = item.project.owner
                            if current_user != owner:
                                return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            try:
                                item.resources.remove(file_id)
                                _file.delete()
                                if _file.location == 'local':
                                    s3_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                        else:
                            item = EnvironmentModel.objects.with_id(item_id)
                            if item != None:
                                rec_temp = RecordModel.objects(environment=item).first()
                                if rec_temp == None:
                                    for p in ProjectModel.objects():
                                        if str(item.id) in p.history:
                                            owner = p.owner
                                            break
                                else:
                                    owner = rec_temp.project.owner
                                if current_user != owner:
                                    return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                try:
                                    item.resources.remove(file_id)
                                    _file.delete()
                                    if _file.location == 'local':
                                        s3_delete_file(_file.group, _file.storage)
                                except ValueError:
                                    pass
                            else:
                                item = ProjectModel.objects.with_id(item_id)
                                if item != None:
                                    owner = item.owner
                                    if current_user != owner:
                                        return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                    try:
                                        item.resources.remove(file_id)
                                        _file.delete()
                                        if _file.location == 'local':
                                            s3_delete_file(_file.group, _file.storage)
                                    except ValueError:
                                        pass
                                else:
                                    item = ApplicationModel.objects.with_id(item_id)
                                    if item != None:
                                        owner = item.developer
                                        if current_user != owner:
                                            return api_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                        try:
                                            item.resources.remove(file_id)
                                            _file.delete()
                                            if _file.location == 'local':
                                                s3_delete_file(_file.group, _file.storage)
                                        except ValueError:
                                            pass
                    if item == None:
                        if item_id in _file.storage or item_id in _file.name:
                            _file.delete()
                            s3_delete_file(_file.group, _file.storage)
                            logStat(deleted=True, file_obj=_file)
                            return api_response(200, 'Deletion succeeded', 'The file %s was succesfully deleted.'%_file.name)
                        else:
                            return api_response(400, 'Missing mandatory instance', 'A file should reference an existing item.')
                    else:
                        item.save()
                    logStat(deleted=True, file_obj=_file)
                    return api_response(200, 'Deletion succeeded', 'The file %s was succesfully deleted.'%_file.name)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/file/update/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_file_update(api_token, app_token, file_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/file/update/<file_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/file/update/<file_id>')
            if fk.request.method == 'POST':
                _file = FileModel.objects.with_id(file_id)
                if _file == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
                else:
                    if _file.owner != 'public' and _file.owner != str(current_user.id):
                        return api_response(401, 'Unauthorized access', 'This file is private and you are not the owner.')
                    else:
                        if fk.request.data:
                            data = json.loads(fk.request.data)
                            encoding = data.get('encoding', _file.encoding)
                            size = data.get('size', _file.size)
                            name = data.get('name', _file.name)
                            path = data.get('path', _file.path)
                            storage = data.get('storage', _file.storage)
                            location = data.get('location', _file.location)
                            mimetype = data.get('mimetype', _file.mimetype)
                            group = data.get('group', _file.group)
                            description = data.get('description', _file.description)
                            if name == '':
                                name = _file.name
                            if location == '':
                                location = _file.location
                            _file.encoding = encoding
                            _file.size = size
                            _file.name = name
                            _file.path = path
                            _file.storage = storage
                            _file.location = location
                            _file.mimetype = mimetype
                            _file.group = group
                            _file.description = description
                            _file.save()
                            return api_response(201, 'File updated', _file.info())
                        else:
                            return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')


# +++++

@app.route(API_URL + '/private/<api_token>/<app_token>/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_projects(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/projects')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/projects')
            if fk.request.method == 'GET':
                projects = ProjectModel.objects(owner=current_user, application=current_app)
                projects_dict = {'total_projects':len(projects), 'projects':[]}
                for project in projects:
                    projects_dict['projects'].append(project.extended())
                return api_response(200, 'User %s Projects list'%str(current_user.id), projects_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/projects/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_projects_clear(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/projects/clear')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/projects/clear')
            if fk.request.method == 'GET':
                projects = ProjectModel.objects(owner=current_user, application=current_app)
                projects.delete()
                return api_response(200, 'User %s Projects deleted'%str(current_user.id), 'All the projects have been deleted.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/envs/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_envs_clear(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/envs/clear')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/envs/clear')
            if fk.request.method == 'GET':
                projects = ProjectModel.objects(owner=current_user, application=current_app)
                for project in projects:
                    for env_id in project.history:
                        env = EnvironmentModel.objects.with_id(env_id)
                        if env != None:
                            env.delete()
                return api_response(200, 'User %s Environments deleted'%str(current_user.id), 'All the environments have been deleted.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/private/<api_token>/<app_token>/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_comments(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/comments/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/comments/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
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

@app.route(API_URL + '/private/<api_token>/<app_token>/project/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_create(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/create')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/create')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    name = data.get('name', '')
                    description = data.get('description', '')
                    goals = data.get('goals', '')
                    tags = data.get('tags', [])
                    access = data.get('access', 'private')
                    history = data.get('history', [])
                    cloned_from_id = data.get('original', '')
                    resources = data.get('resources', [])
                    group = data.get('group', 'undefined')

                    logo_storage = 'default-project.png'
                    logo_encoding = ''
                    logo_mimetype = mimetypes.guess_type(logo_storage)[0]
                    logo_buffer = s3_get_file('logo', logo_storage)
                    if logo_buffer != None:
                        old_file_position = logo_buffer.tell()
                        logo_buffer.seek(0, os.SEEK_END)
                        logo_size = logo_buffer.tell()
                        logo_buffer.seek(old_file_position, os.SEEK_SET)
                    else:
                        logo_size = 0
                    logo_name = 'default-project.png'
                    logo_location = 'local'
                    logo_group = 'logo'
                    logo_description = 'This is the default image used for the project logo in case none is provided.'
                    logo, logo_created = FileModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), encoding=logo_encoding, name=logo_name, mimetype=logo_mimetype, size=logo_size, storage=logo_storage, location=logo_location, group=logo_group, description=logo_description)
                    
                    application = None
                    cloned_from = ''
                    if cloned_from_id != '':
                        cloned = ProjectModel.objects.with_id(cloned_from_id)
                        if cloned != None:
                            cloned_from = str(clone.id)
                    if (cloned_from == '' and cloned_from_id != ''):
                        return api_response(400, 'Missing references mandatory fields', 'A project should have an existing original record when provided original record.')
                    project, created = ProjectModel.objects.get_or_create(owner=current_user, name=name)
                    if not created:
                        return api_response(200, 'Project already exists', project.info())
                    else:
                        project.application = current_app
                        project.description = description
                        project.goals = goals
                        project.tags = tags
                        project.history = history
                        project.cloned_from = cloned_from
                        project.resources = resources
                        project.group = group
                        project.logo = logo
                        project.save()
                        logStat(project=project)
                        return api_response(201, 'Project created', project.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_records(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/records/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/records/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        records = RecordModel.objects(project=project)
                        records_dict = {'total_records':len(records), 'records':[]}
                        for record in records:
                            records_dict['records'].append(record.extended())
                        return api_response(200, 'Project [%s] Records list'%project.name, records_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/private/<api_token>/<app_token>/project/show/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_show(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/show/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/show/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        return api_response(200, 'Project %s'%project.name, project.extended())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/logo/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_logo(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/logo/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/logo/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project != None:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        logo = project.logo
                        if logo.location == 'local' and 'http://' not in logo.storage:
                            logo_buffer = s3_get_file('logo', logo.storage)
                            if logo_buffer == None:
                                return api_response(404, 'No logo found', 'We could not fetch the logo at [%s].'%logo.storage)
                            else:
                                return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                        elif logo.location == 'remote':
                            logo_buffer = web_get_file(logo.storage)
                            if logo_buffer != None:
                                return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                            else:
                                logo_buffer = s3_get_file('logo', 'default-logo.png')
                                if logo_buffer == None:
                                    return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                                else:
                                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                        else:
                            # solve the file situation and return the appropriate one.
                            if 'http://' in logo.storage:
                                logo.location = 'remote'
                                logo.save()
                                logo_buffer = web_get_file(logo.storage)
                                if logo_buffer != None:
                                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                                else:
                                    logo_buffer = s3_get_file('logo', 'default-logo.png')
                                    if logo_buffer == None:
                                        return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                                    else:
                                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                            else:
                                logo.location = 'local'
                                logo.save()
                                logo_buffer = s3_get_file('logo', logo.storage)
                                if logo_buffer == None:
                                    return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                                else:
                                    return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/delete/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_delete(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/delete/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/delete/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        #Delete all attachements and record files too
                        project.delete()
                        logStat(deleted=True, project=project)
                        return api_response(200, 'Deletion succeeded', 'The project %s was succesfully deleted.'%project.name)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/update/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_update(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/update/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/update/<project_id>')
            if fk.request.method == 'POST':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        if fk.request.data:
                            data = json.loads(fk.request.data)
                            application_id = data.get('application', None)
                            owner_id = data.get('owner', None)
                            name = data.get('name', project.name)
                            description = data.get('description', project.description)
                            goals = data.get('goals', project.goals)
                            tags = data.get('tags', [])
                            access = data.get('access', project.access)
                            history = data.get('history', [])
                            cloned_from_id = data.get('original', None)
                            resources = data.get('resources', [])
                            group = data.get('group', project.group)
                            application = None
                            owner = None
                            cloned_from = None
                            if application_id == None:
                                application = project.application
                            else:
                                project = ApplicationModel.objects.with_id(application_id)
                                if application == None:
                                    application = project.application
                            if owner_id == None:
                                owner = project.owner
                            else:
                                project = UserModel.objects.with_id(owner_id)
                                if owner == None:
                                    owner = project.owner
                            if cloned_from_id == None:
                                cloned_from = project.cloned_from
                            else:
                                cloned_from = None
                                clone = ProjectModel.objects.with_id(cloned_from_id)
                                if clone != None:
                                    cloned_from = str(clone.id)
                                if cloned_from == None:
                                    cloned_from = project.cloned_from

                            project.application = application
                            project.owner = owner
                            project.name = name
                            project.description = description
                            project.goals = goals
                            project.tags.extend(tags)
                            project.access = access
                            project.history.extend(history)
                            project.cloned_from = cloned_from
                            project.resources.extend(resources)
                            project.group = group
                            project.save()
                            return api_response(201, 'Project updated', project.info())
                        else:
                            return api_response(204, 'Nothing created', 'You must provide the project information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/download/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_download(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/download/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/download/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        prepared = prepare_project(project)
                        if prepared[0] == None:
                            return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                        else:
                            return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/private/<api_token>/<app_token>/project/envs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_envs(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/envs/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/envs/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
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

@app.route(API_URL + '/private/<api_token>/<app_token>/project/envs/head/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_envs_head(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/envs/head')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/envs/head/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        head = {}
                        if len(project.history) > 0:
                            head = project.history[-1]
                        return api_response(200, 'Project %s environments head'%project.name, head)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/env/show/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_env_show(api_token, app_token, project_id, env_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/env/show/<project_id>/<env_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/env/show/<project_id>/<env_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
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

@app.route(API_URL + '/private/<api_token>/<app_token>/project/env/next/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_env_push(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/env/next/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/env/next/<project_id>')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    group = data.get('group', 'undefined')
                    system = data.get('system', 'undefined')
                    specifics = data.get('specifics', {})
                    version_dict = data.get('version', None)
                    bundle_dict = data.get('bundle', None)

                    project = ProjectModel.objects.with_id(project_id)

                    if project == None:
                        return api_response(400, 'Missing mandatory fields', 'Unable to find this project.')
                    else:
                        if project.owner != current_user:
                            return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                        else:
                            env, created = EnvironmentModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), group=group, system=system, specifics=specifics)
                            if not created:
                                return api_response(500, 'Internal Platform Error', 'There is a possible issue with the MongoDb instance.')
                            else:
                                version, created = VersionModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                                if version_dict != None:
                                    version.system = version_dict.get('system','unknown')
                                    version.baseline = version_dict.get('baseline','')
                                    version.marker = version_dict.get('marker','')
                                    version.save()
                                    env.version = version
                                bundle, created = BundleModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                                if bundle_dict != None:
                                    bundle.scope = bundle_dict.get('scope','unknown')
                                    location = bundle_dict.get('location', '')
                                    if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                                        bundle.location = location
                                        bundle.save()
                                        def handle_file_resolution(_bundle):
                                            # print _bundle
                                            bundle = BundleModel.objects.with_id(_bundle)
                                            bundle_buffer = web_get_file(location)
                                            bundle.mimetype = mimetypes.guess_type(location)[0]
                                            old_file_position = bundle_buffer.tell()
                                            bundle_buffer.seek(0, os.SEEK_END)
                                            bundle.size = bundle_buffer.tell()
                                            bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                            bundle.save()
                                        thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                                    env.bundle = bundle
                                env.save()
                                project.history.append(str(env.id))
                                project.save()
                                return api_response(201, 'Environment created', env.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/env/update/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_env_update(api_token, app_token, project_id, env_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/env/update/<project_id>/<env_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/env/update/<project_id>/<env_id>')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    project = ProjectModel.objects.with_id(project_id)
                    if project == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                    else:
                        if project.owner != current_user:
                            return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                        else:
                            if env_id not in [str(e.id) for e in project._history()]:
                                return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
                            else:
                                env = EnvironmentModel.objects.with_id(env_id)
                                if env == None:
                                    return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                                else:
                                    group = data.get('group', env.group)
                                    system = data.get('system', env.system)
                                    specifics = data.get('specifics', env.specifics)
                                    version_dict = data.get('version', None)
                                    bundle_dict = data.get('bundle', None)
                                    if version_dict != None:
                                        version =  env.version
                                        version.system = version_dict.get('system', version.system)
                                        version.baseline = version_dict.get('baseline', version.baseline)
                                        version.marker = version_dict.get('marker', version.marker)
                                        version.save()
                                    if bundle_dict != None:
                                        bundle =  env.bundle
                                        location = bundle_dict.get('location', '')
                                        bundle.scope = bundle_dict.get('scope', bundle.scope)
                                        if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                                            bundle.location = location
                                            bundle.save()
                                            def handle_file_resolution(_bundle):
                                                # print _bundle
                                                bundle = BundleModel.objects.with_id(_bundle)
                                                bundle_buffer = web_get_file(location)
                                                bundle.mimetype = mimetypes.guess_type(location)[0]
                                                old_file_position = bundle_buffer.tell()
                                                bundle_buffer.seek(0, os.SEEK_END)
                                                bundle.size = bundle_buffer.tell()
                                                bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                                bundle.save()
                                            thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                                    env.group = group
                                    env.system = system
                                    env.specifics = specifics
                                    env.save()
                                    return api_response(200, 'Project %s environment %s updated'%(project.name, env_id), env.extended())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/env/download/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_project_env_download(api_token, app_token, project_id, env_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/env/download/<project_id>/<env_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/env/download/<project_id>/<env_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if project.access == 'private' and project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                    else:
                        if env_id not in project.history:
                            return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
                        else:
                            env = EnvironmentModel.objects.with_id(env_id)
                            if env == None:
                                return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                            else:
                                prepared = prepare_env(project, env)
                                if prepared[0] == None:
                                    return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                                else:
                                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/records/list/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_records_list(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/project/records/list/<project_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/records/list/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project != None and (project.access == 'private' and project.owner != current_user):
                    return api_response(401, 'Unauthorized access', 'You are not this project owner.')
                else:
                    records = RecordModel.objects(project=project)
                    records_dict = {'total_records':len(records), 'records':[]}
                    for record in records:
                        records_dict['records'].append(record.extended())
                    return api_response(200, 'Records list', records_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/records/clear/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_records_clear(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/records/clear')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/records/clear/<project_id>')
            if fk.request.method == 'GET':
                project = ProjectModel.objects.with_id(project_id)
                if project != None and project.owner != current_user:
                    return api_response(401, 'Unauthorized access', 'You are this project owner.')
                else:
                    records = RecordModel.objects(project=project)
                    records.delete()
                    return api_response(200, 'Records cleared', 'All the records have been deleted.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/project/record/create/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_record_create(api_token, app_token, project_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/record/create')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/project/record/create/<project_id>')
            if fk.request.method == 'POST':
                project = ProjectModel.objects.with_id(project_id)
                if project != None and project.owner != current_user:
                    return api_response(401, 'Unauthorized access', 'You are this project owner.')
                else:
                    if fk.request.data:
                        data = json.loads(fk.request.data)
                        parent_id = data.get('parent', '')
                        data_pop(data, 'parent')
                        label = data.get('label', 'Recorded at %s'%str(datetime.datetime.utcnow()))
                        data_pop(data, 'label')
                        tags = data.get('tags', [])
                        data_pop(data, 'tags')
                        system = data.get('system', {})
                        data_pop(data, 'system')
                        inputs = data.get('inputs', [])
                        data_pop(data, 'inputs')
                        outputs = data.get('outputs', [])
                        data_pop(data, 'outputs')
                        dependencies = data.get('dependencies', [])
                        data_pop(data, 'dependencies')
                        status = data.get('status', 'unknown')
                        data_pop(data, 'status')
                        environment_id = data.get('environment', None)
                        data_pop(data, 'environment')
                        cloned_from_id = data.get('cloned_from', '')
                        data_pop(data, 'cloned_from')
                        access = data.get('access', 'private')
                        data_pop(data, 'access')
                        # resources_ids = data.get('resources', [])
                        # data_pop(data, 'resources')
                        rationels = data.get('rationels', [])
                        data_pop(data, 'rationels')
                        # resources = []
                        environment = None
                        cloned_from = ''
                        parent = ''
                        if environment_id != None:
                            environment = EnvironmentModel.objects.with_id(environment_id)

                        if cloned_from_id != '':
                            cloned = RecordModel.objects.with_id(cloned_from_id)
                            if cloned != None:
                                cloned_from = str(clone.id)
                        if parent_id != '':
                            parent_inst = RecordModel.objects.with_id(parent_id)
                            if parent_inst != None:
                                parent = str(parent_inst.id)
                        if environment_id == None:
                            history = project.history
                            if len(history) > 0:
                                environment = history[-1] # Create with the latest environment.
                        # if len(resources) > 0:
                        #     for res_id in resources_ids:
                        #         res = FileModel.objects.with_id(res_id)
                        #         if res != None:
                        #             resources.append(res)
                        # print resources
                        if environment != None:
                            record, created = RecordModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), project=project, application=current_app, environment=environment, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                        else:
                            record, created = RecordModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), project=project, application=current_app, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                        
                        if len(data) != 0:
                            body, created = RecordBodyModel.objects.get_or_create(head=record, data=data)
                        logStat(record=record)
                        return api_response(201, 'Record created', record.info())
                    else:
                        return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/record/show/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_record_show(api_token, app_token, record_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/record/show/<record_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/record/show/<record_id>')
            if fk.request.method == 'GET':
                record = RecordModel.objects.with_id(record_id)
                if record == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
                else:
                    if record.project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are this record\'s project owner.')
                    else:
                        return api_response(200, 'Record info', record.extended())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/record/delete/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_record_delete(api_token, app_token, record_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/record/delete/<record_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/record/delete/<record_id>')
            if fk.request.method == 'GET':
                record = RecordModel.objects.with_id(record_id)
                if record == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
                else:
                    if record.project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are this record\'s project owner.')
                    else:
                        # Delete all comments and attachements and files.
                        record.delete()
                        logStat(deleted=True, record=record)
                        return api_response(200, 'Deletion succeeded', 'The record %s was succesfully deleted.'%str(record.id))
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/record/update/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_record_update(api_token, app_token, record_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/record/update/<record_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/record/update/<record_id>')
            if fk.request.method == 'POST':
                record = RecordModel.objects.with_id(record_id)
                if record == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if record.project.owner != current_user:
                        return api_response(401, 'Unauthorized access', 'You are this record\'s project owner.')
                    else:
                        if fk.request.data:
                            data = json.loads(fk.request.data)
                            project_id = data.get('project', None)
                            data_pop(data, 'project')
                            application_id = data.get('application', None)
                            data_pop(data, 'application')
                            parent_id = data.get('parent', None)
                            data_pop(data, 'parent')
                            label = data.get('label', record.label)
                            data_pop(data, 'label')
                            tags = data.get('tags', [])
                            data_pop(data, 'tags')
                            system = data.get('system', record.system)
                            data_pop(data, 'system')
                            inputs = data.get('inputs', [])
                            data_pop(data, 'inputs')
                            outputs = data.get('outputs', [])
                            data_pop(data, 'outputs')
                            dependencies = data.get('dependencies', [])
                            data_pop(data, 'dependencies')
                            status = data.get('status', record.status)
                            data_pop(data, 'status')
                            environment_id = data.get('environment', None)
                            data_pop(data, 'environment')
                            cloned_from_id = data.get('cloned_from', None)
                            data_pop(data, 'cloned_from')
                            access = data.get('access', record.access)
                            data_pop(data, 'access')
                            resources = data.get('resources', [])
                            data_pop(data, 'resources')
                            rationels = data.get('rationels', [])
                            data_pop(data, 'rationels')
                            project = None
                            application = None
                            parent = None
                            environment = None
                            cloned_from = None
                            if project_id == None:
                                project = record.project
                            else:
                                project = ProjectModel.objects.with_id(project_id)
                                if project == None:
                                    project = record.project
                            if application_id == None:
                                application = record.application
                            else:
                                record = ApplicationModel.objects.with_id(application_id)
                                if application == None:
                                    application = record.application
                            if parent_id == None:
                                parent = record.parent
                            else:
                                parent = None
                                parent_inst = RecordModel.objects.with_id(parent_id)
                                if parent_inst != None:
                                    parent = str(parent_inst.id)
                                if parent == None:
                                    parent = record.parent
                            if environment_id == None:
                                environment = record.environment
                            else:
                                environment = EnvironmentModel.objects.with_id(environment_id)
                                if environment == None:
                                    environment = record.environment
                            if cloned_from_id == None:
                                cloned_from = record.cloned_from
                            else:
                                cloned_from = None
                                clone = RecordModel.objects.with_id(parent_id)
                                if clone != None:
                                    cloned_from = str(clone.id)
                                if cloned_from == None:
                                    cloned_from = record.cloned_from
                            record.project = project
                            record.application = application
                            record.parent = parent
                            record.label = label
                            record.system = system
                            record.status = status
                            record.tags.extend(tags)
                            record.access = access
                            record.inputs.extend(inputs)
                            record.outputs.extend(outputs)
                            record.dependencies.extend(dependencies)
                            record.rationels.extend(rationels)
                            record.cloned_from = cloned_from
                            record.environment = environment
                            record.resources.extend(resources)
                            record.save()
                            if len(data) != 0:
                                body, created = RecordBodyModel.objects.get_or_create(head=record)
                                if created:
                                    body.data = data
                                    body.save()
                                else:
                                    body.data = merge_dicts(body.data, data)
                                    body.save()
                            return api_response(201, 'Record updated', project.info())
                        else:
                            return api_response(204, 'Nothing created', 'You must provide the project information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/record/download/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_record_download(api_token, app_token, record_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/record/download/<record_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/record/download/<record_id>')
            if fk.request.method == 'GET':
                record = RecordModel.objects.with_id(record_id)
                if record == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
                else:
                    if record.project.access == 'private' and record.project.owner != current_user and record.access == 'private':
                        return api_response(401, 'Unauthorized access', 'You are this record\'s project owner.')
                    else:
                        prepared = prepare_record(record)
                        if prepared[0] == None:
                            return api_response(404, 'Request suggested an empty response', 'Unable to retrieve a record to download.')
                        else:
                            return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/diffs', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_diffs(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/diffs')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/diffs')
            if fk.request.method == 'GET':
                diffs = DiffModel.objects()
                diffs_dict = {'total_diffs':0, 'diffs':[]}
                for diff in diffs:
                    if (diff.record_from.project.owner != current_user and diff.record_to.project.owner != current_user) and (diff.record_from.access == 'private' and diff.record_to.access == 'private'):
                        pass
                        # return api_response(401, 'Unauthorized access', 'You have to be the owner of one of the two records.')
                    else:
                        diffs_dict['diffs'].append(diff.extended())
                        diffs_dict['total_diffs'] = len(diffs_dict['diffs'])
                return api_response(200, 'Diffs list', diffs_dict)
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/diff/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_diff_create(api_token, app_token):
    logTraffic(endpoint='/private/<api_token>/<app_token>/diff/create')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/diff/create')
            if fk.request.method == 'POST':
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    # sender_id =  data.get('session', None)
                    record_from_id = data.get('from', None)
                    record_to_id = data.get('to', None)
                    method = data.get('method', 'undefined')
                    resources = data.get('resources', [])
                    proposition = data.get('proposition', 'undefined')
                    status = data.get('status', 'undefined')
                    if record_from_id == None or record_to_id == None:
                        return api_response(400, 'Missing mandatory fields', 'A diff should have at least a record from where the diff is linked and a record to which it is linked.')
                    else:
                        sender = current_user
                        record_from = None
                        record_to = None
                        # sender = UserModel.objects(session=sender_id).first()
                        record_from = RecordModel.objects.with_id(record_from_id)
                        record_to = RecordModel.objects.with_id(record_to_id)
                        if sender == None or record_from == None or record_to == None:
                            return api_response(400, 'Missing references mandatory fields', 'A diff should have at least an existing sender, an existing record from where the diff is linked and an existing record to which it is linked.')
                        if (record_to.access != 'private' or (record_from.access == 'private' and record_from.project.owner == sender)) and ((record_from.access == 'private' and record_from.project.owner == sender) or record_from.access != 'private'):
                            diff, created = DiffModel.objects.get_or_create(created_at=datetime.datetime.utcnow(), sender=sender, targeted=record_to.project.owner, record_from=record_from, record_to=record_to, method=method, resources=resources, proposition=proposition, status=status)
                            if not created:
                                return api_response(200, 'Diff already exists', diff.info())
                            else:
                                # logStat(diff=diff)
                                return api_response(201, 'Diff created', diff.info())
                        else:
                            return api_response(401, 'Unauthorized access to records', 'To be able to reference a record you either have to own it or have a non private access to it.')
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/diff/show/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_diff_show(api_token, app_token, diff_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/diff/show/<diff_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/diff/show/<diff_id>')
            if fk.request.method == 'GET':
                diff = DiffModel.objects.with_id(diff_id)
                if diff == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
                else:
                    if (diff.record_from.project.owner != current_user and diff.record_to.project.owner != current_user) and (diff.record_from.access == 'private' and diff.record_to.access == 'private'):
                        return api_response(401, 'Unauthorized access', 'You have to be the owner of one of the two records.')
                    else:
                        return api_response(200, 'Diff info', diff.extended())
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/private/<api_token>/<app_token>/diff/delete/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_diff_delete(api_token, app_token, diff_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/diff/delete/<diff_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/diff/delete/<diff_id>')
            if fk.request.method == 'GET':
                diff = DiffModel.objects.with_id(diff_id)
                if diff == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
                else:
                    # if (diff.record_from.project.owner != current_user and diff.record_to.project.owner != current_user) and (diff.record_from.access == 'private' and diff.record_to.access == 'private'):
                    #     return api_response(401, 'Unauthorized access', 'You have to be the owner of one of the two records.')
                    # else:
                    #     #Delete all the files
                    #     diff.delete()
                    #     logStat(deleted=True, diff=diff)
                    # return api_response(200, 'Deletion succeeded', 'The diff %s was succesfully deleted.'%str(diff.id))
                    return api_response(401, 'Deletion curerently forbidden', 'The diff deletion has been revoked to regular users.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

#++++
@app.route(API_URL + '/private/<api_token>/<app_token>/diff/update/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_diff_update(api_token, app_token, diff_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/diff/update/<diff_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/diff/update/<diff_id>')
        if fk.request.method == 'POST':
            diff = DiffModel.objects.with_id(diff_id)
            if diff == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                if (diff.record_from.project.owner != current_user and diff.record_to.project.owner != current_user):
                    return api_response(401, 'Unauthorized access', 'You have to be the owner of one of the two records.')
                else:
                    if fk.request.data:
                        data = json.loads(fk.request.data)
                        sender_id =  data.get('sender', None)
                        record_from_id = data.get('from', None)
                        record_to_id = data.get('to', None)
                        method = data.get('method', 'undefined')
                        resources = data.get('resources', [])
                        proposition = data.get('proposition', 'undefined')
                        status = data.get('status', 'undefined')
                        sender = None
                        record_from = None
                        record_to = None
                        if sender_id == None:
                            sender = diff.sender
                        else:
                            sender = UserModel.objects.with_id(sender_id)
                            if sender == None:
                                sender = message.sender
                        if record_from_id == None:
                            record_from = diff.record_from
                        else:
                            record_from = RecordModel.objects.with_id(record_from_id)
                            if record_from == None:
                                record_from = diff.record_from
                        if record_to_id == None:
                            record_to = diff.record_to
                        else:
                            record_to = RecordModel.objects.with_id(record_to_id)
                            if record_to == None:
                                record_to = diff.record_to

                        diff.sender = sender
                        diff.receiver = record_to.project.owner
                        diff.record_from = record_from
                        diff.record_to = record_to
                        diff.method = method
                        diff.resources.extend(resources)
                        diff.proposition = proposition
                        diff.status = status
                        diff.save()
                        return api_response(201, 'Diff updated', diff.info())
                    else:
                        return api_response(204, 'Nothing created', 'You must provide the diff information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

# Custom:
# Item resolver: Take an id and try to find the conresponding object and return it with all the meta api
# functions that can be called on it.
# Can be used with a command line tool to enhance a very good way of using an API.

@app.route(API_URL + '/private/<api_token>/<app_token>/resolve/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def user_resolve_item(api_token, app_token, item_id):
    logTraffic(endpoint='/private/<api_token>/<app_token>/resolve/<item_id>')
    current_user = check_api(api_token)
    current_app = check_app(app_token)
    if current_user ==None:
        return api_response(401, 'Unauthorized access', 'The user credential is not authorized.')
    else:
        if current_app ==None:
            return api_response(401, 'Unauthorized access', 'This app credential is not authorized.')
        else:
            logAccess(current_app,'api', '/private/<api_token>/<app_token>/resolve/<item_id>')
            if fk.request.method == 'GET':
                resolution = {'class':'', 'endpoints':[]}
                if item_id == 'root':
                    resolution['class'] = 'UserModel'
                    
                    resolution['endpoints'].append({'meta':['status', '--st'], 'endpoint':'/private/<api_token>/<app_token>/status'})
                    resolution['endpoints'].append({'meta':['connectivity', '--cn'], 'endpoint':'/private/<api_token>/<app_token>/connectivity'})
                    resolution['endpoints'].append({'meta':['profile', '--pf'], 'endpoint':'/private/<api_token>/<app_token>/profile/show'})
                    resolution['endpoints'].append({'meta':['picture', '--pc'], 'endpoint':'/private/<api_token>/<app_token>/user/picture'})
                    resolution['endpoints'].append({'meta':['projects', '--pj'], 'endpoint':'/private/<api_token>/<app_token>/projects'})
                    resolution['endpoints'].append({'meta':['records', '--re'], 'endpoint':'/private/<api_token>/<app_token>/records'})
                    resolution['endpoints'].append({'meta':['messages', '--me'], 'endpoint':'/private/<api_token>/<app_token>/messages'})
                    resolution['endpoints'].append({'meta':['comments', '--cm'], 'endpoint':'/private/<api_token>/<app_token>/comments'})
                    resolution['endpoints'].append({'meta':['diffs', '--di'], 'endpoint':'/private/<api_token>/<app_token>/diffs'})
                    resolution['endpoints'].append({'meta':['files', '--fi'], 'endpoint':'/private/<api_token>/<app_token>/files'})
                    resolution['endpoints'].append({'meta':['search', '--se'], 'endpoint':'/private/<api_token>/<app_token>/search/<query>'})
                    resolution['endpoints'].append({'meta':['search user', '--su'], 'endpoint':'/private/<api_token>/<app_token>/user/search/<query>'})
                    resolution['endpoints'].append({'meta':['search project', '--sp'], 'endpoint':'/private/<api_token>/<app_token>/project/search/<query>'})
                    resolution['endpoints'].append({'meta':['search app', '--sa'], 'endpoint':'/public/app/search/<query>'})
                    resolution['endpoints'].append({'meta':['users', '--us'], 'endpoint':'/public/users'})
                    resolution['endpoints'].append({'meta':['home', '--ho'], 'endpoint':'/private/<api_token>/<app_token>/user/home'})
                    if current_user.group == 'developer':
                        resolution['endpoints'].append({'meta':['apps', '--us'], 'endpoint':'/<app_token>/applications'})
                    return api_response(200, 'Root resolution results'%item_id, resolution)
                item = UserModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'UserModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/public/user/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['picture', '--pc'], 'endpoint':'/public/user/picture/<item_id>'})
                    resolution['endpoints'].append({'meta':['profile', '--pf'], 'endpoint':'/public/profile/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['projects', '--pj'], 'endpoint':'/public/user/projects/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = MessageModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'MessageModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/message/show/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = CommentModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'CommentModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/comment/show/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = ProjectModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'ProjectModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/project/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['history', '--hi'], 'endpoint':'/private/<api_token>/<app_token>/project/envs/<item_id>'})
                    resolution['endpoints'].append({'meta':['head', '--he'], 'endpoint':'/private/<api_token>/<app_token>/project/env/head/<item_id>'})
                    resolution['endpoints'].append({'meta':['comments', '--co'], 'endpoint':'/private/<api_token>/<app_token>/project/comments/<item_id>'})
                    resolution['endpoints'].append({'meta':['records', '--re'], 'endpoint':'/private/<api_token>/<app_token>/project/records/<item_id>'})
                    resolution['endpoints'].append({'meta':['files', '--fi'], 'endpoint':'/private/<api_token>/<app_token>/project/files/<item_id>'})
                    resolution['endpoints'].append({'meta':['download', '--do'], 'endpoint':'/private/<api_token>/<app_token>/project/download/<item_id>'})
                    resolution['endpoints'].append({'meta':['logo', '--lo'], 'endpoint':'/private/<api_token>/<app_token>/project/logo/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = RecordModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'RecordModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/record/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['env', '--en'], 'endpoint':'/private/<api_token>/<app_token>/record/env/<item_id>'})
                    resolution['endpoints'].append({'meta':['comments', '--co'], 'endpoint':'/private/<api_token>/<app_token>/record/comments/<item_id>'})
                    resolution['endpoints'].append({'meta':['diffs', '--di'], 'endpoint':'/private/<api_token>/<app_token>/record/diffs/<item_id>'})
                    resolution['endpoints'].append({'meta':['files', '--fi'], 'endpoint':'/private/<api_token>/<app_token>/record/files/<item_id>'})
                    resolution['endpoints'].append({'meta':['download', '--do'], 'endpoint':'/private/<api_token>/<app_token>/record/download/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = EnvironmentModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'EnvironmentModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/env/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['download', '--do'], 'endpoint':'/private/<api_token>/<app_token>/env/download/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = DiffModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'DiffModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/diff/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['comments', '--co'], 'endpoint':'/private/<api_token>/<app_token>/diff/comments/<item_id>'})
                    resolution['endpoints'].append({'meta':['files', '--fi'], 'endpoint':'/private/<api_token>/<app_token>/diff/files/<item_id>'})
                    resolution['endpoints'].append({'meta':['download', '--do'], 'endpoint':'/private/<api_token>/<app_token>/diff/download/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = FileModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'FileModel'
                    resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/private/<api_token>/<app_token>/file/show/<item_id>'})
                    resolution['endpoints'].append({'meta':['download', '--do'], 'endpoint':'/private/<api_token>/<app_token>/file/download/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                item = ApplicationModel.objects.with_id(item_id)
                if item != None:
                    resolution['class'] = 'ApplicationModel'
                    if current_user.group == 'developer':
                        resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/<app_token>/application/show'})
                        resolution['endpoints'].append({'meta':['connectivity', '--co'], 'endpoint':'/<app_token>/application/connectivity'})
                        resolution['endpoints'].append({'meta':['logo', '--lo'], 'endpoint':'/<app_token>/application/logo/<item_id>'})
                    else:
                        resolution['endpoints'].append({'meta':['show', '--sh'], 'endpoint':'/public/app/show'})
                        resolution['endpoints'].append({'meta':['connectivity', '--co'], 'endpoint':'/public/app/connectivity'})
                        resolution['endpoints'].append({'meta':['logo', '--lo'], 'endpoint':'/public/app/logo/<item_id>'})
                    return api_response(200, 'Item %s resolution results'%item_id, resolution)

                if item == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


#   Search endpoint.