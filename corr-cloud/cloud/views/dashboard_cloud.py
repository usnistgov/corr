from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from corrdb.common.models import UserModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import DiffModel
from corrdb.common.models import RecordModel
from corrdb.common.models import FileModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
import flask as fk
from cloud import app, cloud_response, storage_manager, access_manager, CLOUD_URL, MODE, VIEW_HOST, VIEW_PORT
import datetime
import simplejson as json
import traceback
import mimetypes

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/search', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def private_search(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/search')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/search')
            if fk.request.args:
                query = fk.request.args.get("query").split(' ') #single word for now.
                users = []
                for user in UserModel.objects():
                    profile = ProfileModel.objects(user=user)[0]
                    where = []
                    if "!all" in query:
                        where.append("all")
                    if any(q.lower() in str(user.id) for q in query):
                        where.append("id")
                    if any(q.lower() in user.email.lower() for q in query):
                        where.append("email")
                    if any(q.lower() in profile.fname.lower() for q in query):
                        where.append("fname")
                    if any(q.lower() in profile.lname.lower() for q in query):
                        where.append("lname")
                    if any(q.lower() in profile.organisation.lower() for q in query):
                        where.append("organisation")
                    if any(q.lower() in profile.about.lower() for q in query):
                        where.append("about")
                    if len(where) != 0:
                        users.append({"created":str(user.created_at),"id":str(user.id), "email":user.email, "name":"{0} {1}".format(profile.fname, profile.lname), "organisation":profile.organisation, "about":profile.about, "apps": user.info()['total_apps'], "projects":user.info()['total_projects'], "records":user.info()['total_records']})
                applications = []
                for appli in ApplicationModel.objects():
                    where = []
                    if "!all" in query:
                        where.append("all")
                    if any(q.lower() in str(appli.id) for q in query):
                        where.append("id")
                    if any(q.lower() in appli.name.lower() for q in query):
                        where.append("name")
                    if any(q.lower() in appli.about.lower() for q in query):
                        where.append("about")
                    if len(where) != 0:
                        applications.append(appli.extended())
                projects = []
                records = []
                #scape the records issue.
                for project in ProjectModel.objects():
                    print(project.name)
                    if project.access == 'private' or project.access == 'public' or (project.access != 'public' and current_user == project.owner):
                        where_project = []
                        if "!all" in query:
                            where_project.append("all")
                        if any(q.lower() in str(project.id) for q in query):
                            where_project.append("id")
                        if any(q.lower() in project.name.lower() for q in query):
                            where_project.append("name")
                        if any(q.lower() in project.goals.lower() for q in query):
                            where_project.append("goals")
                        if any(q.lower() in project.description.lower() for q in query):
                            where_project.append("description")
                        if any(q.lower() in project.group.lower() for q in query):
                            where_project.append("group")

                        if len(where_project) != 0:
                            projects.append(project.extended())
                        
                        for record in RecordModel.objects(project=project):
                            if record.access == 'private' or record.access == 'public' or (record.project.access != 'public' and current_user == record.project.owner):
                                body = record.body
                                where_record = []

                                if "!all" in query:
                                    where_record.append("all")
                                if any(q.lower() in str(record.id) for q in query):
                                    where_record.append("id")
                                if record.label and any(q.lower() in record.label.lower() for q in query):
                                    where_record.append("label")
                                if record.system and any(q.lower() in str(json.dumps(record.system)).lower() for q in query):
                                    where_record.append("system")
                                if record.execution and any(q.lower() in str(json.dumps(record.execution)).lower() for q in query):
                                    where_record.append("execution")
                                if record.inputs and any(q.lower() in str(json.dumps(record.inputs)).lower() for q in query):
                                    where_record.append("inputs")
                                if record.outputs and any(q.lower() in str(json.dumps(record.outputs)).lower() for q in query):
                                    where_record.append("outputs")
                                if record.dependencies and any(q.lower() in str(json.dumps(record.dependencies)).lower() for q in query):
                                    where_record.append("dependencies")
                                if record.status and any(q.lower() in record.status.lower() for q in query):
                                    where_record.append("status")
                                # data contains so much info that most key words are bringing records too.
                                # if any(q.lower() in str(json.dumps(body.data)).lower() for q in query):
                                #     where_record.append("data")
                                if len(where_record) != 0:
                                    records.append(json.loads(record.summary_json()))

                diffs = []
                for diff in DiffModel.objects():
                    if (diff.record_from.access == 'private' or diff.record_to.access == 'private') or (diff.record_from.access == 'public' and diff.record_to.access == 'public') or (diff.record_from.access != 'public' and current_user == diff.record_from.project.owner) or (diff.record_to.access != 'public' and current_user == diff.record_to.project.owner):
                        where = []
                        if "!all" in query:
                            where.append("all")
                        if any(q.lower() in str(diff.id) for q in query):
                            where.append("id")
                        if any(q in str(json.dumps(diff.method)) for q in query):
                            where.append("method")
                        if any(q in str(json.dumps(diff.proposition)) for q in query):
                            where.append("proposition")
                        if any(q in str(json.dumps(diff.status)) for q in query):
                            where.append("status")
                        if any(q in str(json.dumps(diff.comments)) for q in query):
                            where.append("comments")

                        if len(where) != 0:
                            diffs.append({"id":str(diff.id), "created":str(diff.created_at), "from":diff.record_from.info(), "to":diff.record_to.info(), "sender":diff.sender.info(), "targeted":diff.targeted.info(), "proposition":diff.proposition, "method":diff.method, "status":diff.status, "comments":len(diff.comments)})
                
                envs = []
                for env in EnvironmentModel.objects():
                    where = []
                    if "!all" in query:
                        where.append("all")
                    if any(q.lower() in str(env.id) for q in query):
                        where.append("id")
                    if any(q in str(json.dumps(env.group)) for q in query):
                        where.append("group")
                    if any(q in str(json.dumps(env.system)) for q in query):
                        where.append("system")
                    if any(q in str(json.dumps(env.comments)) for q in query):
                        where.append("comments")

                    if len(where) != 0:
                        envs.append(env.info())
                return fk.Response(json.dumps({'users':{'count':len(users), 'result':users}, 'applications':{'count':len(applications), 'result':applications}, 'projects':{'count':len(projects), 'result':projects}, 'records':{'count':len(records), 'result':records}, 'diffs':{'count':len(diffs), 'result':diffs}, 'envs':{'count':len(envs), 'result':envs}}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def project_dashboard(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/projects')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/projects')
            
            projects = ProjectModel.objects(owner=current_user).order_by('+created_at')
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            summaries = []
            for p in projects:
                summaries.append(json.loads(p.activity_json()))
            return fk.Response(json.dumps({'version':version, 'number':len(summaries), 'projects':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/diffs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def diffs_dashboard(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/diffs')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/diffs')
            
            diffs_send = DiffModel.objects(sender=current_user).order_by('+created_at')
            diffs_targ = DiffModel.objects(targeted=current_user).order_by('+created_at')
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            summaries = []
            for d in diffs_send:
                if project_id == "all":
                    summaries.append(d.info())
                elif str(d.record_from.project.id) == project_id or str(d.record_to.project.id) == project_id:
                    summaries.append(d.info())
            for d in diffs_targ:
                if d not in diffs_send:
                    if project_id == "all":
                        summaries.append(d.info())
                    elif str(d.record_from.project.id) == project_id or str(d.record_to.project.id) == project_id:
                        summaries.append(d.info())

            return fk.Response(json.dumps({'number':len(summaries), 'diffs':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def dashboard_records(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/records/<project_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/records/<project_id>')
            if project_id == "all":
                projects = ProjectModel.objects(owner=current_user)
                records = {'size':0, 'records':[]}
                for project in projects:
                    for r in project.records:
                        records['records'].append(json.loads(r.summary_json()))
                records['size'] = len(records['records'])
                return fk.Response(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                project = ProjectModel.objects.with_id(project_id)
                if project ==  None or (project != None and project.owner != current_user and project.access != 'public'):
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    print(str(project.activity_json()))
                    return fk.Response(project.activity_json(), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/envs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def dashboard_envs(hash_session, project_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/envs/<project_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/envs/<project_id>')
            if project_id == "all":
                projects = ProjectModel.objects(owner=current_user)
                envs = {'size':0, 'envs':[]}
                for project in projects:
                    for env in project.envs:
                        envs['envs'].append(env.info())
                envs['size'] = len(envs['envs'])
                return fk.Response(json.dumps(envs, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                project = ProjectModel.objects.with_id(project_id)
                if project ==  None or (project != None and project.owner != current_user and project.access != 'public'):
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    envs = {'size':0, 'envs':[]}
                    for env in project.envs:
                        envs['envs'].append(env.info())
                    envs['size'] = len(envs['envs'])
                    return fk.Response(json.dumps(envs, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/record/diff/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def record_diff(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/record/diff/<record_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/record/diff/<record_id>')
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if (record.project.owner == current_user) or record.access == 'public':
                    diffs = []
                    founds = DiffModel.objects(record_from=record)
                    if founds != None:
                        for diff in founds:
                            diffs.append(diff.info())
                    founds = DiffModel.objects(record_to=record)
                    if founds != None:
                        for diff in founds:
                            diffs.append(diff.info())  
                    record_info = record.info()
                    record_info['diffs'] = diffs          
                    return fk.Response(json.dumps(record_info, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/reproducibility/assess/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def reproducibility_assess(hash_session, record_id):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/reproducibility/assess/<record_id>')
    if fk.request.method == 'GET':
        access_resp = access_manager.check_cloud(hash_session)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/<hash_session>/dashboard/reproducibility/assess/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if request.args:
                    if record.project.owner == current_user or record.access == 'public':
                        repeated = request.args.get('repeated', False)
                        reproduced = request.args.get('reproduced', False)
                        non_repeated = request.args.get('non-repeated', False)
                        non_reproduced = request.args.get('non-reproduced', False)
                        undefined = request.args.get('undefined', False)

                        repeats = []
                        n_repeats = []
                        reprods = []
                        n_reprods = []
                        undefs = []

                        diffs = []
                        diffs.extend(DiffModel.objects(record_from=record))
                        diffs.extend(DiffModel.objects(record_to=record))

                        for diff in diffs:
                            if diff.status == "agreed": #Only agreed for now.
                                if repeated and diff.proposition == "repeated":
                                    repeats.append(diff)
                                if non_repeated and diff.proposition == "non-repeated":
                                    n_repeats.append(diff)
                                if reproduced and diff.proposition == "reproduced":
                                    reprods.append(diff)
                                if non_reproduced and diff.proposition == "non-reproduced":
                                    n_reprods.append(diff)
                                if undefined and diff.proposition == "undefined":
                                    undefs.append(diff)
                        results = {"total":len(repeats)+len(n_repeats)+len(reprods)+len(n_reprods)+len(undefs)}
                        results["repeated"] = {"total":len(repeats), "diffs":[json.loads(d.to_json()) for d in repeats]}
                        results["non-repeated"] = {"total":len(n_repeats), "diffs":[json.loads(d.to_json()) for d in n_repeats]}
                        results["reproduced"] = {"total":len(reprods), "diffs":[json.loads(d.to_json()) for d in reprods]}
                        results["non-reproduced"] = {"total":len(n_reprods), "diffs":[json.loads(d.to_json()) for d in n_reprods]}
                        results["undefined"] = {"total":len(undefs), "diffs":[json.loads(d.to_json()) for d in undefs]}

                        return fk.Response(json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                    else:
                        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    return fk.redirect('{0}:{1}/error/?code=415'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))      


### Public access

@app.route(CLOUD_URL + '/public/dashboard/search', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_search():
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/search')
    if fk.request.method == 'GET':
        if fk.request.args:
            query = fk.request.args.get("query").split(" ") #single word for now.
            users = []
            for user in UserModel.objects():
                profile = ProfileModel.objects(user=user)
                where = []
                if query in user.email:
                    where.append("email")
                if query in profile.fname:
                    where.append("fname")
                if query in profile.lname:
                    where.append("lname")
                if query in profile.organisation:
                    where.append("organisation")
                if query in profile.about:
                    where.append("about")
                if len(where) != 0:
                    users.append({"id":str(user.id), "email":user.email, "fname":profile.fname, "lname":profile.lname, "organisation":profile.organisation, "about":profile.about})
            projects = []
            records = []
            for project in ProjectModel.objects():
                if project.access == 'public':
                    where_project = []
                    if query in project.name:
                        where_project.append("name")
                    if query in project.goals:
                        where_project.append("goals")
                    if query in project.description:
                        where_project.append("description")
                    if query in project.group:
                        where_project.append("group")

                    if len(where_project) != 0:
                        projects.append({"user":str(project.owner.id), "id":str(project.id), "name":project.name, "created":str(project.created_at), "duration":str(project.duration)})
                    
                    for record in RecordModel.objects(project=project):
                        if record.access == 'public':
                            body = record.body
                            where_record = []
                            
                            if query in record.label:
                                where_record.append("label")
                            if query in str(json.dumps(record.system)):
                                where_record.append("system")
                            if query in str(json.dumps(record.program)):
                                where_record.append("program")
                            if query in str(json.dumps(record.inputs)):
                                where_record.append("inputs")
                            if query in str(json.dumps(record.outputs)):
                                where_record.append("outputs")
                            if query in str(json.dumps(record.dependencies)):
                                where_record.append("dependencies")
                            if query in record.status:
                                where_record.append("status")
                            if query in str(json.dumps(body.data)):
                                where_record.append("data")

                            if len(where_record) != 0:
                                records.append({"user":str(record.project.owner.id), "project":str(record.project.id), "id":str(record.id), "label":record.label, "created":str(record.created_at), "status":record.status})

            diffs = []
            for diff in DiffModel.objects():
                if diff.record_from.access == 'public' and diff.record_to.access == 'public':
                    where = []
                    if query in str(json.dumps(diff.diff)):
                        where.append("diff")
                    if query in diff.proposition:
                        where.append("proposition")
                    if query in diff.status:
                        where.append("status")
                    if query in str(json.dumps(diff.comments)):
                        where.append("comments")

                    if len(where) != 0:
                        diffs.append({"id":str(diff.id), "from":str(diff.record_from.id), "to":str(diff.record_to.id), "sender":str(diff.sender.id), "targeted":str(diff.targeted.id), "proposition":diff.proposition, "status":diff.status})
                
            return fk.Response(json.dumps({'users':{'count':len(users), 'result':users}, 'projects':{'count':len(projects), 'result':projects}, 'records':{'count':len(records), 'result':records}, 'diffs':{'count':len(diffs), 'result':diffs}}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=400'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))


@app.route(CLOUD_URL + '/public/dashboard/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_project_dashboard():
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/projects')
    if fk.request.method == 'GET':
        projects = ProjectModel.objects.order_by('+created_at')
        summaries = []
        for p in projects:
            if project.access == 'public':
                project = {"project":json.loads(p.summary_json())}
                records = []
                for r in RecordModel.objects(project=p):
                    if r.access == 'public':
                        records.append(r)
                project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                summaries.append(project)
        return fk.Response(json.dumps({'number':len(summaries), 'projects':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_dashboard_records(project_id):
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/records/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p.access == 'public':
            project = {"project":json.loads(p.summary_json())}
            records = RecordModel.objects(project=p)
            records_object = []
            for record in records:
                if record.access == 'public':
                    record_object = {"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)}
                    diffs = []
                    founds = DiffModel.objects(record_from=record)
                    if founds != None:
                        for diff in founds:
                            diffs.append(diff.info())
                    founds = DiffModel.objects(record_to=record)
                    if founds != None:
                        for diff in founds:
                            diffs.append(diff.info()) 

                    record_object['diffs'] = len(diffs)
                    records_object.append(record_object)

            project["activity"] = {"number":len(records), "records":records_object}
            return fk.Response(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  


@app.route(CLOUD_URL + '/public/dashboard/record/diff/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def public_record_diff(record_id):
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/record/diff/<record_id>')
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print(str(traceback.print_exc()))
        if record is None:
            return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
        else:
            if record.access == 'public':
                diffs = []
                founds = DiffModel.objects(record_from=record)
                if founds != None:
                    for diff in founds:
                        diffs.append(diff.info())
                founds = DiffModel.objects(record_to=record)
                if founds != None:
                    for diff in founds:
                        diffs.append(diff.info())  
                record_info = record.info()
                record_info['diffs'] = diffs          
                return fk.Response(json.dumps(record_info, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/traffic/api', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def traffic_api():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="api")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/traffic/cloud', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def traffic_cloud():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="cloud")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/apps', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_all(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/apps')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            apps = ApplicationModel.objects(developer=current_user)
            apps_json = {'total_apps':len(apps), 'apps':[]}
            for application in apps:
                apps_json['apps'].append(application.extended())
            return cloud_response(200, 'Developers applications', apps_json)
        else:
            return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/app/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_create(hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/app/create')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                data = json.loads(fk.request.data)
                name = data.get('name', '')
                about = data.get('about', '')
                logo_storage = '{0}:{1}/images/gearsIcon.png'.format(VIEW_HOST, VIEW_PORT)
                access = 'activated'
                network = '0.0.0.0'
                visibile = False
                developer = current_user
                logo_encoding = ''
                logo_mimetype = mimetypes.guess_type(logo_storage)[0]
                logo_buffer = storage_manager.web_get_file(logo_storage)
                logo_size = logo_buffer.tell()
                logo_description = 'This is the default image used for applications logos.'
                logo_name = '{0}-logo.png'.format(name)
                logo_location = 'remote'
                logo_group = 'logo'
                
                logo, logo_created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), encoding=logo_encoding, name=logo_name, mimetype=logo_mimetype, size=logo_size, storage=logo_storage, location=logo_location, group=logo_group, description=logo_description)
                app, created = ApplicationModel.objects.get_or_create(developer=developer, name=name, about=about, logo=logo, access=access, network=network, visibile=visibile)
                if not created:
                    return fk.Response('Application already exists.', status.HTTP_403_FORBIDDEN)
                    return cloud_response(200, 'Application already exists', app.info())
                else:
                    logStat(application=app)
                    return cloud_response(201, 'Application created', app.info())
            else:
                return fk.Response('No content provided for this creation.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/app/show/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_show(app_id, hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/app/show/<app_id>')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return fk.Response('Unable to find this application.', status.HTTP_404_NOT_FOUND)
            else:
                return cloud_response(200, 'Application %s'%app.name, app.extended())
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/app/remove/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_remove(app_id, hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/app/remove/<app_id>')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
    else:
        if fk.request.method in ['GET', 'DELETE']:
            appli = ApplicationModel.objects.with_id(app_id)
            if appli == None:
                return fk.Response('Unable to find this application.', status.HTTP_404_NOT_FOUND)
            elif appli.developer != current_user:
                return fk.Response('Unauthorized action on this application.', status.HTTP_401_UNAUTHORIZED)
            else:
                # if app.logo.location == 'local':
                #     storage_manager.storage_delete_file('logo', app.logo.location)
                # app.logo.delete()
                appli.delete()
                logStat(deleted=True, application=appli)
                return cloud_response(200, 'Deletion succeeded', 'The application %s was succesfully deleted.'%app.name)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/app/update/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_update(app_id, hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/app/update/<app_id>')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'POST':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return fk.Response('Unable to find this application.', status.HTTP_404_NOT_FOUND)
            elif app.developer != current_user:
                return fk.Response('Unauthorized action on this application.', status.HTTP_401_UNAUTHORIZED)
            else:
                if fk.request.data:
                    data = json.loads(fk.request.data)
                    name = data.get('name', app.name)
                    about = data.get('about', app.about)
                    logo_storage = data.get('logo', None)
                    access = data.get('access', app.access)
                    if access == "":
                        access = app.access
                    network = data.get('network', app.network)
                    visibile = data.get('visibile', app.visibile)
                    logo = app.logo
                    developer = current_user
                    # I should think of ways to keep this logo section clean.
                    # Normaly i should be able to upload a new logo with the file endpoint.
                    # It is supposed to figure all the stuff below out.
                    if logo_storage != None:
                        logo_encoding = ''
                        logo_mimetype = mimetypes.guess_type(logo_storage)[0]

                        if 'http://' in logo_storage or 'https://' in logo_storage:
                            logo_buffer = storage_manager.web_get_file(logo.storage)
                            if logo_buffer != None:
                                logo_size = logo_buffer.tell()
                                logo_name = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_storage = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_location = 'remote'
                                logo_group = 'logo'
                                logo_description = 'This is the application %s logo.'%name
                                if app.logo.location == 'local':
                                    storage_manager.storage_delete_file('logo', app.logo.storage)
                                logo.name = logo_name
                                logo.mimetype=logo_mimetype
                                logo.size=logo_size
                                logo.storage=logo_storage
                                logo.location=logo_location
                                logo.group=logo_group
                                logo.description=logo_description
                                logo.save()
                    app.developer = developer
                    app.name = name
                    app.access = access
                    app.about = about
                    app.network = network
                    app.visibile = visibile
                    app.save()
                    return cloud_response(201, 'Application updated', app.info())
                else:
                    return fk.Response('No content provided for the update.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/<hash_session>/dashboard/developer/app/logo/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def app_logo(app_id, hash_session):
    logTraffic(CLOUD_URL, endpoint='/private/<hash_session>/dashboard/developer/app/logo/<app_id>')
    access_resp = access_manager.check_cloud(hash_session)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app != None:
                name = app.name if app.name != '' and app.name != None else 'unknown'
                logo = app.logo
                if logo.location == 'local' and 'http://' not in logo.storage and 'https://' not in logo.storage:
                    logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                    if logo_buffer == None:
                        return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                elif logo.location == 'remote':
                    logo_buffer = storage_manager.web_get_file(logo.storage)
                    if logo_buffer != None:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        if logo_buffer == None:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    # solve the file situation and return the appropriate one.
                    if 'http://' in logo.storage or 'https://' in logo.storage:
                        logo.location = 'remote'
                        logo.save()
                        logo_buffer = storage_manager.web_get_file(logo.storage)
                        if logo_buffer != None:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                        else:
                            logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                            if logo_buffer == None:
                                return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                            else:
                                return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo.location = 'local'
                        logo.save()
                        logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                        if logo_buffer == None:
                            return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            else:
                return fk.redirect('{0}:{1}/error/?code=404'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))
