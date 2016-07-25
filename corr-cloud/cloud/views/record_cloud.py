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
from cloud import app, stormpath_manager, prepare_record, crossdomain, delete_record_files, delete_record_file, CLOUD_URL, VIEW_HOST, VIEW_PORT, s3_get_file, logStat, logTraffic, logAccess
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

@app.route(CLOUD_URL + '/private/<hash_session>/record/remove/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def record_remove(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/remove/<record_id>')
        
    if fk.request.method in ['GET', 'DELETE']:
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is not None:
            try:
                logAccess('cloud', '/private/<hash_session>/record/remove/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    result = delete_record_files(record)
                    if result:
                        logStat(deleted=True, record=record)
                        record.delete()
                    return fk.redirect('{0}:{1}/dashboard/?session={2}&view=records&project={3}'.format(VIEW_HOST, VIEW_PORT, hash_session, str(record.project.id)))
                else:
                    return fk.redirect('{0}:{1}/error-401/?action=remove_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error-401/?action=remove_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/comment/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def record_comment(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/comment/<record_id>')
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is not None:
            try:
                logAccess('cloud', '/private/<hash_session>/record/comment/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
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
                            return fk.redirect('{0}:{1}/error-400/'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error-415/'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error-401/?action=remove_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error-401/?action=remove_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def record_comments(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/comments/<record_id>')
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is not None:
            try:
                logAccess('cloud', '/private/<hash_session>/record/comments/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None or (record != None and record.access != 'public'):
                return fk.redirect('{0}:{1}/?action=comments_failed'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error-401/?action=comments_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def record_view(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/view/<record_id>')
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is not None:
            try:
                logAccess('cloud', '/private/<hash_session>/record/view/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    return fk.Response(record.to_json(), mimetype='application/json')
                else:
                    return fk.redirect('{0}:{1}/error-401/?action=view_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error-401/?action=view_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT))      

@app.route(CLOUD_URL + '/private/<hash_session>/record/edit/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def record_edit(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/edit/<record_id>')
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is None:
            return fk.redirect('{0}:{1}/error-401/?action=edit_denied'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess('cloud', '/private/<hash_session>/record/edit/<record_id>')
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print("Allowance: {0}".format(allowance))
            if allowance == hash_session:
                try:
                    record = RecordModel.objects.with_id(record_id)
                except:
                    print(str(traceback.print_exc()))
                if record is None:
                    return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
                else:
                    if record.project.owner == current_user:
                        if fk.request.data:
                                data = json.loads(fk.request.data)
                                try:
                                    # only tags and rationels
                                    tags = data.get("tags", ','.join(record.tags))
                                    rationels = data.get("rationels", record.rationels)
                                    record.tags = tags.split(',')
                                    record.rationels = [rationels]
                                    record.save()
                                    return fk.Response('Record edited', status.HTTP_200_OK)
                                except:
                                    print(str(traceback.print_exc()))
                                    return fk.redirect('{0}:{1}/error-400/'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.redirect('{0}:{1}/error-415/'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error-401/?action=edit_failed'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.redirect('{0}:{1}/error-404/'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def pull_record(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/pull/<record_id>')
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is None:
            return fk.redirect('{0}:{1}/error-401/?action=pull_denied'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess('cloud', '/private/<hash_session>/record/pull/<record_id>')
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print("Allowance: {0}".format(allowance))
            if allowance == hash_session:
                try:
                    record = RecordModel.objects.with_id(record_id)
                except:
                    record = None
                    print(str(traceback.print_exc()))
                if record is None:
                    return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
                else:
                    prepared = prepare_record(record)
                    if prepared[0] == None:
                        print("Unable to retrieve a record to download.")
                        return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
                
            else:
                return fk.redirect('{0}:{1}/error-401/?action=pull_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def public_record_comments(record_id):
    logTraffic(endpoint='/public/record/comments/<record_id>')
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None or (record != None and record.access != 'public'):
            return fk.redirect('{0}:{1}/?action=comments_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/public/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def public_record_view(record_id):
    logTraffic(endpoint='/public/record/view/<record_id>')
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None:
            return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
        else:
            if record.access == 'public':
                return fk.Response(record.to_json(), mimetype='application/json')
            else:
                return fk.redirect('{0}:{1}/error-401/?action=view_failed'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT))   

@app.route(CLOUD_URL + '/public/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def public_pull_record(record_id):
    logTraffic(endpoint='/public/record/pull/<record_id>')
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None:
            return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
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
                        print("Failed because of environment bundle location not found.")
                        return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
                else:
                    print("No environment bundle.")
                    return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.redirect('{0}:{1}/error-401/?action=pull_denied'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error-405/'.format(VIEW_HOST, VIEW_PORT))  

#To be fixed.
#Implement the quotas here image_obj.tell()
@app.route(CLOUD_URL + '/private/<hash_session>/record/file/upload/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def file_add(hash_session, record_id):
    logTraffic(endpoint='/private/<hash_session>/record/file/upload/<record_id>')
    user_model = UserModel.objects(session=hash_session).first()
    if user_model is None:
        return fk.redirect('{0}:{1}/?action=update_denied'.format(VIEW_HOST, VIEW_PORT))
    else:    
        if fk.request.method == 'POST':
            infos = {}
            try:
                logAccess('cloud', '/private/<hash_session>/record/file/upload/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
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
                                except Exception as e:
                                    return fk.make_response(str(traceback.print_exc()), status.HTTP_400_BAD_REQUEST)
                    else:
                        return fk.make_response("Missing mandatory fields.", status.HTTP_400_BAD_REQUEST)
        else:
            return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/record/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def file_download(hash_session, file_id):
    logTraffic(endpoint='/private/<hash_session>/record/file/download/<file_id>')
        
    if fk.request.method == 'GET':
        user_model = UserModel.object.with_id(user_id)
        if user_model == None:
            return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess('cloud', '/private/<hash_session>/record/file/download/<file_id>')
                record_file = FileModel.objects.with_id(file_id)
            except:
                print(str(traceback.print_exc()))
            if record_file is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record_file.record.project.owner == current_user:
                    _file = load_file(record_file)
                    print(_file[1])
                    return fk.send_file(
                        _file[0],
                        mimetypes.guess_type(_file[1])[0],
                        as_attachment=True,
                        attachment_filename=profile_model.record_file['location'].split("_")[1],
                    )
                else:
                    return fk.redirect('{0}:{1}/error-401/?action=remove_failed'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.make_response('Method not allowed.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/record/file/remove/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(origin='*')
def file_remove(hash_session, file_id):
    logTraffic(endpoint='/private/<hash_session>/record/file/remove/<file_id>')
    if fk.request.method == 'DELETE':
        current_user = UserModel.objects(session=hash_session).first()
        print(fk.request.path)
        if current_user is not None:
            try:
                logAccess('cloud', '/private/<hash_session>/record/file/remove/<file_id>')
                record_file = FileModel.objects.with_id(file_id)
            except:
                print(str(traceback.print_exc()))
            if record_file is None:
                return fk.redirect('{0}:{1}/error-204/'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record_file.record.project.owner == current_user:
                    delete_record_file(record_file)
                    # record_file.delete()
                    return fk.Response('Record file removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('{0}:{1}/error-401/?action=remove_failed'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error-401/?action=remove_denied'.format(VIEW_HOST, VIEW_PORT))

