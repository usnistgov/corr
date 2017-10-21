from corrdb.common import logAccess, logStat, logTraffic, crossdomain, basicAuthSession
from corrdb.common.models import UserModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from corrdb.common.models import VersionModel
from corrdb.common.models import BundleModel
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

@app.route(CLOUD_URL + '/private/env/remove/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def env_remove(env_id):
    logTraffic(CLOUD_URL, endpoint='/private/env/remove/<env_id>')
    hash_session = basicAuthSession(fk.request)     
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None :
            return fk.Response('Unauthorized action on this environment.', status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/env/remove/<env_id>')
                env = EnvironmentModel.objects.with_id(env_id)
            except:
                print(str(traceback.print_exc()))
            if env is None:
                return fk.Response('Unable to find this environment.', status.HTTP_404_NOT_FOUND)
            else:
                # result = storage_manager.delete_env_files(env)
                # if result:
                # implement project history en removal: project.history.append(str(env.id))
                
                count = 0
                for project in ProjectModel.objects(owner=current_user):
                    try:
                        project.history.remove(str(env_id))
                        project.save()
                        count = count + 1
                    except:
                        pass
                if count > 0:
                    env.delete()
                return cloud_response(200, 'Deletion succeeded', 'The environment %s was succesfully deleted.'%env_id)
    else:
       return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)


@app.route(CLOUD_URL + '/private/env/view/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def env_view(env_id):
    logTraffic(CLOUD_URL, endpoint='/private/env/view/<env_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'GET':
        caccess_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/env/view/<env_id>')
                env = EnvironmentModel.objects.with_id(env_id)
                # Make sure user own or used this environment.
                owned = False
                for project in ProjectModel.objects(owner=current_user):
                    if str(env.id) in project.history:
                        owned = True
                        break
                if not owned:
                    env = None
            except:
                env = None
                print(str(traceback.print_exc()))
            if env is None:
                return fk.Response('Unable to find this environment.', status.HTTP_404_NOT_FOUND)
            else:
                return fk.Response(env.to_json(), mimetype='application/json')
        else:
            return fk.Response('Unauthorized action on this environment.', status.HTTP_401_UNAUTHORIZED)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/env/create/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def env_create(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/env/create/<record_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/env/create/<record_id>')
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.Response('Unable to find the referenced record.', status.HTTP_404_NOT_FOUND)
            else:
                if fk.request.data:
                    security = secure_content(fk.request.data)
                    if not security[0]:
                        return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                    data = json.loads(fk.request.data)
                    try:
                        env = EnvironmentModel(created_at=str(datetime.datetime.utcnow()))
                        application_name = data.get("app", None)
                        if application_name and application_name != '':
                            application = ApplicationModel.objects(name=application_name).first()
                            if application:
                                # Maybe not put record increment here.
                                application.records = application.records + 1
                                application.save()
                                if str(current_user.id) not in application.users:
                                    application.users.append(str(current_user.id))
                                    application.save()
                                env.application = application

                        group = data.get("group", "unknown")
                        system = data.get("system", "undefined")
                        env.group = group
                        env.system = system
                        env.save()
                        project = record.project
                        if record.environment:
                            project.history.remove(str(record.environment.id))
                        record.environment = env
                        record.save()
                        project.history.append(str(env.id))
                        project.save()
                        return cloud_response(201, 'Environment successfully created.', project.history)
                    except:
                        print(str(traceback.print_exc()))
                        return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return fk.Response('No content provided for the creation.', status.HTTP_204_NO_CONTENT)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/env/next/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def env_next(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/env/next/<project_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/env/next/<project_id>')
            if current_user.quota >= current_user.max_quota*1024*1024*1024:
                return fk.Response('You have exceeded your allowed maximum quota.', status.HTTP_401_UNAUTHORIZED)
            try:
                project = ProjectModel.objects.with_id(project_id)
            except:
                print(str(traceback.print_exc()))
            if project is None:
                return fk.Response('Unable to find the referenced project.', status.HTTP_404_NOT_FOUND)
            else:
                if project.owner != current_user:
                    return fk.Response('Unauthorized action on this project.', status.HTTP_401_UNAUTHORIZED)
                if fk.request.data:
                    security = secure_content(fk.request.data)
                    if not security[0]:
                        return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                    data = json.loads(fk.request.data)
                    try:
                        env = EnvironmentModel(created_at=str(datetime.datetime.utcnow()))
                        application_name = data.get("app", None)
                        if application_name and application_name != '':
                            application = ApplicationModel.objects(name=application_name).first()
                            if application:
                                application.records = application.records + 1
                                application.save()
                                if str(current_user.id) not in application.users:
                                    application.users.append(str(current_user.id))
                                    application.save()
                                env.application = application

                        group = data.get("group", "unknown")
                        system = data.get("system", "undefined")
                        env.group = group
                        env.system = system
                        env.save()
                        version = VersionModel(created_at=str(datetime.datetime.utcnow()))
                        system = data.get("version", "unknown")
                        vc_location = data.get("version-location")
                        vc_baselines = vc_location.split("|")
                        if len(vc_baselines) > 0:
                            version.baseline = vc_baselines[0]
                        if len(vc_baselines) > 1:
                            version.marker = vc_baselines[1]
                        version.system = system
                        version.save()
                        env.version = version
                        env.save()
                        bundle = BundleModel(created_at=str(datetime.datetime.utcnow()))

                        scope = data.get("env-location", "unknown")
                        bundle.scope = scope
                        if scope == "remote":
                            bundle.storage = data.get("bundle-location", "unknown")

                        bundle.save()
                        env.bundle = bundle
                        env.save()
                        project.history.append(str(env.id))
                        project.save()
                        project_content = json.loads(project.summary_json())
                        project_content["env"] = {"bundle-id":str(bundle.id)}
                        return cloud_response(201, 'Environment successfully created.', project_content)
                    except:
                        print(str(traceback.print_exc()))
                        return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return fk.Response('No content provided for the creation.', status.HTTP_204_NO_CONTENT)
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/env/download/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def download_env(hash_session, env_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/env/download/<env_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        try:
            env = EnvironmentModel.objects.with_id(env_id)
            project = None
            for pro in ProjectModel.objects(owner=current_user):
                if str(env.id) in pro.history:
                    project = pro
                    break
        except:
            env = None
            project = None
            print(str(traceback.print_exc()))
            return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
        if env is None or project is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            # Envs are free for download.
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/<hash_session>/env/download/<env_id>')
            prepared = storage_manager.prepare_env(project, env)
            if prepared[0] == None:
                print("Unable to retrieve a env to download.")
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/env/edit/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def env_edit(env_id):
    logTraffic(CLOUD_URL, endpoint='/private/env/edit/<env_id>')
    hash_session = basicAuthSession(fk.request)
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.Response('Unauthorized action on this environment.', status.HTTP_401_UNAUTHORIZED)
        else:
            logAccess(fk, access_resp[1], CLOUD_URL, 'cloud', '/private/env/edit/<env_id>')
            try:
                env = EnvironmentModel.objects.with_id(env_id)
                owned = False
                for project in ProjectModel.objects(owner=current_user):
                    if str(env.id) in project.history:
                        owned = True
                        break
                if not owned:
                    env = None
            except:
                print(str(traceback.print_exc()))
            if env is None:
                return fk.Response('Unable to find this environment.', status.HTTP_404_NOT_FOUND)
            else:
                if fk.request.data:
                    security = secure_content(fk.request.data)
                    if not security[0]:
                        return fk.Response(security[1], status.HTTP_401_UNAUTHORIZED)
                    data = json.loads(fk.request.data)
                    try:
                        group = data.get("group", env.group)
                        system = data.get("system", env.system)
                        env.group = group
                        env.system = system
                        env.save()
                        return fk.Response('Environment edited', status.HTTP_200_OK)
                    except:
                        print(str(traceback.print_exc()))
                        return fk.Response(str(traceback.print_exc()), status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return fk.Response('No content provided for the update.', status.HTTP_204_NO_CONTENT)
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/public/env/view/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_env_view(env_id):
    logTraffic(CLOUD_URL, endpoint='/public/env/view/<env_id>')
    if fk.request.method == 'GET':
        try:
            env = EnvironmentModel.objects.with_id(env_id)            
        except:
            env = None
            print(str(traceback.print_exc()))
        if env is None:
            return fk.Response('Unable to find this environment.', status.HTTP_404_NOT_FOUND)
        else:
            return fk.Response(env.to_json(), mimetype='application/json')
    else:
        return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)