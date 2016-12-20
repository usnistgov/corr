# from .. import logAccess
from flask.ext.stormpath import StormpathManager
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
from stormpath.error import Error
import flask as fk

import hashlib
import datetime

# No admin access for now.
# Only user access is handled.

class AccessManager:
    def __init__(self, app):
        """Initializes an access manager instance.
        """
        self.config = app.config['ACCOUNT_MANAGEMENT']

        if self.config['type'] == 'stormpath':
            self.manager = StormpathManager(app)
            self.type = 'stormpath'
        elif self.config['type'] == 'api-token':
            self.manager = None
            self.type = 'api-token'
        elif self.config['type'] == 'mongodb':
            self.manager = None
            self.type = 'mongodb'

    def create_account(self, email, password, fname, lname, mname):
        """Create an account.
            Returns:
                Tuple of the account object and a message in case of an error.
        """
        try:
            _account = self.manager.application.accounts.create({
                'email': email,
                'password': password,
                "username" : email,
                "given_name" : fname,
                "middle_name" : mname,
                "surname" : lname,
            })
            return (_account, "")
        except Error as re:
            print('Message: %s' %re.message)
            print('HTTP Status: %s' %str(re.status))
            print('Developer Message: %s' %re.developer_message)
            print('More Information: %s' %re.more_info)
            print('Error Code: %s' %str(re.code))
            print('Message message: %s' %re.message['message'])
            return (None, re.message['message'])

    def register(self, email, password, fname, lname, mname):
        """Registration handler.
            Returns:
                User account registered.
        """
        from corrdb.common.models import UserModel
        account = None
        hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
        if self.type == 'api-token':
            pass
        else:
            if self.type == 'mongodb':
                account = UserModel.objects(email=email).first()
            elif self.type == 'stormpath':
                try:
                    _account = application.authenticate_account(
                        email,
                        password,
                    ).account
                except:
                    _account = None
                if _account != None:
                    account = UserModel.objects(email=email).first()
            if account is None:
                failure = False
                if self.type == 'stormpath':
                    failure = self.create_account(email, password, fname, lname, mname)[0] is None
                if not failure:
                    (account, created) = UserModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), email=email, group='user', api_token=hashlib.sha256(('CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).encode("ascii")).hexdigest())
                if self.type == 'mongodb':
                    account.password = hash_pwd
                    account.save()
        return account


    def login(self, email, password):
        """Account login handler.
            Returns:
                User account instance if successful otherwise None.
        """
        from corrdb.common.models import UserModel
        account = None
        if self.type == 'stormpath':
            try:
                _account = self.manager.application.authenticate_account(email, password).account
                if _account is not None:
                    account = UserModel.objects(email=email).first()
            except Error as re:
                print('Message: %s' %re.message)
                print('HTTP Status: %s' %str(re.status))
                print('Developer Message: %s' %re.developer_message)
                print('More Information: %s' %re.more_info)
                print('Error Code: %s' %str(re.code))
        elif self.type == 'api-token':
            # No login for api-token.
            pass
        elif self.type == 'mongodb':
            hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
            account_1 = UserModel.objects(email=email).first()
            if account_1 != None:
                if account_1.password == None:
                    account_1.password = hash_pwd
                    account_1.save()
                account = account_1
            else:
                account = UserModel.objects(email=email, password=hash_pwd).first()
        return account

    def logout(self, session_token):
        """Session login handler.
        """
        if self.type == 'stormpath':
            pass
        elif self.type == 'api-token':
            # Not logout for api-token.
            pass
        elif self.type == 'mongodb':
            pass

    def unregister(self, session_token):
        """Account unregistration handler.
            Returns:
                None in case of a success. Otherwise return the account object.
        """
        # No unregister yet.
        if self.type == 'stormpath':
            pass
        elif self.type == 'api-token':
            pass
        elif self.type == 'mongodb':
            pass
        return None

    def reset_password(self, email):
        """Password recovery handler.
            Returns:
                User Account in case of a success, otherwise None.
        """
        account = None
        if self.type == 'stormpath':
            try:
                account = self.manager.application.send_password_reset_email(email)
            except Error as re:
                print('Message: %s' %re.message)
                print('HTTP Status: %s' %str(re.status))
                print('Developer Message: %s' %re.developer_message)
                print('More Information: %s' %re.more_info)
                print('Error Code: %s' %str(re.code))
                print('Message message: %s' %re.message['message'])
        elif self.type == 'api-token':
            pass
        elif self.type == 'mongodb':
            pass
        return account

    def change_password(self, user_model, password):
        """Password change handler.
            Returns:
                User Account in case of a success, otherwise None.
        """
        account = None
        hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
        if self.type == 'stormpath':
            accounts = self.manager.application.accounts
            for acc in accounts:
                if acc.email == user_model.email:
                    account = acc
                    break
            if account is not None:
                account.password = password
        elif self.type == 'api-token':
            pass
        elif self.type == 'mongodb':
            account = user_model
            account.password = hash_pwd
        account.save()
        return account

    def accounts(self):
        """Retrieve the registered accounts.
            Returns:
                List of registered users accounts.
        """
        from corrdb.common.models import UserModel
        users = None
        if self.type == 'stormpath':
            users = self.manager.application.accounts
        elif self.type == 'api-token' or self.type == 'mongodb':
            users = UserModel.objects()
        return users

    def check_cloud(self, hash_session):
        """Check that a session is valid.
            Returns:
                Tuple of Validation Boolean and the account instance.
        """
        from corrdb.common.models import UserModel
        account = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if account is None:
            return False, None
        else:
            # print "Connected_at: %s"%str(user_model.connected_at)
            allowance = account.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print("Allowance: {0}".format(allowance))
            # print "Connected_at: %s"%str(user_model.connected_at)
            if allowance == hash_session:
                return True, account
            else:
                return False, account
            
    def check_api(self, token):
        from corrdb.common.models import UserModel
        """Get the user object instance from its api token.
            Returns:
                The user object instance.
        """
        print([user.extended() for user in UserModel.objects()])
        return UserModel.objects(api_token=token).first()

    def check_app(self, token):
        from corrdb.common.models import ApplicationModel
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


