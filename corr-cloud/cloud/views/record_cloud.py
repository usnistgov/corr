from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
from flask.ext.api import status
import flask as fk
from cloud import app, stormpath_manager, load_bundle, crossdomain, delete_record_files, delete_record_file, CLOUD_URL
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


#I think i will not allow upload of bundles from the web interface because i will loose environment consistency on the fact that
#records are attached to the same bundle when nothing is changed in the code.
#For experimental this still stands and is related to the way that the experiment profile is writtern
#meaning having the same actions and same sequence and same calls. In this case only one profile will
# be linked to many experiment untill a change happens in that sense.

@app.route(CLOUD_URL + '/<hash_session>/record/remove/<record_id>', methods=['DELETE'])
@crossdomain(origin='*')
def record_remove(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/remove/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'DELETE':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if record.project.owner == current_user:
                    delete_record_files(record)
                    record.delete()
                    return fk.Response('Record removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_denied')
    else:
       return fk.redirect('http://0.0.0.0:5000/error-405/') 

@app.route(CLOUD_URL + '/<hash_session>/record/comment/<record_id>', methods=['POST'])
@crossdomain(origin='*')
def record_comment(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/comment/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if record.project.owner == current_user:
                    if fk.request.data:
                        data = json.loads(fk.request.data)
                        comment = data.get("comment", {}) #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}
                        if len(comment) != 0:
                            record.comments.append(comment)
                            record.save()
                            return fk.Response('Projject comment posted', status.HTTP_200_OK)
                        else:
                            return fk.redirect('http://0.0.0.0:5000/error-400/')
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-415/')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_denied')
    else:
       return fk.redirect('http://0.0.0.0:5000/error-405/') 

@app.route(CLOUD_URL + '/<hash_session>/record/comments/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def record_comments(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/comments/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None or (record != None and record.access != 'public'):
                return fk.redirect('http://0.0.0.0:5000/?action=comments_failed')
            else:
                return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=comments_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/') 

@app.route(CLOUD_URL + '/<hash_session>/record/view/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def record_view(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/view/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if record.project.owner == current_user:
                    return fk.Response(record.to_json(), mimetype='application/json')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')      

@app.route(CLOUD_URL + '/<hash_session>/record/edit/<record_id>', methods=['POST'])
@crossdomain(origin='*')
def record_edit(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/edit/<record_id>")
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
                    record = RecordModel.objects.with_id(record_id)
                except:
                    print str(traceback.print_exc())
                if record is None:
                    return fk.redirect('http://0.0.0.0:5000/error-204/')
                else:
                    if record.project.owner == current_user:
                        if fk.request.data:
                                data = json.loads(fk.request.data)
                                try:
                                    head = data.get("head", {})
                                    content = data.get("content", {})
                                    #process the updaye to be made.
                                    record.save()
                                    return fk.Response('Record edited', status.HTTP_200_OK)
                                except:
                                    print str(traceback.print_exc())
                                    return fk.redirect('http://0.0.0.0:5000/error-400/')
                        else:
                            return fk.redirect('http://0.0.0.0:5000/error-415/')
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-401/?action=edit_failed')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-404/')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/record/pull/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def pull_record(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/pull/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=pull_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                try:
                    record = RecordModel.objects.with_id(record_id)
                except:
                    print str(traceback.print_exc())
                if record is None:
                    return fk.redirect('http://0.0.0.0:5000/error-204/')
                else:
                    if record.project.owner == current_user:
                        record_user = record.project.owner
                        if record.environment:
                            environment = record.environment
                            if environment.bundle['location']:
                                bundle = load_bundle(record)
                                # print image[1]
                                return fk.send_file(
                                    bundle[0],
                                    mimetypes.guess_type(bundle[1])[0],
                                    as_attachment=True,
                                    attachment_filename=str(record_user.id)+"-"+str(record.project.id)+"-"+str(record_id)+"-record.zip",
                                )
                            else:
                                print "Failed because of environment bundle location not found."
                                return fk.redirect('http://0.0.0.0:5000/error-204/')
                        else:
                            print "No environment bundle."
                            return fk.redirect('http://0.0.0.0:5000/error-204/')
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-401/?action=pull_failed')
                
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=pull_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/record/comments/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def public_record_comments(record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/record/comments/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print str(traceback.print_exc())
        if record is None or (record != None and record.access != 'public'):
            return fk.redirect('http://0.0.0.0:5000/?action=comments_failed')
        else:
            return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/') 

@app.route(CLOUD_URL + '/public/record/view/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def public_record_view(record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/record/view/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print str(traceback.print_exc())
        if record is None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
        else:
            if record.access == 'public':
                return fk.Response(record.to_json(), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')   

@app.route(CLOUD_URL + '/public/record/pull/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def public_pull_record(record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/record/pull/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print str(traceback.print_exc())
        if record is None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
        else:
            if record.project.access == 'public':
                if record.environment:
                    record_user = record.project.owner
                    environment = record.environment
                    if environment.bundle['location']:
                        bundle = load_bundle(record)
                        # print image[1]
                        return fk.send_file(
                            bundle[0],
                            mimetypes.guess_type(bundle[1])[0],
                            as_attachment=True,
                            attachment_filename=str(record_user.id)+"-"+str(record.project.id)+"-"+str(record_id)+"-record.zip",
                        )
                    else:
                        print "Failed because of environment bundle location not found."
                        return fk.redirect('http://0.0.0.0:5000/error-204/')
                else:
                    print "No environment bundle."
                    return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=pull_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')  

#To be fixed.
#Implement the quotas here image_obj.tell()
@app.route(CLOUD_URL + '/<hash_session>/record/file/upload/<record_id>', methods=['POST'])
@crossdomain(origin='*')
def file_add(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/file/upload/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
    user_model = UserModel.objects(session=hash_session).first()
    if user_model is None:
        return fk.redirect('http://0.0.0.0:5000/?action=update_denied')
    else:    
        if fk.request.method == 'POST':
            infos = {}
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if fk.request.data:
                    file_model = FileModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                    infos = json.loads(fk.request.data)
                    relative_path = infos.get("relative_path", "./")
                    group = infos.get("group", "undefined")
                    description = infos.get("description", "")

                    file_model.group = group
                    file_model.description = description

                    if fk.request.files:
                        if fk.request.files['file']:
                            file_obj = fk.request.files['file']

                            if current_user.quota+file_obj.tell() > 5000000000:
                                return fk.make_response("You have exceeded your 5Gb of quota. You will have to make some space.", status.HTTP_403_FORBIDDEN)
                            else:
                                relative_path = "%s%s"%(relative_path, file_obj.filename)
                                location = str(user_model.id)+"-"+str(record.id)+"_%s"%file_obj.filename

                                try:
                                    uploaded = upload_file(user_model, file_obj)
                                    if uploaded:
                                        file_model.relative_path = relative_path
                                        file_model.location = location
                                        today = datetime.date.today()
                                        (stat, created) = StatModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), interval="%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day), category="storage", periode="daily")
                                        if not created:
                                            stat.traffic += file_obj.tell()
                                            stat.save()
                                            file_model.save()
                                            return fk.make_response("File uploaded with success.", status.HTTP_200_OK)
                                        else:
                                            return fk.make_response("Could not create storage states.", status.HTTP_500_INTERNAL_SERVER_ERROR)
                                    else:
                                        file_model.delete()
                                        return fk.make_response("Could not upload the file.", status.HTTP_500_INTERNAL_SERVER_ERROR)
                                except Exception, e:
                                    return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
                    else:
                        return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/record/file/download/<file_id>', methods=['POST'])
@crossdomain(origin='*')
def file_download(hash_session, file_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/file/download/<file_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        user_model = UserModel.object.with_id(user_id)
        if user_model == None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
        else:
            try:
                record_file = FileModel.objects.with_id(file_id)
            except:
                print str(traceback.print_exc())
            if record_file is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if record_file.record.project.owner == current_user:
                    _file = load_file(record_file)
                    print _file[1]
                    return fk.send_file(
                        _file[0],
                        mimetypes.guess_type(_file[1])[0],
                        as_attachment=True,
                        attachment_filename=profile_model.record_file['location'].split("_")[1],
                    )
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_failed')
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/<hash_session>/record/file/remove/<file_id>', methods=['DELETE'])
@crossdomain(origin='*')
def file_remove(hash_session, file_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/record/file/remove/<file_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
    if fk.request.method == 'DELETE':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record_file = FileModel.objects.with_id(file_id)
            except:
                print str(traceback.print_exc())
            if record_file is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
            else:
                if record_file.record.project.owner == current_user:
                    delete_record_file(record_file)
                    record_file.delete()
                    return fk.Response('Record file removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=remove_denied')

