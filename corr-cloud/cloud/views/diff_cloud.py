from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import DiffModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
from flask.ext.api import status
import flask as fk
from cloud import app, cloud_response, storage_manager, access_manager, CLOUD_URL, VIEW_HOST, VIEW_PORT, VIEW_MODE
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
import mimetypes

# CLOUD_VERSION = 1
# CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

@app.route(CLOUD_URL + '/private/<hash_session>/diff/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diff_create(hash_session, diff_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/diff/create')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/diff/create')
            if fk.request.data:
                data = json.loads(fk.request.data)
                targeted_id = data.get("targeted", "")
                record_from_id = data.get("record_from", "")
                record_to_id = data.get("record_to", "")
                diffentiation = data.get("diff", {})
                proposition = data.get("proposition", "undefined")
                status = data.get("status", "undefined")
                comments = data.get("comments", [])

                if targeted_id == "" or record_from_id == "" or record_to_id == "":
                    return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                else:
                    try:
                        targeted = UserModel.objects.with_id(targeted_id)
                        record_from = RecordModel.objects.with_id(record_from_id)
                        record_to = RecordModel.objects.with_id(record_to_id)
                        if targeted != None and record_to != None and record_from != None:
                            (diff, created) = DiffModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), sender=current_user, targeted=targeted, record_from=record_from, record_to=record_to)
                            if created:
                                diff.proposition = proposition
                                diff.status = status
                                diff.comments = comments
                                diff.save()
                                return fk.Response('Diff created', status.HTTP_200_OK)
                            else:
                                return fk.redirect('{0}:{1}/error/?code=409'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    except:
                        return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/diff/remove/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diff_remove(hash_session, diff_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/diff/remove/<diff_id>')
    if fk.request.method == 'DELETE':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/diff/remove/<diff_id>')
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print(str(traceback.print_exc()))
            if diff is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if diff.sender == current_user or diff.targeted == current_user:
                    diff.delete()
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/diff/comment/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diff_comment(hash_session, diff_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/diff/comment/<diff_id>')
    if fk.request.method == 'POST':
        caccess_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/diff/comment/<diff_id>')
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print(str(traceback.print_exc()))
            if diff is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    comment = data.get("comment", {})
                    if len(comment) != 0:
                        diff.comments.append(comment)
                        diff.save()
                        return fk.Response('Diff comment posted', status.HTTP_200_OK)
                    else:
                        return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

@app.route(CLOUD_URL + '/private/<hash_session>/diff/view/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diff_view(hash_session, diff_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/diff/view/<diff_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/diff/view/<diff_id>')
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print(str(traceback.print_exc()))
            if diff is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(diff.to_json(), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))      

@app.route(CLOUD_URL + '/private/<hash_session>/diff/edit/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diff_edit(hash_session, diff_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/diff/edit/<diff_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/diff/edit/<diff_id>')
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print(str(traceback.print_exc()))
            if diff is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    if diff.sender == current_user:
                        try:
                            diffentiation = data.get("diff", diff.diff)
                            proposition = data.get("proposition", diff.proposition)
                            diff.diff = diffentiation
                            diff.proposition = proposition
                            if diff.status == "agreed" or diff.status == "denied":
                                diff.status = "altered"
                            diff.save()
                            return fk.Response('Diff edited', status.HTTP_200_OK)
                        except:
                            print(str(traceback.print_exc()))
                            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    elif diff.target == current_user:
                        try:
                            status = data.get("status", diff.status)
                            diff.status = status
                            diff.save()
                            return fk.Response('Diff edited', status.HTTP_200_OK)
                        except:
                            print(str(traceback.print_exc()))
                            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/diff/view/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_diff_view(diff_id):
    logTraffic(CLOUD_URL, endpoint='/public/diff/view/<diff_id>')
    if fk.request.method == 'GET':
        try:
            logAccess(CLOUD_URL, 'cloud', '/public/diff/view/<diff_id>')
            diff = DiffModel.objects.with_id(diff_id)
        except:
            print(str(traceback.print_exc()))
        if diff is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.Response(diff.to_json(), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))      