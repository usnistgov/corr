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
from cloud import app, stormpath_manager, crossdomain, delete_project_files, CLOUD_URL
import datetime
import json
import traceback
import smtplib
from email.mime.text import MIMEText
from cloud import load_bundle
import mimetypes

# CLOUD_VERSION = 1
# CLOUD_URL = '/cloud/v{0}'.format(CLOUD_VERSION)

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

#Fix the redirections.
#Make the public search for projects and records and diffs in the dashboard.

#Make a diff_cloud route. to create, update, remove and view diff.

@app.route(CLOUD_URL + '/<hash_session>/project/sync/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def project_sync(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/sync/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/?action=sync_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                p = ProjectModel.objects.with_id(project_id)
                if p ==  None or (p != None and p.owner != current_user and p.access != 'public'):
                    return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
                else:
                    project = {"project":json.loads(p.summary_json())}
                    records = RecordModel.objects(project=p)
                    project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                    return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/project/view/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def project_view(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/view/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/?action=sync_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                p = ProjectModel.objects.with_id(project_id)
                if p ==  None or (p != None and p.owner != current_user and p.access != 'public'):
                    return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
                else:
                    project = {"project":json.loads(p.to_json())}
                    records = RecordModel.objects(project=p)
                    project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                    return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')           

@app.route(CLOUD_URL + '/<hash_session>/project/remove/<project_id>', methods=['DELETE'])
@crossdomain(origin='*')
def project_remove(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/remove/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'DELETE':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            # if project_name is not None:
            project = ProjectModel.objects.with_id(project_id)
            # project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            if project ==  None or (project != None and project.owner != current_user):
                return fk.redirect('http://0.0.0.0:5000/?action=remove_failed')
            else:
                delete_project_files(project)
                project.delete()
                return fk.Response('Project deleted', status.HTTP_200_OK)
            # else:
            #     projects = ProjectModel.objects(owner=current_user)
            #     for project in projects:
            #         delete_project_files(project)
            #         project.delete()
            #     return fk.Response('All projects deleted', status.HTTP_200_OK)
        else:
            return fk.redirect('http://0.0.0.0:5000/?action=remove_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/project/comment/<project_id>', methods=['POST'])
@crossdomain(origin='*')
def project_comment(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/comment/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            # if project_name is not None:
            project = ProjectModel.objects.with_id(project_id)
            # project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            if project ==  None or (project != None and project.access != 'public'):
                return fk.redirect('http://0.0.0.0:5000/?action=comment_failed')
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    comment = data.get("comment", {}) #{"user":str(user_id), "created":str(datetime.datetime.utc()), "title":"", "content":""}
                    if len(comment) != 0:
                        project.comments.append(comment)
                        project.save()
                        return fk.Response('Projject comment posted', status.HTTP_200_OK)
                    else:
                        return fk.redirect('http://0.0.0.0:5000/error-400/')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-415/')
        else:
            return fk.redirect('http://0.0.0.0:5000/?action=comment_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/project/comments/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def project_comments(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/comments/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/?action=comments_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                project = ProjectModel.objects.with_id(project_id)
                # project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
                if project ==  None or (project != None and project.access != 'public'):
                    return fk.redirect('http://0.0.0.0:5000/?action=comments_failed')
                else:
                    return fk.Response(json.dumps(project.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=comments_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/project/edit/<project_id>', methods=['POST'])
@crossdomain(origin='*')
def project_edit(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/edit/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'POST':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            project = ProjectModel.objects.with_id(project_id)
            # project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
            if project ==  None or (project != None and project.owner != current_user):
                return fk.redirect('http://0.0.0.0:5000/?action=edit_failed')
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    try:
                        description = data.get("description", project.description)
                        goals = data.get("goals", project.goals)
                        group = data.get("group", project.group)
                        environment = data.get("environment", {})
                        project.description = description
                        project.goals = goals
                        project.group = group
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
                        print str(traceback.print_exc())
                        return fk.make_response("Could not edit the project.", status.HTTP_503_SERVICE_UNAVAILABLE)
                else:
                    return fk.Response('Nothing to update', status.HTTP_200_OK)
        else:
            return fk.redirect('http://0.0.0.0:5000/?action=edit_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')       

#project_name or project_id
@app.route(CLOUD_URL + '/<hash_session>/project/record/<project_name>', methods=['GET'])
@crossdomain(origin='*')
def project_records(hash_session, project_name):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/project/record/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/?action=records_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                project = ProjectModel.objects(name=project_name).first()
                # project = ProjectModel.objects(name=project_name, owner=current_user).first_or_404()
                if project ==  None or (project != None and project.owner != current_user and project.access != 'public'):
                    return fk.redirect('http://0.0.0.0:5000/?action=records_failed')
                else:
                    return fk.Response(project.activity_json(), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/?action=records_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')


# Public access
@app.route(CLOUD_URL + '/public/project/sync/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def public_project_sync(project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/project/sync/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
            return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
        else:
            # if not p.private:
            project = {"project":json.loads(p.summary_json())}
            records = []
            for record in RecordModel.objects(project=p):
                if record.access == 'public':
                    records.append(record)
            project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
            return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')        

@app.route(CLOUD_URL + '/public/project/record/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def public_project_records(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/project/record/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
            return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
        else:
            return fk.Response(p.activity_json(True), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/project/comments/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def public_project_comments(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/project/comments/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        project = ProjectModel.objects.with_id(project_id)
        if project ==  None or (project != None and project.access != 'public'):
            return fk.redirect('http://0.0.0.0:5000/?action=comments_failed')
        else:
            return fk.Response(json.dumps(project.comments, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/project/view/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def public_project_view(project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/project/view/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p ==  None or (p != None and p.access != 'public'):
            return fk.redirect('http://0.0.0.0:5000/?action=sync_failed')
        else:
            project = {"project":json.loads(p.to_json())}
            records = RecordModel.objects(project=p)
            project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
            return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')    