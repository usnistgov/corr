from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from corrdb.common.models import UserModel
from corrdb.common.models import ApplicationModel
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

@app.route(CLOUD_URL + '/private/<hash_session>/env/remove/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def env_remove(hash_session, env_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/env/remove/<env_id>')     
    if fk.request.method in ['GET', 'DELETE']:
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/env/remove/<env_id>')
                env = EnvironmentModel.objects.with_id(env_id)
            except:
                print(str(traceback.print_exc()))
            if env is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                result = storage_manager.delete_env_files(env)
                if result:
                    logStat(deleted=True, env=env)
                    env.delete()
                return fk.redirect('{0}:{1}/dashboard/?session={2}&view=envs&project=all'.format(VIEW_HOST, VIEW_PORT, hash_session))
    else:
       return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT)) 


@app.route(CLOUD_URL + '/private/<hash_session>/env/view/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def env_view(hash_session, env_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/env/view/<env_id>')
    if fk.request.method == 'GET':
        caccess_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/env/view/<env_id>')
                env = EnvironmentModel.objects.with_id(env_id)
            except:
                print(str(traceback.print_exc()))
            if env is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                return fk.Response(env.to_json(), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))      

@app.route(CLOUD_URL + '/private/<hash_session>/env/create/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def env_create(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/env/create/<record_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/env/create/<record_id>')
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return cloud_response(404, 'Environment not created.', "The record referenced is unknown.")
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    try:
                        env = EnvironmentModel(created_at=str(datetime.datetime.utcnow()))
                        application_id = data.get("app", None)
                        if application_id:
                            application = ApplicationModel.objects.with_id(application_id)
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
                        record.project.history.append(str(env.id))
                        record.project.save()
                        record.environment = env
                        record.save()
                        return cloud_response(201, 'Environment successfully created.', "The environment was created.")
                    except:
                        print(str(traceback.print_exc()))
                        return cloud_response(500, 'environment not created.', str(traceback.print_exc()))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/env/edit/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def env_edit(hash_session, env_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/env/edit/<env_id>')
    if fk.request.method == 'POST':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            try:
                env = EnvironmentModel.objects.with_id(env_id)
            except:
                print(str(traceback.print_exc()))
            if env is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if fk.request.data:
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
                        return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))