from corrdb.common import logAccess, logStat, logTraffic, crossdomain
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
from cloud import app, cloud_response, storage_manager, access_manager, CLOUD_URL, VIEW_HOST, VIEW_PORT, VIEW_MODE
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
import mimetypes

@app.route(CLOUD_URL + '/private/<hash_session>/record/remove/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_remove(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/remove/<record_id>')     
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/remove/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    result = storage_manager.delete_record_files(record)
                    if result:
                        logStat(deleted=True, record=record)
                        record.delete()
                    return fk.redirect('{0}:{1}/dashboard/?session={2}&view=records&project={3}'.format(VIEW_HOST, VIEW_PORT, hash_session, str(record.project.id)))
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/comment/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_comment(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/comment/<record_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/comment/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    if fk.request.data:
                        data = json.loads(fk.request.data)
                        comment = data.get("comment", {})
                        if len(comment) != 0:
                            record.comments.append(comment)
                            record.save()
                            return fk.Response('Projject comment posted', status.HTTP_200_OK)
                        else:
                            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_comments(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/comments/<record_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/comments/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None or (record != None and record.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/<hash_session>/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_view(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/view/<record_id>')
    if fk.request.method == 'GET':
        caccess_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/view/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    return fk.Response(record.to_json(), mimetype='application/json')
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))      

@app.route(CLOUD_URL + '/private/<hash_session>/record/create/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_create(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/create/<project_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/create/<project_id>')
            try:
                project = ProjectModel.objects.with_id(project_id)
            except:
                print(str(traceback.print_exc()))
            if project is None:
                return cloud_response(404, 'Record not created.', "The project referenced is unknown.")
            else:
                if project.owner == current_user:
                    if fk.request.data:
                            data = json.loads(fk.request.data)
                            try:
                                record = RecordModel(created_at=str(datetime.datetime.utcnow()), project=project)
                                tags = data.get("tags", "")
                                rationels = data.get("rationels", "")
                                status = data.get("status", "unknown")
                                content = data.get("content", "no content")
                                access = data.get("access", "public")
                                record.tags = [tags]
                                record.rationels = [rationels]
                                record.status = status
                                record.access = access
                                record.extend = {"uploaded":content}
                                record.save()
                                return cloud_response(201, 'Record successfully created.', "The record was created.")
                            except:
                                print(str(traceback.print_exc()))
                                return cloud_response(500, 'record not created.', str(traceback.print_exc()))
                    else:
                        return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return cloud_response(401, 'Record not created.', "You are not this project owner.")
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/record/edit/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_edit(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/edit/<record_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user:
                    if fk.request.data:
                            data = json.loads(fk.request.data)
                            try:
                                tags = data.get("tags", ','.join(record.tags))
                                rationels = data.get("rationels", record.rationels)
                                status = data.get("status", record.status)
                                record.tags = tags.split(',')
                                record.rationels = [rationels]
                                record.status = status
                                record.save()
                                return fk.Response('Record edited', status.HTTP_200_OK)
                            except:
                                print(str(traceback.print_exc()))
                                return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def pull_record(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/pull/<record_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/pull/<record_id>')
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                record = None
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                prepared = storage_manager.prepare_record(record)
                if prepared[0] == None:
                    print("Unable to retrieve a record to download.")
                    return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_record_comments(record_id):
    logTraffic(CLOUD_URL, endpoint='/public/record/comments/<record_id>')
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None or (record != None and record.access != 'public'):
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.Response(json.dumps(record.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/public/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_record_view(record_id):
    logTraffic(CLOUD_URL, endpoint='/public/record/view/<record_id>')
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            if record.access == 'public':
                return fk.Response(record.to_json(), mimetype='application/json')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))   

@app.route(CLOUD_URL + '/public/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_pull_record(record_id):
    logTraffic(CLOUD_URL, endpoint='/public/record/pull/<record_id>')
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            if record.project.access == 'public':
                prepared = storage_manager.prepare_record(record)
                if prepared[0] == None:
                    print("Unable to retrieve a record to download.")
                    return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

#To be fixed.
#Implement the quotas here image_obj.tell()
@app.route(CLOUD_URL + '/private/<hash_session>/record/file/upload/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def file_add(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/file/upload/<record_id>')
    access_resp = access_manager.check_cloud(hash_session)
    user_model = access_resp[1]
    if user_model is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:    
        if fk.request.method == 'POST':
            infos = {}
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/file/upload/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
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
                                return fk.redirect('{0}:{1}/error/?code=403'.format(VIEW_HOST, VIEW_PORT))
                            else:
                                relative_path = "%s%s"%(relative_path, file_obj.filename)
                                location = str(user_model.id)+"-"+str(record.id)+"_%s"%file_obj.filename

                                try:
                                    uploaded = storage_manager.storage_upload_file(file_model, file_obj)
                                    if uploaded[0]:
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
                                            return fk.redirect('{0}:{1}/error/?code=500'.format(VIEW_HOST, VIEW_PORT))
                                    else:
                                        file_model.delete()
                                        return fk.redirect('{0}:{1}/error/?code=500'.format(VIEW_HOST, VIEW_PORT))
                                except Exception as e:
                                    traceback.print_exc()
                                    return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/record/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def file_download(hash_session, file_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/file/download/<file_id>')
        
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/file/download/<file_id>')
                record_file = FileModel.objects.with_id(file_id)
            except:
                print(str(traceback.print_exc()))
            if record_file is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record_file.record.project.owner == current_user:
                    _file = storage_manager.storage_get_file('file', record_file.storage)
                    return fk.send_file(
                        _file,
                        mimetype=_file.mimetype,
                        as_attachment=True,
                        attachment_filename=_file.name,
                    )
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/record/file/remove/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def file_remove(hash_session, file_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/file/remove/<file_id>')
    if fk.request.method == 'DELETE':
        access_resp = access_manager.check_cloud(hash_session)
        user_model = access_resp[1]
        if user_model is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/record/file/remove/<file_id>')
                record_file = FileModel.objects.with_id(file_id)
            except:
                print(str(traceback.print_exc()))
            if record_file is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record_file.record.project.owner == current_user:
                    storage_manager.delete_record_file(record_file)
                    return fk.Response('Record file removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))

