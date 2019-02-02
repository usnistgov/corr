"""Manage access control.
"""
# from .. import logAccess
# from flask.ext.stormpath import StormpathManager
# from flask.ext.stormpath import user
# from flask.ext.stormpath import login_required
# from stormpath.error import Error
import flask as fk

import hashlib
import datetime

import re

def get_or_create(document=None, **kwargs):
    return (document(**kwargs).save(), True)

# No admin access for now.
# Only user access is handled.

class AccessManager:
    def __init__(self, app):
        """Initializes an access manager instance.
        """
        self.config = app.config['ACCOUNT_MANAGEMENT']
        self.secur = app.config['SECURITY_MANAGEMENT']['account']

        # if self.config['type'] == 'stormpath':
        #     self.manager = StormpathManager(app)
        #     self.type = 'stormpath'
        # el
        if self.config['type'] == 'api-token':
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
            print('Message message: %s' %re.message)
            return (None, re.message)

    def register(self, email, password, fname, lname, mname):
        """Registration handler.

        Returns:
          User account registered.
        """
        from corrdb.common.models import UserModel
        account = None
        _account = None
        check_password = self.password_check(password)
        if not check_password['password_ok']:
            message = ["Password rules vialation:"]
            if check_password['length_error']:
                message.append("Must be at least 8 characters.")
            if check_password['digit_error']:
                message.append("Must contain at least one digit.")
            if check_password['uppercase_error']:
                message.append("Must contain at least one upper case character.")
            if check_password['lowercase_error']:
                message.append("Must contain at least one lower case character.")
            if check_password['symbol_error']:
                message.append("Must contain at least one special character.")
            return False, message
        hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
        if self.type == 'api-token':
            pass
        else:
            if self.type == 'mongodb':
                account = UserModel.objects(email=email).first()
            elif self.type == 'stormpath':
                try:
                    _account = self.manager.application.search(email).first()
                except:
                    _account = None
                if _account != None:
                    account = UserModel.objects(email=email).first()
            if account is None:
                if self.type == 'stormpath':
                    account = UserModel.objects(email=email).first()
                    if account is None:
                        (account, created) = get_or_create(document=UserModel, created_at=str(datetime.datetime.utcnow()), email=email, group='user', api_token=hashlib.sha256(('CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).encode("ascii")).hexdigest())
                    if _account is None:
                        failure = self.create_account(email, password, fname, lname, mname)[0] is None
                        if failure:
                            account.password = hash_pwd
                            account.save()
                if self.type == 'mongodb':
                    account = UserModel.objects(email=email).first()
                    if account is None:
                        (account, created) = get_or_create(document=UserModel, created_at=str(datetime.datetime.utcnow()), email=email, group='user', api_token=hashlib.sha256(('CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).encode("ascii")).hexdigest())
                    account.password = hash_pwd
                    account.save()
                account.save()
                return True, account
            else:
                return False, account

        return False, account

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
                if _account:
                    account = UserModel.objects(email=email).first()
                else:
                    _account = self.manager.application.search(email).first()
                    if _account is None:
                        failure = self.create_account(email, password, "FirstName", "LastName", "")[0] is None
                        if failure:
                            hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
                            account = UserModel.objects(email=email, password=hash_pwd).first()
                        else:
                            account = UserModel.objects(email=email).first()
                    else:
                        account = None
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
            if account_1:
                if account_1.password is None:
                    account_1.password = hash_pwd
                    account_1.save()
                    account = account_1
                else:
                    account = UserModel.objects(email=email, password=hash_pwd).first()
            else:
                # (account, created) = get_or_create(document=UserModel, created_at=str(datetime.datetime.utcnow()), email=email, group='user', api_token=hashlib.sha256(('CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).encode("ascii")).hexdigest())
                # account.password = hash_pwd
                # account.save()
                account = None
        if account and account.group == "unknown":
            account.group = "user"
            account.save()
        if account:
            account.connected_at = str(datetime.datetime.utcnow())
            if account.auth in ["wrong1", "wrong2", "wrong3"]:
                account.auth = "approved"
            account.save()
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
        check_password = self.password_check(password)
        if not check_password['password_ok']:
            message = ["Password rules vialation:"]
            if check_password['length_error']:
                message.append("Must be at least 8 characters.")
            if check_password['digit_error']:
                message.append("Must contain at least one digit.")
            if check_password['uppercase_error']:
                message.append("Must contain at least one upper case character.")
            if check_password['lowercase_error']:
                message.append("Must contain at least one lower case character.")
            if check_password['symbol_error']:
                message.append("Must contain at least one special character.")
            return None, message
        hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
        if self.type == 'stormpath':
            accounts = self.manager.application.accounts
            for acc in accounts:
                if acc.email == user_model.email:
                    account = acc
                    break
            if account:
                account.password = password
        elif self.type == 'api-token':
            pass
        elif self.type == 'mongodb':
            account = user_model
            account.password = hash_pwd
        if account:
            account.save()
        return account, []

    def password_check(self, password):
        """Verify the strength of 'password'.
        A password is considered strong if:
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more

        Returns:
          a dict indicating the wrong criteria.
        """

        # calculating the length
        length_error = len(password) < 8

        # searching for digits
        digit_error = re.search(r"\d", password) is None

        # searching for uppercase
        uppercase_error = re.search(r"[A-Z]", password) is None

        # searching for lowercase
        lowercase_error = re.search(r"[a-z]", password) is None

        # searching for symbols
        # ]\;',./!@#$%^&*()_+-=
        symbol_error = not any(i in "]\;',./!@#$%^&*()_+-=]" for i in password)

        # overall result
        password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

        return {
            'password_ok' : password_ok,
            'length_error' : length_error,
            'digit_error' : digit_error,
            'uppercase_error' : uppercase_error,
            'lowercase_error' : lowercase_error,
            'symbol_error' : symbol_error,
        }

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
            users = UserModel.objects
        return users

    def check_cloud(self, hash_session, acc_sec=False, cnt_sec=False):
        """Check that a session is valid.

        Returns:
          Tuple of Validation Boolean and the account instance.
        """
        from corrdb.common.models import UserModel
        if hash_session == "logout":
            account = None
        else:
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
                if acc_sec and account.extend.get('access', 'verified') != 'verified':
                    return False, account
                else:
                    return True, account
            else:
                return False, account

    def check_api(self, token, acc_sec=False, cnt_sec=False):
        from corrdb.common.models import UserModel
        """Get the user object instance from its api token.

        Returns:
          The user object instance.
        """
        print([user.extended() for user in UserModel.objects])
        account = UserModel.objects(api_token=token).first()
        if account.extend.get('access', 'verified') != 'verified':
            return None
        else:
            return account

    def check_app(self, token, acc_sec=False, cnt_sec=False):
        from corrdb.common.models import ApplicationModel
        """Get the application object instance from its api token.

        Returns:
          The application object instance.
        """
        if token == "no-app":
            return None
        else:
            for application in ApplicationModel.objects:
                print("{0} -- {1}.".format(str(application.developer.id), application.name))
            application = ApplicationModel.objects(app_token=token).first()
            developer = application.developer
            if developer.extend.get('access', 'verified') != 'verified':
                return None
            else:
                return application
