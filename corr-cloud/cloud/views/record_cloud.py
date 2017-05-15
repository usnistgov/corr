from corrdb.common import logAccess, logStat, logTraffic, crossdomain, basicAuthSession
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
from flask.ext.api import status
import flask as fk
from cloud import app, cloud_response, storage_manager, access_manager, data_pop, CLOUD_URL, VIEW_HOST, VIEW_PORT, MODE, ACC_SEC, CNT_SEC
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
import mimetypes

@app.route(CLOUD_URL + '/private/record/remove/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_remove(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/remove/<record_id>')
    hash_session = basicAuthSession(fk.request)     
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/remove/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.Response('Unable to find this record.', status.HTTP_404_NOT_FOUND)
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record.project.owner == current_user or current_user.group == "admin":
                    storage_manager.delete_record_files(record, logStat)
                    logStat(deleted=True, record=record)
                    env_id = None
                    if record.environment:
                        env_id = str(record.environment.id)
                    record.delete()
                    if env_id:
                        try:
                            record.project.history.remove(env_id)
                            record.project.save()
                        except:
                            pass
                    return cloud_response(200, 'Deletion succeeded', 'The record %s was succesfully deleted.'%record_id)
                else:
                    return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
    else:
       return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/record/comment/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_comment(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/comment/<record_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/comment/<record_id>')
                if current_user.quota >= current_user.max_quota*1024*1024*1024:
                    return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                # if record.project.owner == current_user  or current_user.group == "admin":
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
                # else:
                #     return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 

@app.route(CLOUD_URL + '/private/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_comments(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/comments/<record_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/comments/<record_id>')
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

@app.route(CLOUD_URL + '/private/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_view(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/view/<record_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/view/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.Response('Unable to find this record.', status.HTTP_404_NOT_FOUND)
            else:
                if record.project.owner == current_user or record.access == 'public' or current_user.group == "admin":
                    return fk.Response(record.to_json(), mimetype='application/json')
                else:
                    return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
        else:
            return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/record/create/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_create(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/create/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/record/create/<project_id>')
            if current_user.quota >= current_user.max_quota*1024*1024*1024:
                return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
            try:
                project = ProjectModel.objects.with_id(project_id)
            except:
                print(str(traceback.print_exc()))
            if project is None:
                return fk.Response('Unable to find the referenced project.', status.HTTP_404_NOT_FOUND)
            else:
                if project.owner == current_user  or current_user.group == "admin":
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
                                if len(project.history) > 0:
                                    head = project.history[-1]
                                    env = EnvironmentModel.objects.with_id(head)
                                    if env:
                                        record.environment = env
                                        record.save()
                                # project_content = {"project":json.loads(project.summary_json())}
                                # records = []
                                # for r in RecordModel.objects(project=project):
                                #     records.append(r)
                                # project_content["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                                return cloud_response(201, 'Record successfully created.', json.loads(project.summary_json()))
                            except:
                                print(str(traceback.print_exc()))
                                return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        return fk.Response('No content provided for the creation.', status.HTTP_204_NO_CONTENT)
                else:
                    return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/record/edit/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_edit(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/edit/<record_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/record/edit/<record_id>')
            if current_user.quota >= current_user.max_quota*1024*1024*1024:
                return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.Response('Unable to find this record.', status.HTTP_404_NOT_FOUND)
            else:
                if record.project.owner == current_user  or current_user.group == "admin":
                    if fk.request.data:
                            data = json.loads(fk.request.data)
                            try:
                                tags = data.get("tags", ','.join(record.tags))
                                data_pop(data, 'tags')
                                rationels = data.get("rationels", ','.join(record.rationels))
                                data_pop(data, 'rationels')
                                r_status = data.get("status", record.status)
                                data_pop(data, 'status')

                                r_access = data.get("access", record.access)
                                data_pop(data, 'access')

                                record.tags = tags.split(',')
                                record.rationels = rationels.split(',')
                                record.status = r_status
                                # if record.access != r_access and record.project.access == "private":
                                #     return fk.Response('Unauthorized action on this record. Record access cannot be changed when project is private.', status.HTTP_401_UNAUTHORIZED)
                                record.access = r_access
                                record.save()

                                body = data.get("body", None)
                                if body:
                                    data = body
                                system = data.get("system", record.system)
                                data_pop(data, 'system')
                                execution = data.get("execution", record.execution)
                                data_pop(data, 'execution')
                                inputs = data.get("inputs", record.inputs)
                                data_pop(data, 'inputs')
                                outputs = data.get("outputs", record.outputs)
                                data_pop(data, 'outputs')
                                dependencies = data.get("dependencies", record.dependencies)
                                data_pop(data, 'dependencies')

                                if not isinstance(inputs, list):
                                    inputs = [inputs]

                                if not isinstance(outputs, list):
                                    outputs = [outputs]

                                if not isinstance(dependencies, list):
                                    dependencies = [dependencies]

                                record.system = system
                                record.execution = execution
                                record.inputs = inputs
                                record.outputs = outputs
                                record.dependencies = dependencies
                                record.save()

                                # Allow all the extra keys to go inside body.
                                if len(data) != 0:
                                    body, created = RecordBodyModel.objects.get_or_create(head=record)
                                    if created:
                                        body.data = data
                                    else:
                                        already = body.data
                                        for key, value in data.items():
                                            already[key] = value
                                        body.data = already
                                    body.save()

                                return fk.Response(record.summary_json(), mimetype='application/json')
                            except:
                                print(str(traceback.print_exc()))
                                return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                    else:
                        return fk.Response('No content provided for the update.', status.HTTP_204_NO_CONTENT)
                else:
                    return fk.Response('Unauthorized action on this record.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def pull_record(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/record/pull/<record_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
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
                return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
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

@app.route(CLOUD_URL + '/public/record/comments/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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

@app.route(CLOUD_URL + '/public/record/view/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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

@app.route(CLOUD_URL + '/public/record/pull/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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
@app.route(CLOUD_URL + '/private/record/file/upload/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def file_add(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/file/upload/<record_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    user_model = access_resp[1]
    if user_model is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:    
        if fk.request.method == 'POST':
            infos = {}
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/file/upload/<record_id>')
                if current_user.quota >= current_user.max_quota*1024*1024*1024:
                    return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
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

                            if current_user.quota+file_obj.tell() > current_user.max_quota*1024*1024*1024:
                                return fk.Response('You will exceede your allowed maximum quota with this file.', status.HTTP_401_UNAUTHORIZED)
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

@app.route(CLOUD_URL + '/private/record/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def file_download(file_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/file/download/<file_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/file/download/<file_id>')
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

@app.route(CLOUD_URL + '/private/record/file/remove/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def file_remove(file_id):
    logTraffic(CLOUD_URL, endpoint='/private/record/file/remove/<file_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'DELETE':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        user_model = access_resp[1]
        if user_model is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/record/file/remove/<file_id>')
                record_file = FileModel.objects.with_id(file_id)
            except:
                print(str(traceback.print_exc()))
            if record_file is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if record_file.record.project.owner == current_user:
                    storage_manager.delete_record_file(record_file, logStat)
                    return fk.Response('Record file removed', status.HTTP_200_OK)
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

