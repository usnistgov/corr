from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from corrdb.common.models import UserModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import FileModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import AccessModel
from corrdb.common.models import StatModel
# from flask.ext.stormpath import user
# from flask.ext.stormpath import login_required
from flask.ext.api import status
import flask as fk
from cloud import app, storage_manager, access_manager, cloud_response, CLOUD_URL, API_HOST, API_PORT, API_MODE, VIEW_HOST, VIEW_PORT, VIEW_MODE
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
from hurry.filesize import size
import hashlib
import os
import mimetypes
from io import StringIO

# CLOUD_VERSION = 1
# CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

#Allow admins to do everything they want. Developers will be able to do specific things with the API
#that normal users can't

@app.route(CLOUD_URL + '/public/user/register', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_register():
    logTraffic(CLOUD_URL, endpoint='/public/user/register')        
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            # application = stormpath_manager.application
            email = data.get('email', '').lower()
            password = data.get('password', '')
            # username = data.get('username', 'username')
            fname = data.get('fname', 'FirstName')
            lname = data.get('lname', 'LastName')
            group = data.get('group', 'user')
            picture_link = data.get('picture', '')
            admin = data.get('admin', {})
            if picture_link == '':
                picture = {'scope':'', 'location':''}
            else:
                picture = {'scope':'remote', 'location':picture_link}
            organisation = data.get('organisation', 'No organisation provided')
            about = data.get('about', 'Nothing about me yet.')
            if email == '' or '@' not in email or password == '':
                # return cloud_response(400, "Bad request", "The email field cannot be empty.")
                return fk.make_response("The email field cannot be empty.", status.HTTP_400_BAD_REQUEST)
            else:
                user_model = access_manager.register(email, password, fname, lname, '')

                if user_model is None:
                    return cloud_response(500, "Account Registration failed", "Your user account creation failed. Please try later.")
                else:
                    (profile_model, created) = ProfileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), user=user_model, fname=fname, lname=lname, organisation=organisation, about=about)
                    print("Token %s"%user_model.api_token)
                    print(fk.request.headers.get('User-Agent'))
                    print(fk.request.remote_addr)
                    # print "Connected_at: %s"%str(user_model.connected_at)
                    # user_model.connected_at = datetime.datetime.utcnow()
                    # user_model.save()
                    user_model.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    user_model.retoken()
                    # print "Connected_at: %s"%str(user_model.connected_at)
                    print("Session: %s"%user_model.session)

                    logStat(user=user_model)
                    # return cloud_response(400, "Bad request", "The email field cannot be empty.")
                    return fk.Response(json.dumps({'session':user_model.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                # todo.
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/password/reset', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_password_reset():
    logTraffic(CLOUD_URL, endpoint='/public/user/password/reset')
    if fk.request.method == 'POST':
        print("Request: %s"%str(fk.request.data))
        if fk.request.data:
            data = json.loads(fk.request.data)
            # application = stormpath_manager.application
            email = data.get('email', '')
            account = access_manager.reset_password(email)
            # account = application.send_password_reset_email(email)
            if account != None:
                return fk.Response('An email has been sent to renew your password', status.HTTP_200_OK)
            else:
                return fk.make_response('Password reset failed.', status.HTTP_401_UNAUTHORIZED)
                    
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/user/password/change', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_password_change():
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/password/change')        
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error-401/?action=change_denied'.format(VIEW_HOST, VIEW_PORT))
        else:
            if not access_resp[0]:
                return fk.make_response('Password change failed.', status.HTTP_401_UNAUTHORIZED)
            else:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/password/change')
                user_model = access_resp[1]
                if fk.request.data:
                    password = data.get('password', '')
                    response = access_manager.change_password(user_model, password)
                    if response is None:
                        return fk.make_response('Password change failed.', status.HTTP_401_UNAUTHORIZED)
                    else:
                        return fk.Response('Password changed', status.HTTP_200_OK)
                else:
                    return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/login', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_login():
    logTraffic(CLOUD_URL, endpoint='/public/user/login')
    if fk.request.method == 'POST':
        print("Request: %s"%str(fk.request.data))
        if fk.request.data:
            data = json.loads(fk.request.data)
            # application = stormpath_manager.application
            email = data.get('email', '').lower()
            password = data.get('password', '')
            if email == '' or '@' not in email:
                return fk.make_response("The email field cannot be empty.", status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    account = access_manager.login(email, password)
                    if account == None:
                        return fk.make_response('Unknown user account.', status.HTTP_401_UNAUTHORIZED)
                    print("Token %s"%account.api_token)
                    print(fk.request.headers.get('User-Agent'))
                    print(fk.request.remote_addr)
                    # print "Connected at %s"%str(account.connected_at)
                    # account.connected_at = datetime.datetime.utcnow()
                    # account.save()
                    account.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    # print "Session: %s"%account.session
                    return fk.Response(json.dumps({'session':account.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                    # return fk.redirect('{0}:{1}/?session={2}'.format(VIEW_HOST, VIEW_PORT, account.session))
                except:
                    print(str(traceback.print_exc()))
                    return fk.make_response('Login failed.', status.HTTP_401_UNAUTHORIZED)
                    
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/user/sync', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_sync(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/sync')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.make_response('Sync failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/sync')
            user_model = access_resp[1]
            print(fk.request.path)
            user_model.sess_sync("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            return fk.Response(json.dumps({'session':user_model.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/user/logout', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_logout(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/logout')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error-401/?action=logout_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/logout')
            user_model = access_resp[1]
            user_model.renew("%sLogout"%(fk.request.headers.get('User-Agent')))
            return fk.Response('Logout succeed', status.HTTP_200_OK)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/<hash_session>/user/unregister', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_unregister(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/unregister')        
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error-401/?action=unregister_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/unregister')
            user_model = access_resp[1]
            return fk.make_response('Currently not implemented. Try later.', status.HTTP_501_NOT_IMPLEMENTED)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/<hash_session>/user/dashboard', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_dashboard(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/dashboard')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error-401/?action=access_denied'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/dashboard')
            user_model = access_resp[1]
            profile_model = ProfileModel.objects(user=user_model).first()
            dashboard = {}
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            projects = ProjectModel.objects(owner=user_model)
            if profile_model is not None:
                dashboard["profile"] = {'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about}
            dashboard["version"] = version
            print("Version {0}".format( dashboard["version"]))
            dashboard["records_total"] = 0
            dashboard["projects_total"] = len(projects)
            dashboard["records_total"] = 0
            dashboard["environments_total"] = 0
            dashboard["projects"] = []
            for project in projects:
                project_dash = {"name":project.name, "records":{"January":{"number":0, "size":0}, "February":{"number":0, "size":0}, "March":{"number":0, "size":0}, "April":{"number":0, "size":0}, "May":{"number":0, "size":0}, "June":{"number":0, "size":0}, "July":{"number":0, "size":0}, "August":{"number":0, "size":0}, "September":{"number":0, "size":0}, "October":{"number":0, "size":0}, "November":{"number":0, "size":0}, "December":{"number":0, "size":0}}}
                records = RecordModel.objects(project=project)
                dashboard["records_total"] += len(records)
                for record in records:
                    environment = record.environment
                    size = 0
                    try:
                        size = environment.bundle["size"]
                    except:
                        size = 0

                    dashboard["environments_total"] += size

                    month = str(record.created_at).split("-")[1]
                    if month == "01":
                        project_dash["records"]["January"]["number"] += 1
                        project_dash["records"]["January"]["size"] += size
                    if month == "02":
                        project_dash["records"]["February"]["number"] += 1
                        project_dash["records"]["February"]["size"] += size
                    if month == "03":
                        project_dash["records"]["March"]["number"] += 1
                        project_dash["records"]["March"]["size"] += size
                    if month == "04":
                        project_dash["records"]["April"]["number"] += 1
                        project_dash["records"]["April"]["size"] += size
                    if month == "05":
                        project_dash["records"]["May"]["number"] += 1
                        project_dash["records"]["May"]["size"] += size
                    if month == "06":
                        project_dash["records"]["June"]["number"] += 1
                        project_dash["records"]["June"]["size"] += size
                    if month == "07":
                        project_dash["records"]["July"]["number"] += 1
                        project_dash["records"]["July"]["size"] += size
                    if month == "08":
                        project_dash["records"]["August"]["number"] += 1
                        project_dash["records"]["August"]["size"] += size
                    if month == "09":
                        project_dash["records"]["September"]["number"] += 1
                        project_dash["records"]["September"]["size"] += size
                    if month == "10":
                        project_dash["records"]["October"]["number"] += 1
                        project_dash["records"]["October"]["size"] += size
                    if month == "11":
                        project_dash["records"]["November"]["number"] += 1
                        project_dash["records"]["November"]["size"] += size
                    if month == "12":
                        project_dash["records"]["December"]["number"] += 1
                        project_dash["records"]["December"]["size"] += size
                dashboard["projects"].append(project_dash)
            return fk.Response(json.dumps(dashboard, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/<hash_session>/user/update', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_update(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/update')  
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        if access_resp[1] is None:
            return fk.make_response('Account update denied.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/update')
            user_model = access_resp[1]
            if fk.request.data:
                data = json.loads(fk.request.data)
                # application = stormpath_manager.application
                #Update stormpath user if password is affected
                #Update local profile data and picture if other data are affected.
                profile_model = ProfileModel.objects(user=user_model).first_or_404()
                fname = data.get("fname", profile_model.fname)
                lname = data.get("lname", profile_model.lname)
                password = data.get("pwd", "")
                organisation = data.get("org", profile_model.organisation)
                about = data.get("about", profile_model.about)
                # When picture given as a json field and not file path.
                picture_link = data.get("picture", "")
                picture = profile_model.picture
                if picture_link != "":
                    picture['location'] = picture_link

                print("Fname: %s"%fname)
                print("Lname: %s"%lname)

                profile_model.fname = fname
                profile_model.lname = lname
                profile_model.organisation = organisation
                profile_model.about = about
                profile_model.picture = picture

                profile_model.save()

                if password != "":
                    response = access_manager.change_password(user_model, password)
                    if response is None:
                        return fk.make_response('Password change failed in stormpath.', status.HTTP_401_UNAUTHORIZED)
                return fk.Response('Account update succeed', status.HTTP_200_OK)
            else:
                return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/file/upload/<group>/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_file_upload(hash_session, group, item_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/file/upload/<group>/<item_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error-401/?action=upload_denied'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/file/upload/<group>/<item_id>')
            if group not in ["input", "output", "dependencie", "file", "descriptive", "diff", "resource-record", "resource-env", "resource-app", "attach-comment", "attach-message", "picture" , "logo-project" , "logo-app" , "resource", "bundle"]:
                return cloud_response(405, 'Method Group not allowed', 'This endpoint supports only a specific set of groups.')
            else:
                if group == "picture":
                    item_id = str(user_model.id)
                print("item_id: %s"%item_id)
                if fk.request.files:
                    file_obj = fk.request.files['file']
                    filename = '%s_%s'%(item_id, file_obj.filename)
                    _file, created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), name=filename)
                    if not created:
                        return cloud_response(200, 'File already exists with same name for this item', _file.info())
                    else:
                        print("filename: %s"%filename)
                        encoding = ''
                        if file_obj != None:
                            old_file_position = file_obj.tell()
                            file_obj.seek(0, os.SEEK_END)
                            size = file_obj.tell()
                            file_obj.seek(old_file_position, os.SEEK_SET)
                        else:
                            size = 0
                        if item_id == "none":
                            storage = '%s_%s'%(str(user_model.id), file_obj.filename)
                        else:
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
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is an input file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'output':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is an output file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'dependencie':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is an dependency file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'descriptive':
                            item = ProjectModel.objects.with_id(item_id)
                            owner = item.owner
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is a resource file for the project %s'%(file_obj.filename, str(item.id))
                        elif group == 'diff':
                            item = DiffModel.objects.with_id(item_id)
                            owner1 = item.sender
                            owner2 = item.targeted
                            if user_model != owner1 and user_model != owner2:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is a resource file for the collaboration %s'%(file_obj.filename, str(item.id))
                        elif 'attach' in group:
                            if 'message' in group:
                                item = MessageModel.objects.with_id(item_id)
                                owner1 = item.sender
                                owner2 = item.receiver
                                if user_model != owner1 and user_model != owner2:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is an attachement file for the message %s'%(file_obj.filename, str(item.id))
                            elif 'comment' in group:
                                item = CommentModel.objects.with_id(item_id)
                                owner = item.sender
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
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
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                        elif group == 'picture':
                            item = ProfileModel.objects(user=user_model).first()
                            owner = item.user
                            if user_model != owner:
                                return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                            description = '%s is the picture file of the profile %s'%(file_obj.filename, str(item.id))
                            if item.picture != None:
                                old_storage = item.picture.storage
                                print("Old storage %s"%old_storage)
                                _file.delete()
                                _file = item.picture
                            print('%s is the picture file of the profile %s'%(file_obj.filename, str(item.id)))
                        elif 'logo' in group:
                            if 'app' in group:
                                item = ApplicationModel.objects.with_id(item_id)
                                owner = item.developer
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is the logo file of the application %s'%(file_obj.filename, str(item.id))
                            elif 'project' in group:
                                item = ProjectModel.objects.with_id(item_id)
                                owner = item.owner
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is the logo file of the project %s'%(file_obj.filename, str(item.id))
                            _file.delete()
                            _file = item.logo
                        elif 'resource' in group:
                            if 'record' in group:
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is an resource file for the record %s'%(file_obj.filename, str(item.id))
                            elif 'env' in group:
                                item = EnvironmentModel.objects.with_id(item_id)
                                rec_temp = RecordModel.objects(environment=item).first()
                                owner = rec_temp.project.owner
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is a resource file for the environment %s'%(file_obj.filename, str(item.id))
                            elif 'app' in group:
                                item = ApplicationModel.objects.with_id(item_id)
                                owner = item.developer
                                if user_model != owner:
                                    return cloud_response(401, 'Unauthorized access', 'You are not an owner of this item.')
                                description = '%s is a resource file for the app %s'%(file_obj.filename, str(item.id))
                            group_ = group.split('-')[0]

                        if item == None:
                            if group != 'picture' or group != 'logo':
                                return cloud_response(400, 'Missing mandatory instance', 'A file should reference an existing item.')
                        else:
                            _file.description = description
                            _file.encoding = encoding
                            _file.size = size
                            # _file.path = path
                            _file.owner = user_model
                            _file.storage = storage
                            _file.location = location
                            _file.mimetype = mimetype
                            _file.group = group_
                            _file.save()
                            uploaded = storage_manager.storage_upload_file(_file, file_obj)
                            if not uploaded[0]:
                                _file.delete()
                                return cloud_response(500, 'An error occured', "%s"%uploaded[1])
                            else:
                                logStat(file_obj=_file)
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
                                    # _file.delete()
                                    if item.storage != storage:
                                        storage_manager.storage_delete_file('bundle',item.storage)
                                    item.encoding = encoding
                                    item.size = size
                                    item.storage = storage
                                    item.mimetype = mimetype
                                    item.save()
                                elif 'attach' in group:
                                    item.attachments.append(str(_file.id))
                                elif group == 'picture':
                                    if item.picture != None:
                                        if _file.storage != old_storage:
                                            deleted = storage_manager.storage_delete_file('picture',old_storage)
                                            if deleted:
                                                logStat(deleted=True, file_obj=item.picture)
                                        else:
                                            print("Old not deleted!")
                                    else:
                                        print("No picture")
                                    if item != None:
                                        item.picture = _file
                                elif 'logo' in group:
                                    if item.logo.location != storage:
                                        storage_manager.storage_delete_file('logo',item.logo.storage)
                                    if item != None:
                                        item.logo = _file
                                elif 'resource' in group:
                                    item.resources.append(str(_file.id))
                                if item != None:
                                    item.save()
                                return cloud_response(201, 'New file created', _file.info())
                else:
                    return cloud_response(204, 'Nothing created', 'You must provide the file information.')
    else:
        return cloud_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')


# Figure this out when all the updates are done.
@app.route(CLOUD_URL + '/public/user/contactus', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_contactus(): #Setup and start smtp server on the instance
    logTraffic(CLOUD_URL, endpoint='/public/user/contactus')
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            try:
                email = data.get("email", "")
                message = data.get("message", "")
                msg = MIMEText("Dear user,\n You contacted us regarding the following matter:\n-------\n%s\n-------\nWe hope to reply shortly.\nBest regards,\n\nDDSM team."%message)
                msg['Subject'] = 'DDSM -- You contacted us!'
                msg['From'] = "yannick.congo@gmail.com" # no_reply@ddsm.nist.gov
                msg['To'] = email
                msg['CC'] = "yannick.congo@gmail.com"
                s = smtplib.SMTP('localhost')
                s.sendmail("yannick.congo@gmail.com", email, msg.as_string())
                s.quit()
                return fk.Response('Message sent.', status.HTTP_200_OK)
            except:
                print(str(traceback.print_exc()))
                return fk.make_response("Could not send the email.", status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/version', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_version(): #Setup and start smtp server on the instance
    logTraffic(CLOUD_URL, endpoint='/public/version')
        
    if fk.request.method == 'GET':
        version = 'N/A'
        try:
            from corrdb import __version__
            version = __version__
        except:
            pass
        return fk.Response(version, status.HTTP_200_OK)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/user/config', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_config(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/config')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            cloud_response(401, 'Unauthorized access', 'The user credential is not authorized.')
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/config')
            config_buffer = StringIO()
            config_content = {'default':{'api':{'host':API_HOST, 'port':API_PORT, 'key':user_model.api_token}}}
            config_buffer.write(json.dumps(config_content, sort_keys=True, indent=4, separators=(',', ': ')))
            config_buffer.seek(0)
            return fk.send_file(config_buffer, as_attachment=True, attachment_filename='config.json', mimetype='application/json')
    else:
        return cloud_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CLOUD_URL + '/private/<hash_session>/user/picture', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_picture(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/picture')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            cloud_response(401, 'Unauthorized access', 'The user credential is not authorized.')
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/picture')
            profile = ProfileModel.objects(user=user_model).first()
            if profile == None:
                picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                if picture_buffer == None:
                    return cloud_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                else:
                    return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
            else:
                picture = profile.picture
                print(profile.picture.storage)
                if picture == None:
                    picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                    if picture_buffer == None:
                        return cloud_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                elif picture.location == 'local' and 'http://' not in picture.storage:
                    # print str(picture.to_json())
                    picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                    if picture_buffer == None:
                        picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                        else:
                            return cloud_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                    else:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                elif picture.location == 'remote':
                    picture_buffer = storage_manager.web_get_file(picture.storage)
                    if picture_buffer != None:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                        if picture_buffer == None:
                            return cloud_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                        else:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                else:
                    # solve the file situation and return the appropriate one.
                    if 'http://' in picture.storage:
                        picture.location = 'remote'
                        picture.save()
                        picture_buffer = storage_manager.web_get_file(picture.storage)
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                            if picture_buffer == None:
                                return cloud_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                            else:
                                return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                    else:
                        picture.location = 'local'
                        picture.save()
                        picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                        if picture_buffer == None:
                            picture_buffer = storage_manager.web_get_file('{0}://{1}:{2}/images/picture.png'.format(VIEW_MODE, VIEW_HOST, VIEW_PORT))
                            if picture_buffer != None:
                                return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                            else:
                                return cloud_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
    else:
        return cloud_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(CLOUD_URL + '/private/<hash_session>/user/trusted', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_truested(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/trusted')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.make_response('Trusting failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/trusted')
            # return fk.Response('Trusting succeed', status.HTTP_200_OK)
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            return fk.Response(json.dumps({'version':version}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/home', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_home():
    logTraffic(CLOUD_URL, endpoint='/public/user/home')
    if fk.request.method == 'GET':
        users = UserModel.objects()
        projects = ProjectModel.objects()
        records = RecordModel.objects()
        environments = EnvironmentModel.objects()
        apps = ApplicationModel.objects()
        traffic = TrafficModel.objects()
        print(fk.request.path)

        users_stat = {"number":len(users)}
        users_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="user")]

        projects_stat = {"number":len(projects)}
        projects_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="project")]

        storage_stat = {}
        storage_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="storage")]

        apps_stat = {"size":len(apps)}
        apps_stat["history"] = [json.loads(app.to_json()) for app in StatModel.objects(category="application")]

        traffic_stat = {"size":len(traffic)}
        traffic_stat["history"] = [json.loads(tr.to_json()) for tr in traffic]

        amount = 0
        for user in users:
            try:
                amount += user.quota
            except:
                amount += 0

        storage_stat["size"] = size(amount)

        version = 'N/A'
        try:
            from corrdb import __version__
            version = __version__
        except:
            pass

        records_stat = {"number":len(records)}
        records_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="record")]

        return fk.Response(json.dumps({'version':version, 'traffic':traffic_stat, 'users':users_stat, 'apps':apps_stat, 'projects':projects_stat, 'records':records_stat, 'storage':storage_stat}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/<hash_session>/user/profile', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_profile(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/profile')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.make_response('profile get failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/profile')
            profile_model = ProfileModel.objects(user=user_model).first()
            if profile_model == None:
                profile_model, created = ProfileModel.objects.get_or_create(user=user_model, fname="None", lname="None", organisation="None", about="None")
                if created:
                    profile_model.created_at=str(datetime.datetime.utcnow())
                    profile_model.save()
            print(fk.request.path)
            return fk.Response(json.dumps({'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'email':user_model.email, 'session':user_model.session, 'api':user_model.api_token}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/<hash_session>/user/renew', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def user_renew(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/renew')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.make_response('Renew token failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/renew')
            print(fk.request.path)
            user_model.retoken()
            return fk.Response(json.dumps({'api':user_model.api_token}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/recover', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def cloud_public_user_recover():
    logTraffic(CLOUD_URL, endpoint='/public/user/recover')
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            try:
                email = data.get("email", "")
                if email == "":
                    return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
                else:
                    account = access_manager.reset_password(email)
                    if account != None:
                        return fk.Response('Recovery email sent from stormpath.', status.HTTP_200_OK)
                    else:
                        return fk.make_response('Password reset failed.', status.HTTP_401_UNAUTHORIZED)
            except:
                print(str(traceback.print_exc()))
                return fk.make_response("Could not send the email.", status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/picture/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def cloud_public_user_picture(user_id):
    logTraffic(CLOUD_URL, endpoint='/public/user/picture/<user_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
        else:
            profile_model = ProfileModel.object(user=user_model).first_or_404()
            if profile_model.picture['scope'] == 'remote':
                return fk.redirect(profile_model.picture['location'])
            elif profile_model.picture['scope'] == 'local':
                if profile_model.picture['location']:
                    picture = load_picture(profile_model)
                    print(picture[1])
                    return fk.send_file(
                        picture[0],
                        mimetypes.guess_type(picture[1])[0],
                        # as_attachment=True,
                        attachment_filename=profile_model.picture['location'],
                    )
                else:
                    print("Failed because of picture location not found.")
                    return fk.make_response('Empty location. Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


# Picture upload
#    Update the picture field to: local and the name of the file.

#Picture get link to retrieve file