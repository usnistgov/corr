from corrdb.common.models import UserModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
from flask.ext.api import status
import flask as fk
from cloud import app, stormpath_manager, crossdomain, upload_picture, CLOUD_URL
import datetime
import json
import traceback
import smtplib
from email.mime.text import MIMEText
from hurry.filesize import size
import hashlib

# CLOUD_VERSION = 1
# CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

#Allow admins to do everything they want. Developers will be able to do specific things with the API
#that normal users can't

@app.route(CLOUD_URL + '/public/user/register', methods=['POST'])
@crossdomain(origin='*')
def user_register():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/register")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        if fk.request.data:
            data = json.loads(fk.request.data)
            application = stormpath_manager.application
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
                return fk.make_response("The email field cannot be empty.", status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    _account = None
                    user_model = None
                    try:
                        _account = application.authenticate_account(
                            email,
                            password,
                        ).account
                    except:
                        _account = None
                    if _account != None:
                        user_model = UserModel.objects(email=email).first()

                    # _user = application.accounts.create({
                    #     'email': email,
                    #     'password': password
                    #     # "username" : username,
                    #     # "given_name" : "Empty",
                    #     # "middle_name" : "Empty",
                    #     # "surname" : "Empty"
                    # })
                    if user_model == None:
                        print "User Model does not exist."
                        while True:
                            # Many trials because of API key generation failures some times.
                            try:
                                if group != "admin" and email != "root@corr.gov":
                                    if _account == None:
                                        try:
                                            _account = application.accounts.create({
                                                'email': email,
                                                'password': password,
                                                "username" : email,
                                                "given_name" : "undefined",
                                                "middle_name" : "undefined",
                                                "surname" : "undefined",
                                            })
                                        except:
                                            print str(traceback.print_exc())
                                            _account = None
                                    if _account != None:
                                        print "created!!!"
                                        (user_model, created) = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, group=group, api_token=hashlib.sha256(b'CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).hexdigest())
                                    else:
                                        print "Unauthorized admin account creation. Could not create user!"
                                        return fk.make_response('Unauthorized admin account creation. Could not create user!', status.HTTP_401_UNAUTHORIZED)
                                else:
                                # # Many trials because of API key generation failures some times.
                                # (user_model, created) = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, api_token=hashlib.sha256(b'DDSMSession_%s_%s'%(email, str(datetime.datetime.utcnow()))).hexdigest())
                                    if email == "root@corr.gov":
                                        if _account == None:
                                            try:
                                                _account = application.accounts.create({
                                                    'email': email,
                                                    'password': password,
                                                    "username" : email,
                                                    "given_name" : "undefined",
                                                    "middle_name" : "undefined",
                                                    "surname" : "CoRR"
                                                })
                                            except:
                                                print str(traceback.print_exc())
                                                _account = None
                                        if _account != None:
                                            (user_model, created) = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, group="admin", api_token=hashlib.sha256(b'CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).hexdigest())
                                        else:
                                            print "You are forbidden to do this."
                                            return fk.make_response('You are forbidden to do this.', status.HTTP_401_UNAUTHORIZED)
                                    else:
                                        if len(admin) != 0:
                                            try:
                                                _admin = application.authenticate_account(
                                                    admin["email"],
                                                    admin["password"],
                                                ).account
                                            except:
                                                _admin = None
                                            admin_account = UserModel.objects(email=email).first()
                                            if admin_account != None and _admin != None:
                                                if account.group == "admin":
                                                    if _account == None:
                                                        try:
                                                            _account = application.accounts.create({
                                                                'email': email,
                                                                'password': password,
                                                                "username" : email,
                                                                "given_name" : "undefined",
                                                                "middle_name" : "undefined",
                                                                "surname" : "undefined"
                                                            })
                                                        except:
                                                            print str(traceback.print_exc())
                                                    if _account != None:
                                                        (user_model, created) = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, group=group, api_token=hashlib.sha256(b'CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).hexdigest())
                                                        # admin_model = UserModel.objects(email=admin["email"]).first()
                                                        # if admin_model.group == "admin":
                                                        #     user_model.group = "admin"
                                                        #     user_model.save()
                                                    else:
                                                        print "Unauthorized admin account creation. Could not create user!"
                                                        return fk.make_response('Unauthorized admin account creation. Could not create user!', status.HTTP_401_UNAUTHORIZED)
                                                else:
                                                    print "Unauthorized admin account creation. Referee is not an admin."
                                                    return fk.make_response('Unauthorized admin account creation. Referee is not an admin.', status.HTTP_401_UNAUTHORIZED)
                                            else:
                                                print "Unauthorized admin account creation. Unknown admin referee."
                                                return fk.make_response('Unauthorized admin account creation. Unknown admin referee.', status.HTTP_401_UNAUTHORIZED)
                                        else:
                                            print "Unauthorized admin account creation. No provided admin referee."
                                            return fk.make_response('Unauthorized admin account creation. No provided admin referee.', status.HTTP_401_UNAUTHORIZED)
                                if created:
                                    (profile_model, created) = ProfileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), user=user_model, fname=fname, lname=lname, organisation=organisation, about=about)
                                break
                            except:
                                print str(traceback.print_exc())
                    else:
                        print "This user already exists."
                        return fk.make_response('This user already exists.', status.HTTP_401_UNAUTHORIZED)

                    print "Token %s"%user_model.api_token
                    print fk.request.headers.get('User-Agent')
                    print fk.request.remote_addr
                    # print "Connected_at: %s"%str(user_model.connected_at)
                    # user_model.connected_at = datetime.datetime.utcnow()
                    # user_model.save()
                    user_model.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    user_model.retoken()
                    # print "Connected_at: %s"%str(user_model.connected_at)
                    print "Session: %s"%user_model.session

                    today = datetime.date.today()
                    (stat, created) = StatModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), interval="%s_1-%s_12"%(today.year, today.year), category="user", periode="yearly")
                    if not created:
                        stat.traffic += 1 
                        stat.save()

                    return fk.Response(json.dumps({'session':user_model.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                    # return fk.redirect('http://0.0.0.0:5000/%s'%user_model.session)
                except:
                    print str(traceback.print_exc())
                    print "This user already exists."
                    return fk.make_response('This user already exists.', status.HTTP_401_UNAUTHORIZED)
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/password/reset', methods=['POST'])
@crossdomain(origin='*')
def user_password_reset():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/password/reset")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        print "Request: %s"%str(fk.request.data)
        if fk.request.data:
            data = json.loads(fk.request.data)
            application = stormpath_manager.application
            email = data.get('email', '')
            account = application.send_password_reset_email(email)
            if account != None:
                return fk.Response('An email has been sent to renew your password', status.HTTP_200_OK)
            else:
                return fk.make_response('Password reset failed.', status.HTTP_401_UNAUTHORIZED)
                    
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/password/renew', methods=['POST'])
@crossdomain(origin='*')
def user_password_renew():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/password/renew")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        print "Request: %s"%str(fk.request.data)
        if fk.request.data:
            data = json.loads(fk.request.data)
            application = stormpath_manager.application
            token = data.get('token', '')
            password = data.get('password','')
            account = application.verify_password_reset_token(token)
            if account != None:
                account.password = password
                account.save()
                return fk.redirect('http://0.0.0.0:5000')
            else:
                return fk.make_response('Password renew failed.', status.HTTP_401_UNAUTHORIZED)
                    
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/user/password/change', methods=['POST'])
@crossdomain(origin='*')
def user_password_change():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/password/change")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.redirect('http://0.0.0.0:5000/?action=change_denied')
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                application = stormpath_manager.application
                accounts = application.accounts
                account = None
                for acc in accounts:
                    if acc.email == user_model.email:
                        account = acc
                        break
                if account != None:
                    if fk.request.data:
                        data = json.loads(fk.request.data)
                        password = data.get('password', '')
                        account.password = password
                        account.save()
                        return fk.Response('Passoword changed', status.HTTP_200_OK)
                    else:
                        return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
                else:
                    return fk.make_response('Password change failed.', status.HTTP_401_UNAUTHORIZED)
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=change_failed')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/login', methods=['POST'])
@crossdomain(origin='*')
def user_login():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/login")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        print "Request: %s"%str(fk.request.data)
        if fk.request.data:
            data = json.loads(fk.request.data)
            application = stormpath_manager.application
            email = data.get('email', '').lower()
            password = data.get('password', '')
            if email == '' or '@' not in email:
                return fk.make_response("The email field cannot be empty.", status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    try:
                        _user = application.authenticate_account(
                            email,
                            password,
                        ).account
                    except:
                        _user = None
                    account = UserModel.objects(email=email).first()
                    if account == None and _user != None:
                        # Sync with stormpath here... :-)
                        # account, created = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, api_token=hashlib.sha256(b'DDSMSession_%s_%s'%(email, str(datetime.datetime.utcnow()))).hexdigest())
                        # if created:
                        #     (profile_model, created) = ProfileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), user=account, fname="None", lname="None", organisation="None", about="None")
                        # We do not allow this anymore. Registration handles this. Yet the account type has to be provided
                        # Because we have to make a difference between admin, developer and user later.
                        return fk.make_response('Login failed.', status.HTTP_401_UNAUTHORIZED)
                    if account != None and _user == None:
                        try:
                            _account = application.accounts.create({
                                'email': email,
                                'password': password,
                                "username" : email,
                                "given_name" : "undefined",
                                "middle_name" : "undefined",
                                "surname" : "undefined"
                            })
                        except:
                            _account = None
                        if _account == None:
                            print str(traceback.print_exc())
                            return fk.make_response('Login failed.', status.HTTP_401_UNAUTHORIZED)
                    print "Token %s"%account.api_token
                    print fk.request.headers.get('User-Agent')
                    print fk.request.remote_addr
                    # print "Connected at %s"%str(account.connected_at)
                    # account.connected_at = datetime.datetime.utcnow()
                    # account.save()
                    account.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    # print "Session: %s"%account.session
                    return fk.Response(json.dumps({'session':account.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                    # return fk.redirect('http://0.0.0.0:5000/?session=%s'%account.session)
                    # return fk.redirect('http://0.0.0.0:5200%s/%s/user/sync'%(CLOUD_URL, account.session))
                except:
                    print str(traceback.print_exc())
                    return fk.make_response('Login failed.', status.HTTP_401_UNAUTHORIZED)
                    
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/user/sync', methods=['GET'])
@crossdomain(origin='*')
def user_sync(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/sync/<hash_session>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.make_response('Login failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            user_model.sess_sync("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            return fk.Response(json.dumps({'session':user_model.session}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/user/logout', methods=['GET'])
@crossdomain(origin='*')
def user_logout(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/logout/<hash_session>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.redirect('http://0.0.0.0:5000/?action=logout_denied')
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                # user_model.connected_at = datetime.datetime.utcnow()
                # user_model.save()
                user_model.renew("%sLogout"%(fk.request.headers.get('User-Agent')))
                # return fk.redirect('http://0.0.0.0:5000/?action=logout_success')
                return fk.Response('Logout succeed', status.HTTP_200_OK)
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=logout_failed')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/unregister/', methods=['GET'])
@crossdomain(origin='*')
def user_unregister(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/unregister/<hash_session>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        if user_model is None:
            return fk.redirect('http://0.0.0.0:5000/?action=unregister_denied')
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                return fk.make_response('Currently not implemented. Try later.', status.HTTP_501_NOT_IMPLEMENTED)
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=unregister_failed')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/dashboard', methods=['GET'])
@crossdomain(origin='*')
def user_dashboard(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/dashboard/<hash_session>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.redirect('http://0.0.0.0:5000/?action=logout_denied')
        else:
            profile_model = ProfileModel.objects(user=user_model).first()
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                dashboard = {}
                projects = ProjectModel.objects(owner=user_model)
                if profile_model is not None:
                    dashboard["profile"] = {'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'picture':profile_model.picture}
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
                return fk.redirect('http://0.0.0.0:5000/?action=dashboard_failed')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/update', methods=['POST'])
@crossdomain(origin='*')
def user_update(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/update/<hash_session>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
    user_model = UserModel.objects(session=hash_session).first()
    if user_model is None:
        return fk.redirect('http://0.0.0.0:5000/?action=update_denied')
    else:    
        if fk.request.method == 'POST':
            if fk.request.data:
                data = json.loads(fk.request.data)
                application = stormpath_manager.application()
                # user_model = UserModel.objects(session=hash_session).first()
                print fk.request.path
                # if user_model is None:
                #     return fk.redirect('http://0.0.0.0:5000/?action=update_denied')
                # else:
                # print "Connected_at: %s"%str(user_model.connected_at)
                allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                print "Allowance: "+allowance
                # print "Connected_at: %s"%str(user_model.connected_at)
                if allowance == hash_session:
                    #Update stormpath user if password is affected
                    #Update local profile data and picture if other data are affected.
                    # return fk.redirect('http://0.0.0.0:5000/?action=update_success')
                    profile_model = ProfileModel.object(user=user_model).first_or_404()
                    fname = data.get("fname", profile_model.fname)
                    lname = data.get("fname", profile_model.lname)
                    password = data.get("password", "")
                    organisation = data.get("organisation", profile_model.organisation)
                    about = data.get("about", profile_model.about)
                    picture_link = data.get("picture", "")
                    picture = profile_model.picture
                    if picture_link != "":
                        picture['location'] = picture_link

                    profile_model.fname = fname
                    profile_model.lname = lname
                    profile_model.organisation = organisation
                    profile_model.about = about
                    profile_model.picture = picture

                    profile_model.save()

                    if password != "":
                        application = stormpath_manager.application
                        accounts = application.accounts
                        account = None
                        for acc in accounts:
                            if acc.email == user_model.email:
                                account = acc
                                break
                        if account != None:
                            account.password = password
                            account.save()
                    return fk.Response('Account update succeed', status.HTTP_200_OK)
                else:
                    return fk.make_response('Account update failed.', status.HTTP_401_UNAUTHORIZED)
                    # return fk.redirect('http://0.0.0.0:5000/?action=update_failed')
            if fk.request.files:
                if fk.request.files['picture']:
                    picture_obj = fk.request.files['picture']
                    try: 
                        picture_link = str(user_model.id)+"."+picture_obj.filename.split('.')[-1]
                        profile_model = ProfileModel.object(user=user_model).first_or_404()
                        uploaded = upload_picture(user_model, picture_obj)
                        if uploaded:
                            profile_model.picture['scope'] = 'local'
                            profile_model.picture['location'] = picture_link
                            profile_model.save()
                    except Exception, e:
                        return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
            else:
                return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

# Figure this out when all the updates are done.
@app.route(CLOUD_URL + '/public/user/contactus', methods=['POST'])
@crossdomain(origin='*')
def user_contactus(): #Setup and start smtp server on the instance
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/contactus")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
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
                print str(traceback.print_exc())
                return fk.make_response("Could not send the email.", status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/user/picture', methods=['GET'])
@crossdomain(origin='*')
def user_picture(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/picture")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.make_response('Picture get failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                profile_model = ProfileModel.object(user=user_model).first_or_404()
                if profile_model.picture['scope'] == 'remote':
                    return fk.redirect(profile_model.picture['location'])
                elif profile_model.picture['scope'] == 'local':
                    if profile_model.picture['location']:
                        #Refuse images that are more than 5Mb
                        picture = load_picture(profile_model)
                        print picture[1]
                        return fk.send_file(
                            picture[0],
                            mimetypes.guess_type(picture[1])[0],
                            as_attachment=True,
                            attachment_filename=profile_model.picture['location'],
                        )
                    else:
                        print "Failed because of picture location not found."
                        return fk.make_response('Empty location. Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
            else:
                return fk.make_response('Picture get failed.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/trusted', methods=['GET'])
@crossdomain(origin='*')
def user_truested(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/trusted")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.make_response('Trusting failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            if allowance == hash_session:
                return fk.Response('Trusting succeed', status.HTTP_200_OK)
            else:
                return fk.make_response('Trusting failed.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/home', methods=['GET'])
@crossdomain(origin='*')
def user_home():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/home")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        users = UserModel.objects()
        projects = ProjectModel.objects()
        records = RecordModel.objects()
        environments = EnvironmentModel.objects()
        print fk.request.path

        users_stat = {"number":len(users)}
        users_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="user")]

        projects_stat = {"number":len(projects)}
        projects_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="project")]

        storage_stat = {}
        storage_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="storage")]
        amount = 0
        for user in users:
            try:
                amount += user.quota
            except:
                amount += 0

        storage_stat["size"] = size(amount)

        records_stat = {"number":len(records)}
        records_stat["history"] = [json.loads(stat.to_json()) for stat in StatModel.objects(category="record")]

        return fk.Response(json.dumps({'users':users_stat, 'projects':projects_stat, 'records':records_stat, 'storage':storage_stat}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/profile', methods=['GET'])
@crossdomain(origin='*')
def user_profile(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/profile")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        profile_model, created = ProfileModel.objects.get_or_create(user=user_model, fname="None", lname="None", organisation="None", about="None")
        if created:
            profile_model.created_at=str(datetime.datetime.utcnow())
            profile_model.save()
        print fk.request.path
        if user_model is None:
            return fk.make_response('profile get failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            if allowance == hash_session:
                return fk.Response(json.dumps({'fname':profile_model.fname, 'lname':profile_model.lname, 'organisation':profile_model.organisation, 'about':profile_model.about, 'picture':profile_model.picture, 'email':user_model.email, 'session':user_model.session, 'api':user_model.api_token}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.make_response('profile get failed.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/<hash_session>/user/renew', methods=['GET'])
@crossdomain(origin='*')
def user_renew(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/user/renew")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if user_model is None:
            return fk.make_response('Renew token failed.', status.HTTP_401_UNAUTHORIZED)
        else:
            allowance = user_model.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            if allowance == hash_session:
                user_model.retoken()
                return fk.Response(json.dumps({'api':user_model.api_token}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.make_response('Renew token failed.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/user/picture/<user_id>', methods=['GET'])
@crossdomain(origin='*')
def public_user_picture(user_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/user/picture/<user_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.object.with_id(user_id)
        if user_model == None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
        else:
            profile_model = ProfileModel.object(user=user_model).first_or_404()
            if profile_model.picture['scope'] == 'remote':
                return fk.redirect(profile_model.picture['location'])
            elif profile_model.picture['scope'] == 'local':
                if profile_model.picture['location']:
                    picture = load_picture(profile_model)
                    print picture[1]
                    return fk.send_file(
                        picture[0],
                        mimetypes.guess_type(picture[1])[0],
                        as_attachment=True,
                        attachment_filename=profile_model.picture['location'],
                    )
                else:
                    print "Failed because of picture location not found."
                    return fk.make_response('Empty location. Nothing to pull from here!', status.HTTP_204_NO_CONTENT)
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)


# Picture upload
#    Update the picture field to: local and the name of the file.

#Picture get link to retrieve file