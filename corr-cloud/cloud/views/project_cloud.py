from corrdb.common import logAccess, logStat, logTraffic, crossdomain, basicAuthSession
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
from cloud import app, cloud_response, storage_manager, access_manager, secure_content ,CLOUD_URL, VIEW_HOST, VIEW_PORT, MODE, ACC_SEC, CNT_SEC
import datetime
import simplejson as json
import traceback
import smtplib
from email.mime.text import MIMEText
import mimetypes

@app.route(CLOUD_URL + '/private/project/sync/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_sync(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/sync/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/sync/<project_id>')
            p = ProjectModel.objects.with_id(project_id)
            if p ==  None or (p != None and p.owner != current_user and p.access != 'public' and current_user.group != "admin"):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                project = {"project":json.loads(p.summary_json())}
                records = RecordModel.objects(project=p)
                project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/project/view/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_view(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/view/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/view/<project_id>')
            p = ProjectModel.objects.with_id(project_id)
            if p ==  None or (p != None and p.owner != current_user and p.access != 'public' and current_user.group != "admin"):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                project = {"project":json.loads(p.to_json())}
                records = RecordModel.objects(project=p)
                project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/project/remove/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_remove(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/remove/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/remove/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.owner != current_user and current_user.group != "admin"):
                return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
            else:
                storage_manager.delete_project_files(project, logStat)
                project.delete()
                logStat(deleted=True, project=project)
                return cloud_response(200, 'Deletion succeeded', 'The project %s was succesfully deleted.'%project_id)
        else:
            return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/project/comment/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_comment(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/comment/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/comment/<project_id>')
            if current_user.quota >= current_user.max_quota*1024*1024*1024:
                return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)

            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.access != 'public' and current_user.group != "admin"):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
                    security = secure_content(fk.request.data)
                    if not security[0]:
                        return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                    data = json.loads(fk.request.data)
                    comment = data.get("comment", {})
                    if len(comment) != 0:
                        project.comments.append(comment)
                        project.save()
                        return fk.Response('Projject comment posted', status.HTTP_200_OK)
                    else:
                        return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_comments(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/comments/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/comments/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.access != 'public' and current_user.group != "admin"):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(json.dumps(project.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/project/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_create():
    logTraffic(CLOUD_URL, endpoint='/private/project/create')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/create')
            if current_user.quota >= current_user.max_quota*1024*1024*1024:
                return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
            if fk.request.data:
                security = secure_content(fk.request.data)
                if not security[0]:
                    return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                data = json.loads(fk.request.data)
                try:
                    name = data.get("name", "")
                    description = data.get("description", "")
                    goals = data.get("goals", "")
                    access = data.get("access", 'public')
                    group = data.get("group", "undefined")
                    tags = data.get("tags", "")
                    environment = data.get("environment", {})
                    query_project = ProjectModel.objects(owner=current_user, name=name).first()
                    if query_project is None:
                        project = ProjectModel(created_at=str(datetime.datetime.utcnow()), owner=current_user, name=name)
                        project.description = description
                        project.access = access
                        project.goals = goals
                        project.group = group
                        project.tags = [tags]
                        project.save()
                        return cloud_response(201, 'Project successfully created.', project.info())
                    else:
                        return fk.Response('A project with this name already exists.', status.HTTP_403_FORBIDDEN)
                except:
                    print(str(traceback.print_exc()))
                    return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return fk.Response('No content provided for the creation.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/project/edit/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_edit(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/project/edit/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/edit/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.owner != current_user and current_user.group != "admin"):
                return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
            else:
                if fk.request.data:
                    security = secure_content(fk.request.data)
                    if not security[0]:
                        return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                    data = json.loads(fk.request.data)
                    try:
                        description = data.get("description", project.description)
                        goals = data.get("goals", project.goals)
                        group = data.get("group", project.group)
                        access = data.get("access", 'unchanged')
                        tags = data.get("tags", ','.join(project.tags))
                        environment = data.get("environment", {})
                        project.description = description
                        project.goals = goals
                        project.group = group
                        if access != "unchanged":
                            project.access = access
                        project.tags = tags.split(',')
                        if len(environment) != 0:
                            environment_model = EnvironmentModel.objects.with_id(environment['id'])
                            if environment_model is not None:
                                system = environment.get('system', environment_model.system)
                                version = environment.get('version', environment_model.version)
                                specifics = environment.get('specifics', environment_model.specifics)
                                group = environment.get('group', environment_model.group)
                                remote_bundle = environment.get('bundle', '')
                                environment_model.system = system
                                environment_model.version = version
                                environment_model.specifics = specifics
                                environment_model.group = group
                                if remote_bundle != '' and environment_model.bundle['scope'] != 'local':
                                    environment_model.bundle['location'] = remote_bundle
                                environment_model.save()
                        project.save()
                        if access != "unchanged":
                            for record in RecordModel.objects(project=project):
                                record.access = access
                                record.save()

                        return fk.Response('Project updated', status.HTTP_200_OK)
                    except:
                        print(str(traceback.print_exc()))
                        return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return fk.Response('No content provided for the update.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/project/record/<project_name>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_records(project_name):
    logTraffic(CLOUD_URL, endpoint='/private/project/record/<project_name>')   
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/project/record/<project_name>')
            project = ProjectModel.objects(name=project_name).first()
            if project ==  None or (project != None and project.owner != current_user and project.access != 'public' and current_user.group != "admin"):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(project.activity_json(), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/project/sync/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_sync(project_id):
    logTraffic(CLOUD_URL, endpoint='/public/project/sync/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public' and current_user.group == "admin"):
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            project = {"project":json.loads(p.summary_json())}
            records = []
            for record in RecordModel.objects(project=p):
                if record.access == 'public':
                    records.append(record)
            project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
            return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))        

@app.route(CLOUD_URL + '/public/project/record/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_records(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/public/project/record/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.Response(p.activity_json(True), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_comments(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/public/project/comments/<project_id>')
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project ==  None or (project != None and project.access != 'public'):
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.Response(json.dumps(project.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/project/view/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_view(project_id):
    logTraffic(CLOUD_URL, endpoint='/public/project/view/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            project = {"project":json.loads(p.to_json())}
            records = RecordModel.objects(project=p)
            project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
            return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))    