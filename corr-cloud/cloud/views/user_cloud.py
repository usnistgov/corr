from corrdb.common import logAccess, logStat, logTraffic, crossdomain, basicAuthSession
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
from corrdb.common.models import BundleModel
from flask.ext.api import status
import flask as fk
from cloud import app, storage_manager, access_manager, cloud_response, CLOUD_URL, API_HOST, API_PORT, VIEW_HOST, VIEW_PORT, MODE, ACC_SEC, CNT_SEC
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
from hurry.filesize import size
import hashlib
import os
import mimetypes
from io import BytesIO

@app.route(CLOUD_URL + '/public/user/register', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_register():
    logTraffic(CLOUD_URL, endpoint='/public/user/register')        
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            email = data.get('email', '').lower()
            password = data.get('password', '')
            fname = data.get('fname', 'FirstName')
            lname = data.get('lname', 'LastName')
            group = data.get('group', 'user')
            picture_link = data.get('picture', '')
            admin = data.get('admin', '')
            if picture_link == '':
                picture = {'scope':'', 'location':''}
            else:
                picture = {'scope':'remote', 'location':picture_link}
            organisation = data.get('organisation', 'No organisation provided')
            about = data.get('about', 'Nothing about me yet.')
            if email == '' or '@' not in email or password == '':
                return fk.Response('Invalid email or password.', status.HTTP_400_BAD_REQUEST)
                # return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
            else:
                created, user_model = access_manager.register(email, password, fname, lname, '')
                if not created:
                    return fk.Response('This email is already used.', status.HTTP_401_UNAUTHORIZED)
                else:
                    if user_model is None:
                        # return fk.redirect('{0}:{1}/error/?code=500'.format(VIEW_HOST, VIEW_PORT))
                        return fk.Response('Unable to create the user account.', status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        (profile_model, created) = ProfileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), user=user_model, fname=fname, lname=lname, organisation=organisation, about=about)
                        print("Token %s"%user_model.api_token)
                        print(fk.request.headers.get('User-Agent'))
                        print(fk.request.remote_addr)
                        user_model.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                        user_model.retoken()
                        print("Session: %s"%user_model.session)
                        if admin != '':
                            admin_account = UserModel.objects(session=admin).first()
                            if admin_account and admin_account.group == "admin":
                                user_model.group = group
                                user_model.save()
                                user_info = {}
                                user_info["created"] = str(user_model.created_at)
                                user_info["id"] = str(user_model.id)
                                user_info["auth"] = user_model.auth
                                user_info["max-quota"] = user_model.max_quota
                                user_info["usage"] = round(100*user_model.quota/(user_model.max_quota*1024*1024*1024), 2)
                                user_info["group"] = user_model.group
                                user_info["email"] = user_model.email
                                user_info["fname"] = profile_model.fname
                                user_info["lname"] = profile_model.lname
                                user_info["org"] = profile_model.organisation
                                user_info["about"] = profile_model.about
                                user_info["apps"] = user_model.info()['total_apps']
                                user_info["projects"] = user_model.info()['total_projects']
                                user_info["records"] = user_model.info()['total_records']
                                return cloud_response(201, 'Your account was successfully created', user_info)

                        if access_manager.secur:
                            return fk.Response('Your account was successfully created. We recommend that you check your emails in case of required verification. And wait for admin approval.', status.HTTP_200_OK)
                        else:
                            return fk.Response('Your account was successfully created. We recommend that you check your emails in case of required verification.', status.HTTP_200_OK)
                        # return fk.Response(json.dumps({'session':user_model.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/password/reset', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_password_reset():
    logTraffic(CLOUD_URL, endpoint='/public/user/password/reset')
    if fk.request.method == 'POST':
        print("Request: %s"%str(fk.request.data))
        if fk.request.data:
            data = json.loads(fk.request.data)
            email = data.get('email', '')
            account = access_manager.reset_password(email)
            if account != None:
                return fk.Response('An email has been sent to renew your password', status.HTTP_200_OK)
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/password/change', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_password_change():
    logTraffic(CLOUD_URL, endpoint='/private/user/password/change')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            if not access_resp[0]:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                logAccess(CLOUD_URL, 'cloud', '/private/user/password/change')
                user_model = access_resp[1]
                if fk.request.data:
                    password = data.get('password', '')
                    response = access_manager.change_password(user_model, password)
                    if response is None:
                        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.Response('Password changed', status.HTTP_200_OK)
                else:
                    return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/login', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_login():
    logTraffic(CLOUD_URL, endpoint='/public/user/login')
    if fk.request.method == 'POST':
        print("Request: %s"%str(fk.request.data))
        if fk.request.data:
            data = json.loads(fk.request.data)
            email = data.get('email', '').lower()
            password = data.get('password', '')
            if email == '' or '@' not in email:
                return fk.Response('Invalid email.', status.HTTP_400_BAD_REQUEST)
                # return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
            else:
                try:
                    account = access_manager.login(email, password)

                    if account == None:
                        return fk.Response('Unknown email or password. Maybe you should register. Please also make sure you verified your email by clicking the link we might have sent you.{0}'.format(hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()), status.HTTP_401_UNAUTHORIZED)
                        # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                    if access_manager.secur and account.group != "admin":
                        # access = account.extend.get('access', 'verified')
                        # account.extend['access'] = access
                        # account.save()
                        if account.auth == 'signup':
                            return fk.Response('Your account is pending verification from the admin. We appologise for this convenience. For security reasons this instance requires account moderation.', status.HTTP_401_UNAUTHORIZED)
                    if account.auth == 'blocked':
                        return fk.Response('Your account is blocked. We appologise for this convenience. Contact the admin for further actions.', status.HTTP_401_UNAUTHORIZED)
                    elif account.auth == 'unregistered':
                        return fk.Response('You unregistered. We appologise for this convenience. Contact the admin for further actions.', status.HTTP_401_UNAUTHORIZED)
                    print("Token %s"%account.api_token)
                    print(fk.request.headers.get('User-Agent'))
                    print(fk.request.remote_addr)
                    account.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    return fk.Response(json.dumps({'session':account.session, 'group':account.group}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                except:
                    print(str(traceback.print_exc()))
                    return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                    # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                    
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/sync', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_sync():
    logTraffic(CLOUD_URL, endpoint='/private/user/sync')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/sync')
            user_model = access_resp[1]
            print(fk.request.path)
            user_model.sess_sync("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            return fk.Response(json.dumps({'session':user_model.session, 'group':user_model.group}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/logout', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_logout():
    logTraffic(CLOUD_URL, endpoint='/private/user/logout')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/logout')
            user_model = access_resp[1]
            user_model.renew("%sLogout"%(fk.request.headers.get('User-Agent')))
            return fk.Response('Logout succeed', status.HTTP_200_OK)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/unregister', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_unregister():
    logTraffic(CLOUD_URL, endpoint='/private/user/unregister') 
    hash_session = basicAuthSession(fk.request)       
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/unregister')
            user_model = access_resp[1]
            return fk.redirect('{0}:{1}/error/?code=501'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/dashboard', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_dashboard():
    logTraffic(CLOUD_URL, endpoint='/private/user/dashboard')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/dashboard')
            user_model = access_resp[1]
            profile_model = ProfileModel.objects(user=user_model).first()
            dashboard = {}
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            if user_model.group == "admin":
                projects = ProjectModel.objects()
            else:
                projects = ProjectModel.objects(owner=user_model)
            if profile_model is not None:
                dashboard["profile"] = {'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'max-quota':user_model.max_quota}
            dashboard["version"] = version
            print("Version {0}".format( dashboard["version"]))
            dashboard["records_total"] = 0
            dashboard["projects_total"] = len(projects)
            dashboard["records_total"] = 0
            dashboard["environments_total"] = 0
            dashboard["projects"] = []
            for project in projects:
                project_dash = {"name":"{0}~{1}".format(project.owner.email, project.name), "records":{"January":{"number":0, "size":0}, "February":{"number":0, "size":0}, "March":{"number":0, "size":0}, "April":{"number":0, "size":0}, "May":{"number":0, "size":0}, "June":{"number":0, "size":0}, "July":{"number":0, "size":0}, "August":{"number":0, "size":0}, "September":{"number":0, "size":0}, "October":{"number":0, "size":0}, "November":{"number":0, "size":0}, "December":{"number":0, "size":0}}}
                records = RecordModel.objects(project=project)
                dashboard["records_total"] += len(records)
                dashboard["environments_total"] += len(project.history)
                size = 0
                for record in records:
                    month = str(record.created_at).split("-")[1]
                    try:
                        env = record.environment
                        if env:
                            bundle = env.bundle
                            if bundle:
                                size = long(bundle.size)
                    except:
                        pass
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
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/update', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_update():
    logTraffic(CLOUD_URL, endpoint='/private/user/update') 
    hash_session = basicAuthSession(fk.request) 
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/update')
            user_model = access_resp[1]
            if fk.request.data:
                data = json.loads(fk.request.data)
                profile_model = ProfileModel.objects(user=user_model).first_or_404()
                fname = data.get("fname", profile_model.fname)
                lname = data.get("lname", profile_model.lname)
                user_model.save()
                max_quota = data.get("max-quota", user_model.max_quota)
                password = data.get("pwd", "")
                organisation = data.get("org", profile_model.organisation)
                about = data.get("about", profile_model.about)
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

                user_model.max_quota = float(max_quota)
                user_model.save()

                if password != "":
                    response = access_manager.change_password(user_model, password)
                    if response is None:
                        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                return fk.Response('Account update succeed', status.HTTP_200_OK)
            else:
                return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/account/update/<account_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def account_update(account_id):
    logTraffic(CLOUD_URL, endpoint='/private/account/update/<account_id>')  
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        if access_resp[1] is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/account/update/<account_id>')
            user_model = access_resp[1]
            if user_model.group != "admin":
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
                    account_model = UserModel.objects.with_id(account_id)
                    if account_model is None:
                        return fk.Response('Unable to find the user account.', status.HTTP_401_UNAUTHORIZED)
                    else:
                        data = json.loads(fk.request.data)
                        profile_model = ProfileModel.objects(user=account_model).first_or_404()
                        group = data.get("group", account_model.group)
                        auth = data.get("auth", account_model.auth)
                        fname = data.get("fname", profile_model.fname)
                        lname = data.get("lname", profile_model.lname)
                        organisation = data.get("org", profile_model.organisation)
                        about = data.get("about", profile_model.about)
                        max_quota = data.get("max-quota", account_model.max_quota)

                        account_model.group = group
                        account_model.auth = auth
                        account_model.max_quota = float(max_quota)

                        profile_model.fname = fname
                        profile_model.lname = lname
                        profile_model.organisation = organisation
                        profile_model.about = about

                        profile_model.save()
                        account_model.save()

                        return fk.Response('Account update succeed', status.HTTP_200_OK)
                else:
                    return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/file/upload/<group>/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_file_upload(group, item_id):
    logTraffic(CLOUD_URL, endpoint='/private/file/upload/<group>/<item_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            return fk.Response('Unable to find this account.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/file/upload/<group>/<item_id>')
            if group not in ["input", "output", "dependencie", "file", "descriptive", "diff", "resource-record", "resource-env", "resource-app", "attach-comment", "attach-message", "picture" , "logo-project" , "logo-app" , "resource", "bundle"]:
                return cloud_response(405, 'Method Group not allowed', 'This endpoint supports only a specific set of groups.')
            else:
                if fk.request.args:
                    checksum = fk.request.args.get('checksum')
                else:
                    checksum = None
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
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                            description = '%s is an input file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'output':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            if user_model != owner:
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                            description = '%s is an output file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'dependencie':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            if user_model != owner:
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                            description = '%s is an dependency file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'descriptive':
                            item = ProjectModel.objects.with_id(item_id)
                            owner = item.owner
                            if user_model != owner:
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                            description = '%s is a resource file for the project %s'%(file_obj.filename, str(item.id))
                        elif group == 'diff':
                            item = DiffModel.objects.with_id(item_id)
                            owner1 = item.sender
                            owner2 = item.targeted
                            if user_model != owner1 and user_model != owner2:
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                            description = '%s is a resource file for the collaboration %s'%(file_obj.filename, str(item.id))
                        elif 'attach' in group:
                            if 'message' in group:
                                item = MessageModel.objects.with_id(item_id)
                                owner1 = item.sender
                                owner2 = item.receiver
                                if user_model != owner1 and user_model != owner2:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is an attachement file for the message %s'%(file_obj.filename, str(item.id))
                            elif 'comment' in group:
                                item = CommentModel.objects.with_id(item_id)
                                owner = item.sender
                                if user_model != owner:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
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
                                return cloud_response(401, 'Unauthorized upload', "Unauthorized owner.")
                                # return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                        elif group == 'picture':
                            item = ProfileModel.objects(user=user_model).first()
                            owner = item.user
                            if user_model != owner:
                                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
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
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is the logo file of the application %s'%(file_obj.filename, str(item.id))
                            elif 'project' in group:
                                item = ProjectModel.objects.with_id(item_id)
                                owner = item.owner
                                if user_model != owner:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is the logo file of the project %s'%(file_obj.filename, str(item.id))
                            _file.delete()
                            _file = item.logo
                        elif 'resource' in group:
                            if 'record' in group:
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                if user_model != owner:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is an resource file for the record %s'%(file_obj.filename, str(item.id))
                            elif 'env' in group:
                                item = EnvironmentModel.objects.with_id(item_id)
                                rec_temp = RecordModel.objects(environment=item).first()
                                owner = rec_temp.project.owner
                                if user_model != owner:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is a resource file for the environment %s'%(file_obj.filename, str(item.id))
                            elif 'app' in group:
                                item = ApplicationModel.objects.with_id(item_id)
                                owner = item.developer
                                if user_model != owner:
                                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                                description = '%s is a resource file for the app %s'%(file_obj.filename, str(item.id))
                            group_ = group.split('-')[0]

                        if item == None:
                            if group != 'picture' or group != 'logo':
                                return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
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
                                if checksum and checksum != _file.checksum:
                                    _file.delete()
                                    return cloud_response(401, 'Unauthorized upload', "Invalid checksum received: {0} and computed: {1}".format(checksum, _file.checksum))
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
                                    item.checksum = _file.checksum
                                    if item.storage and item.storage != storage:
                                        storage_manager.storage_delete_file('bundle', item.storage)
                                        return cloud_response(401, 'Unauthorized upload', "Inconsistent storage location.")
                                    if checksum and checksum != _file.checksum:
                                        storage_manager.storage_delete_file('bundle', item.storage)
                                        return cloud_response(401, 'Unauthorized upload', "Invalid checksum.")
                                    del _file
                                    item.encoding = encoding
                                    item.size = size
                                    item.storage = storage
                                    item.mimetype = mimetype
                                    item.save()
                                    return cloud_response(201, 'New bundle file uploaded', item.info())
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
                    return cloud_response(204, 'No content provided', "No data in the request")
                    # return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/contactus', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_contactus():
    logTraffic(CLOUD_URL, endpoint='/public/user/contactus')
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            try:
                email = data.get("email", "")
                message = data.get("message", "")
                msg = MIMEText("Dear user,\n You contacted us regarding the following matter:\n-------\n%s\n-------\nWe hope to reply shortly.\nBest regards,\n\nDDSM team."%message)
                msg['Subject'] = 'DDSM -- You contacted us!'
                msg['From'] = "yannick.congo@gmail.com"
                msg['To'] = email
                msg['CC'] = "yannick.congo@gmail.com"
                s = smtplib.SMTP('localhost')
                s.sendmail("yannick.congo@gmail.com", email, msg.as_string())
                s.quit()
                return fk.Response('Message sent.', status.HTTP_200_OK)
            except:
                print(str(traceback.print_exc()))
                return fk.redirect('{0}:{1}/error/?code=503'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/version', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_version():
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
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/user/config', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_config(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/config')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/config')
            config_buffer = BytesIO()
            config_content = {'default':{'app':'', 'api':{'host':API_HOST, 'path':'/corr/api/v0.1', 'port':API_PORT, 'key':user_model.api_token}}}
            config_buffer.write(json.dumps(config_content, sort_keys=True, indent=4, separators=(',', ': ')).encode('utf-8'))
            config_buffer.seek(0)
            return fk.send_file(config_buffer, as_attachment=True, attachment_filename='config.json', mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/user/picture', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_picture(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/user/picture')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/user/picture')
            profile = ProfileModel.objects(user=user_model).first()
            if profile == None:
                picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                if picture_buffer == None:
                    return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
            else:
                picture = profile.picture
                if picture == None:
                    picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                    if picture_buffer == None:
                        return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                elif picture.location == 'local' and 'http://' not in picture.storage and 'https://' not in picture.storage:
                    picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                    if picture_buffer == None:
                        picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                        else:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                elif picture.location == 'remote':
                    picture_buffer = storage_manager.web_get_file(picture.storage)
                    if picture_buffer != None:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                        if picture_buffer == None:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                else:
                    if 'http://' in picture.storage or 'https://' in picture.storage:
                        picture.location = 'remote'
                        picture.save()
                        picture_buffer = storage_manager.web_get_file(picture.storage)
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                            if picture_buffer == None:
                                return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                            else:
                                return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                    else:
                        picture.location = 'local'
                        picture.save()
                        picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                        if picture_buffer == None:
                            picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                            if picture_buffer != None:
                                return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                            else:
                                return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/trusted', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_truested():
    logTraffic(CLOUD_URL, endpoint='/private/user/trusted')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            return fk.Response('Unauthorized access.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/trusted')
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            return fk.Response(json.dumps({'version':version, 'group':user_model.group}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/home', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))


@app.route(CLOUD_URL + '/private/user/profile', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_profile():
    logTraffic(CLOUD_URL, endpoint='/private/user/profile')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        user_model.save()
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/profile')
            profile_model = ProfileModel.objects(user=user_model).first()
            if profile_model == None:
                profile_model, created = ProfileModel.objects.get_or_create(user=user_model, fname="None", lname="None", organisation="None", about="None")
                if created:
                    profile_model.created_at=str(datetime.datetime.utcnow())
                    profile_model.save()
            print(fk.request.path)
            return fk.Response(json.dumps({'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'email':user_model.email, 'session':user_model.session, 'api':user_model.api_token, 'max-quota':user_model.max_quota, 'usage':round(100*(user_model.quota/(user_model.max_quota*1024*1024*1024)), 2)}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/user/renew', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def user_renew():
    logTraffic(CLOUD_URL, endpoint='/private/user/renew')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/user/renew')
            print(fk.request.path)
            user_model.retoken()
            return fk.Response(user_model.api_token, status.HTTP_200_OK)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/recover', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def cloud_public_user_recover():
    logTraffic(CLOUD_URL, endpoint='/public/user/recover')
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            try:
                email = data.get("email", "")
                if email == "":
                    return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                else:
                    account = access_manager.reset_password(email)
                    if account != None:
                        return fk.Response('Recovery email sent from stormpath.', status.HTTP_200_OK)
                    else:
                        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            except:
                print(str(traceback.print_exc()))
                return fk.redirect('{0}:{1}/error/?code=503'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/user/picture/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def cloud_public_user_picture(user_id):
    logTraffic(CLOUD_URL, endpoint='/public/user/picture/<user_id>')
    if fk.request.method == 'GET':
        user_model = UserModel.objects.with_id(user_id)
        profile = ProfileModel.objects(user=user_model).first_or_404()
        if profile == None:
            picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
            if picture_buffer == None:
                return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
        else:
            picture = profile.picture
            if picture == None:
                picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                if picture_buffer == None:
                    return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
            elif picture.location == 'local' and 'http://' not in picture.storage and 'https://' not in picture.storage:
                picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                if picture_buffer == None:
                    picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                    if picture_buffer != None:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                    else:
                        return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
            elif picture.location == 'remote':
                picture_buffer = storage_manager.web_get_file(picture.storage)
                if picture_buffer != None:
                    return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                else:
                    picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                    if picture_buffer == None:
                        return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
            else:
                if 'http://' in picture.storage or 'https://' in picture.storage:
                    picture.location = 'remote'
                    picture.save()
                    picture_buffer = storage_manager.web_get_file(picture.storage)
                    if picture_buffer != None:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                        if picture_buffer == None:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                else:
                    picture.location = 'local'
                    picture.save()
                    picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                    if picture_buffer == None:
                        picture_buffer = storage_manager.web_get_file('{0}:{1}/images/picture.png'.format(VIEW_HOST, VIEW_PORT))
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                        else:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))