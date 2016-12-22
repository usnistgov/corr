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

@app.route(CLOUD_URL + '/private/<hash_session>/project/sync/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_sync(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/sync/<project_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/sync/<project_id>')
            p = ProjectModel.objects.with_id(project_id)
            if p ==  None or (p != None and p.owner != current_user and p.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                project = {"project":json.loads(p.summary_json())}
                records = RecordModel.objects(project=p)
                project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/project/view/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_view(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/view/<project_id>')
        
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/view/<project_id>')
            p = ProjectModel.objects.with_id(project_id)
            if p ==  None or (p != None and p.owner != current_user and p.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                project = {"project":json.loads(p.to_json())}
                records = RecordModel.objects(project=p)
                project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))           

@app.route(CLOUD_URL + '/private/<hash_session>/project/remove/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_remove(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/remove/<project_id>')
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/remove/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.owner != current_user):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                storage_manager.delete_project_files(project)
                project.delete()
                logStat(deleted=True, project=project)
                return fk.redirect('{0}:{1}/dashboard/?session={2}'.format(VIEW_HOST, VIEW_PORT, hash_session))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/project/comment/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_comment(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/comment/<project_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/comment/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
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

@app.route(CLOUD_URL + '/private/<hash_session>/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_comments(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/comments/<project_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/comments/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(json.dumps(project.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/project/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_create(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/create')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/create')
            if fk.request.data:
                data = json.loads(fk.request.data)
                try:
                    name = data.get("name", "")
                    description = data.get("description", "")
                    goals = data.get("goals", "")
                    access = data.get("goals", "public")
                    group = data.get("group", "undefined")
                    tags = data.get("tags", ",")
                    environment = data.get("environment", {})
                    query_project = ProjectModel.objects(owner=current_user, name=name).first()
                    if query_project is None:
                        project = ProjectModel(created_at=str(datetime.datetime.utcnow()), owner=current_user, name=name)
                        project.description = description
                        project.access = access
                        project.goals = goals
                        project.group = group
                        project.tags = tags.split(',')
                        project.save()
                        return cloud_response(201, 'Project successfully created.', "The project was created.")
                    else:
                        return cloud_response(409, 'Project not created.', "A project with this name already exists.")
                except:
                    print(str(traceback.print_exc()))
                    return fk.redirect('{0}:{1}/error/?code=503'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response('Nothing to create from', status.HTTP_200_OK)
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/project/edit/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_edit(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/edit/<project_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/edit/<project_id>')
            project = ProjectModel.objects.with_id(project_id)
            if project ==  None or (project != None and project.owner != current_user):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    try:
                        description = data.get("description", project.description)
                        goals = data.get("goals", project.goals)
                        group = data.get("group", project.group)
                        tags = data.get("tags", ','.join(project.tags))
                        environment = data.get("environment", {})
                        project.description = description
                        project.goals = goals
                        project.group = group
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
                        return fk.Response('Project updated', status.HTTP_200_OK)
                    except:
                        print(str(traceback.print_exc()))
                        return fk.redirect('{0}:{1}/error/?code=503'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.Response('Nothing to update', status.HTTP_200_OK)
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))       

@app.route(CLOUD_URL + '/private/<hash_session>/project/record/<project_name>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_records(hash_session, project_name):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/project/record/<project_name>')   
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/project/record/<project_name>')
            project = ProjectModel.objects(name=project_name).first()
            if project ==  None or (project != None and project.owner != current_user and project.access != 'public'):
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(project.activity_json(), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/project/sync/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_sync(project_id):
    logTraffic(CLOUD_URL, endpoint='/public/project/sync/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
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

@app.route(CLOUD_URL + '/public/project/record/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
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

@app.route(CLOUD_URL + '/public/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
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

@app.route(CLOUD_URL + '/public/project/view/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
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