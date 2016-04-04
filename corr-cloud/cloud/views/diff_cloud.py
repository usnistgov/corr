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
from cloud import app, stormpath_manager, crossdomain, CLOUD_URL
import datetime
import json
import traceback
import smtplib
from email.mime.text import MIMEText
import mimetypes

# CLOUD_VERSION = 1
# CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

@app.route(CLOUD_URL + '/<hash_session>/diff/create', methods=['POST'])
@crossdomain(origin='*')
def diff_create(hash_session, diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/diff/create")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=edit_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
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
                        return fk.redirect('http://0.0.0.0:5000/error-400/')
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
                                    return fk.redirect('http://0.0.0.0:5000/error-409/')
                            else:
                                return fk.redirect('http://0.0.0.0:5000/error-400/')
                        except:
                            return fk.redirect('http://0.0.0.0:5000/error-400/')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-415/')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-404/')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/diff/remove/<diff_id>', methods=['DELETE'])
@crossdomain(origin='*')
def diff_remove(hash_session, diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/diff/remove/<diff_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'DELETE':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print str(traceback.print_exc())
            if diff is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if diff.sender == current_user or diff.targeted == current_user:
                    diff.delete()
                    return fk.Response('Diff request removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_denied')
    else:
       return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/diff/comment/<diff_id>', methods=['POST'])
@crossdomain(origin='*')
def diff_comment(hash_session, diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/diff/comment/<diff_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print str(traceback.print_exc())
            if diff is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                # if diff.project.owner == current_user: # Allow any user to be able to comment on a diff.
                # Because based on a discussion a user that can't see the two records can ask
                # the scientists involved to make one or both public so that he can access them.
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    comment = data.get("comment", {}) #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}
                    if len(comment) != 0:
                        diff.comments.append(comment)
                        diff.save()
                        return fk.Response('Diff comment posted', status.HTTP_200_OK)
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-400/')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-415/')
                # else:
                #     return fk.redirect('http://0.0.0.0:5000/error-401/?action=comment_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=comment_denied')
    else:
       return fk.redirect('http://0.0.0.0:5000/error-405/')  

@app.route(CLOUD_URL + '/<hash_session>/diff/view/<diff_id>', methods=['GET'])
@crossdomain(origin='*')
def diff_view(hash_session, diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/diff/view/<diff_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                diff = DiffModel.objects.with_id(diff_id)
            except:
                print str(traceback.print_exc())
            if diff is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                # Let's allow anybody to be able to see a diff from a search or other.
                # if diff.creator == current_user or diff.target == current_user:
                return fk.Response(diff.to_json(), mimetype='application/json')
                # else:
                #     return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')      

@app.route(CLOUD_URL + '/<hash_session>/diff/edit/<diff_id>', methods=['POST'])
@crossdomain(origin='*')
def diff_edit(hash_session, diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/diff/edit/<diff_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=edit_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                try:
                    diff = DiffModel.objects.with_id(diff_id)
                except:
                    print str(traceback.print_exc())
                if diff is None:
                    return fk.redirect('http://0.0.0.0:5000/error-204/')
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
                                print str(traceback.print_exc())
                                return fk.redirect('http://0.0.0.0:5000/error-400/')
                        elif diff.target == current_user:
                            try:
                                status = data.get("status", diff.status)
                                diff.status = status
                                diff.save()
                                return fk.Response('Diff edited', status.HTTP_200_OK)
                            except:
                                print str(traceback.print_exc())
                                return fk.redirect('http://0.0.0.0:5000/error-400/')
                        else:
                            return fk.redirect('http://0.0.0.0:5000/error-401/?action=edit_failed')
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-415/')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-404/')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/diff/view/<diff_id>', methods=['GET'])
@crossdomain(origin='*')
def public_diff_view(diff_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/diff/view/<diff_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        try:
            diff = DiffModel.objects.with_id(diff_id)
        except:
            print str(traceback.print_exc())
        if diff is None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
        else:
            #Full disclosure on diffs.
            #It is one of the means of communication in the platform also.
            # if not diff.source.private and not diff.destination.private:
            return fk.Response(diff.to_json(), mimetype='application/json')
            # else:
            #     return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')      