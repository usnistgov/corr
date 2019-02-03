from corrdb.common.models import UserModel
from corrdb.common.models import ProfileModel
from corrdb.common import get_or_create
import hashlib
import datetime
import simplejson as json
import os
import re

def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        12 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 12

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

    return password_ok

def check_admin(email=None):
    """
    Check that admin account does not already exist
    Returns boolean to indicate if it is true or false
    """
    if email:
        account = UserModel.objects(email=email).first()
        if account and account.group == "admin":
            return True
        else:
            admin = UserModel.objects(group="admin").first()
            if admin:
                # We only want to allow the creation of one admin
                # Only the original admin can add new admins.
                # Once created another admin cannot be added this way
                # for security purposes.
                print("Admins already exist!")
                return True
            else:
                return False
    else:
        # Fake admin existence to avoid attempt to create admin with void email.
        return True

def create_admin(email, password, fname, lname):
    """
    Creates the first admin user
    Returns boolean to indicate if the account was created or not
    """
    if not password_check(password):
        return False
    else:
        hash_pwd = hashlib.sha256(('CoRRPassword_%s'%password).encode("ascii")).hexdigest()
        (account, created) = get_or_create(document=UserModel, created_at=str(datetime.datetime.utcnow()), email=email, group='admin', api_token=hashlib.sha256(('CoRRToken_%s_%s'%(email, str(datetime.datetime.utcnow()))).encode("ascii")).hexdigest())
        if created:
            account.password = hash_pwd
            account.save()
            (profile_model, created) = get_or_create(document=ProfileModel, created_at=str(datetime.datetime.utcnow()), user=account, fname=fname, lname=lname)
            if created:
                return True
            else:
                return False
        else:
            return False

content = {}
# Loading admin user account information.
# The instance admin should make sure to securely backup this file.
if os.path.isfile("/home/corradmin/credentials/tmp_admin.json"):
    with open("/home/corradmin/credentials/tmp_admin.json", "r") as admin_stuff:
        content = json.loads(admin_stuff.read())
    try:
        if not check_admin(content['admin-email']):
            print("Creating an admin account!")
            create_admin(content['admin-email'], content['admin-password'], content['admin-fname'], content['admin-lname'])
    except:
        print("An error occured!")
else:
    with open("/tmp/tmp_admin.json", "r") as admin_stuff:
        content = json.loads(admin_stuff.read())
    try:
        if not check_admin(content['admin-email']):
            print("Creating an admin account!")
            create_admin(content['admin-email'], content['admin-password'], content['admin-fname'], content['admin-lname'])
    except:
        print("An error occured!")
