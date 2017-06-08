from corrdb.common import logAccess, logStat, logTraffic, crossdomain, basicAuthSession
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
from flask.ext.api import status
import flask as fk
from cloud import app, cloud_response, storage_manager, access_manager, processRequest, queryResponseDict, CLOUD_URL, MODE, VIEW_HOST, VIEW_PORT, ACC_SEC, CNT_SEC
import datetime
import simplejson as json
import traceback
import mimetypes

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

# Query language that follows reference relationship in models.
# ![val1,val2,...] => looking for these values (empty means all).
# ?[mod1,mod2,...] => looking in models (all means all) (>|<|>=|<=modX.fieldY)
# ~ at end => include models and models depending on them
# none => only models that depends on them. 
# | => pipe the result of the precedent to another query. ? is not accepted here
# & => adding another query as a separate one to merge their results.
# There is no or because these are enoug. we are not working on conditionals.
# I have to prove that this is enough for query in this case.

# TODO:
# Make it include more operations: < > ==
# Make it more human like.

@app.route(CLOUD_URL + '/private/dashboard/search', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def private_search():
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/search')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/search')
            if fk.request.args:
                _request = ""
                for key, value in fk.request.args.items():
                    if key == "req":
                        _request = "{0}".format(value)
                    else:
                        _request = "{0}&{1}{2}".format(_request, key, value)
                if not any(el in _request for el in ["[", "]", "!", "?", "|", "&"]):
                    _request = "![{0}]?[]".format(_request)
                message, contexts = processRequest(_request)
                if contexts is None:
                    return cloud_response(500, 'Error processing the query', message)
                else:
                    users = []
                    applications = []
                    projects = []
                    records = []
                    envs = []
                    diffs = []
                    for context_index in range(len(contexts)):
                        context = contexts[context_index]
                        user_filter = []
                        for user in context["user"]:
                            if user.email not in user_filter:
                                user_filter.append(user.email)
                                profile = ProfileModel.objects(user=user)[0]
                                users.append({"created":str(user.created_at),"id":str(user.id), "email":user.email, "name":"{0} {1}".format(profile.fname, profile.lname), "organisation":profile.organisation, "about":profile.about, "apps": user.info()['total_apps'], "projects":user.info()['total_projects'], "records":user.info()['total_records']})
                        for profile in context["profile"]:
                            if profile.user.email not in user_filter:
                                user_filter.append(profile.user.email)
                                user = profile.user
                                users.append({"created":str(user.created_at),"id":str(user.id), "email":user.email, "name":"{0} {1}".format(profile.fname, profile.lname), "organisation":profile.organisation, "about":profile.about, "apps": user.info()['total_apps'], "projects":user.info()['total_projects'], "records":user.info()['total_records']})
                        for appli in context["tool"]:
                            skip = False
                            for cn_i in range(context_index):
                                if appli in contexts[cn_i]["tool"]:
                                    skip = True
                                    break
                            if not skip:
                                applications.append(appli.extended())
                        for project in context["project"]:
                            skip = False
                            for cn_i in range(context_index):
                                if project in contexts[cn_i]["project"]:
                                    skip = True
                                    break
                            if not skip:
                                if project.access == 'public' or current_user == project.owner or current_user.group == "admin":
                                    projects.append(project.extended())
                        for record in context["record"]:
                            skip = False
                            for cn_i in range(context_index):
                                if record in contexts[cn_i]["record"]:
                                    skip = True
                                    break
                            if not skip:
                                if record.access == 'public' or current_user == record.project.owner or current_user.group == "admin":
                                    records.append(json.loads(record.summary_json()))
                        for env in context["env"]:
                            skip = False
                            for cn_i in range(context_index):
                                if env in contexts[cn_i]["env"]:
                                    skip = True
                                    break
                            if not skip:
                                for project in ProjectModel.objects():
                                    if str(env.id) in project.history:
                                        if project.access == 'public' or current_user == project.owner or current_user.group == "admin":
                                            envs.append(env.info())
                                        break
                        for diff in context["diff"]:
                            skip = False
                            for cn_i in range(context_index):
                                if diff in contexts[cn_i]["diff"]:
                                    skip = True
                                    break
                            if not skip:
                                if current_user.group == "admin" or (diff.record_from.access == 'public' and diff.record_to.access == 'public') or current_user == diff.record_from.project.owner or current_user == diff.record_to.project.owner:
                                    diffs.append({"id":str(diff.id), "created":str(diff.created_at), "from":diff.record_from.info(), "to":diff.record_to.info(), "sender":diff.sender.info(), "targeted":diff.targeted.info(), "proposition":diff.proposition, "method":diff.method, "status":diff.status, "comments":len(diff.comments)})
                    response = {}
                    response['users'] = {'count':len(users), 'result':users}
                    response['applications'] = {'count':len(applications), 'result':applications}
                    response['projects'] = {'count':len(projects), 'result':projects}
                    response['envs'] = {'count':len(envs), 'result':envs}
                    response['records'] = {'count':len(records), 'result':records}
                    response['diffs'] = {'count':len(diffs), 'result':diffs}
                    return cloud_response(200, message, response)
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def project_dashboard():
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/projects')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/projects')
            
            if current_user.group == "admin":
                projects = ProjectModel.objects().order_by('+created_at')
            else:
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
            block_size = 45
            end = block_size
            if fk.request.args:
                page = int(fk.request.args.get("page"))
                begin = int(page)*block_size
                if int(page) == 0 and len(summaries) <= block_size:
                    # end = -1
                    pass
                else:
                    if begin >= len(summaries):
                        end = -1
                        summaries = []
                    else:
                        if len(summaries) - begin >= block_size:
                            end = int(page)*block_size + block_size
                        else:
                            end = len(summaries)
                        summaries = summaries[begin:end]
            return fk.Response(json.dumps({'end':end, 'version':version, 'number':len(summaries), 'projects':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/users', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def users_dashboard():
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/users')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/users')
            
            if current_user.group == "admin":
                users = UserModel.objects().order_by('+created_at')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            summaries = []
            for u in users:
                if u != current_user:
                    profile = ProfileModel.objects(user=u).first()
                    user_info = {}
                    user_info["created"] = str(u.created_at)
                    user_info["id"] = str(u.id)
                    user_info["auth"] = u.auth
                    user_info["group"] = u.group
                    user_info["email"] = u.email
                    user_info["max-quota"] = u.max_quota
                    user_info["usage"] = round(100*u.quota/(u.max_quota*1024*1024*1024), 2)
                    user_info["fname"] = profile.fname
                    user_info["lname"] = profile.lname
                    user_info["org"] = profile.organisation
                    user_info["about"] = profile.about
                    user_info["apps"] = u.info()['total_apps']
                    user_info["projects"] = u.info()['total_projects']
                    user_info["records"] = u.info()['total_records']
                    summaries.append(user_info)
            block_size = 45
            end = block_size
            if fk.request.args:
                page = int(fk.request.args.get("page"))
                begin = int(page)*block_size
                if int(page) == 0 and len(summaries) <= block_size:
                    # end = -1
                    pass
                else:
                    if begin >= len(summaries):
                        end = -1
                        summaries = []
                    else:
                        if len(summaries) - begin >= block_size:
                            end = int(page)*block_size + block_size
                        else:
                            end = len(summaries)
                        summaries = summaries[begin:end]
            return fk.Response(json.dumps({'end':end, 'version':version, 'number':len(summaries), 'users':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/diffs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def diffs_dashboard(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/diffs')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/diffs')
            version = 'N/A'
            try:
                from corrdb import __version__
                version = __version__
            except:
                pass
            summaries = []

            if current_user.group == "admin":
                diffs = DiffModel.objects().order_by('+created_at')
                for d in diffs:
                    if project_id == "all":
                        summaries.append(d.info())
                    elif str(d.record_from.project.id) == project_id or str(d.record_to.project.id) == project_id:
                        summaries.append(d.info())
            else:
                diffs_send = DiffModel.objects(sender=current_user).order_by('+created_at')
                diffs_targ = DiffModel.objects(targeted=current_user).order_by('+created_at')
                
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
            block_size = 45
            end = block_size
            if fk.request.args:
                page = int(fk.request.args.get("page"))
                begin = int(page)*block_size
                if int(page) == 0 and len(summaries) <= block_size:
                    # end = -1
                    pass
                else:
                    if begin >= len(summaries):
                        end = -1
                        summaries = []
                    else:
                        if len(summaries) - begin >= block_size:
                            end = int(page)*block_size + block_size
                        else:
                            end = len(summaries)
                        summaries = summaries[begin:end]
            return fk.Response(json.dumps({'end':end, 'number':len(summaries), 'diffs':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def dashboard_records(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/records/<project_id>')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/records/<project_id>')
            if project_id == "all":
                if current_user.group == "admin":
                    projects = ProjectModel.objects()
                else:
                    projects = ProjectModel.objects(owner=current_user)
                records = {'size':0, 'records':[]}
                for project in projects:
                    for r in project.records:
                        records['records'].append(json.loads(r.summary_json()))
                block_size = 45
                end = -1
                if fk.request.args:
                    page = fk.request.args.get("page")
                    begin = int(page) * block_size
                    if int(page) == 0 and len(records['records']) <= block_size:
                        end = -1
                    else:
                        if begin > len(records['records']):
                            end = -1
                            records = []
                        else:
                            if len(records['records']) >= begin + block_size:
                                end = begin + block_size
                            else:
                                end = len(records['records'])
                            records = records['records'][begin, end]
                records['end'] = end 
                records['size'] = len(records['records'])
                return fk.Response(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                project = ProjectModel.objects.with_id(project_id)
                if project ==  None or (project != None and project.owner != current_user and project.access != 'public' and current_user.group != "admin"):
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    # print(str(project.activity_json()))
                    if fk.request.args:
                        return fk.Response(project.activity_json(page=fk.request.args.get("page")), mimetype='application/json')
                    else:
                        return fk.Response(project.activity_json(), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

@app.route(CLOUD_URL + '/private/dashboard/envs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def dashboard_envs(project_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/envs/<project_id>')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is None:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/envs/<project_id>')
            if project_id == "all":
                if current_user.group == "admin":
                    projects = ProjectModel.objects()
                else:
                    projects = ProjectModel.objects(owner=current_user)
                envs = {'size':0, 'envs':[]}

                for project in projects:
                    for env_id in project.history:
                        env = EnvironmentModel.objects.with_id(env_id)
                        env_info = env.info()
                        env["project"] = project.info()
                        envs['envs'].append(env_info)
                block_size = 45
                end = block_size
                if fk.request.args:
                    page = int(fk.request.args.get("page"))
                    begin = int(page)*block_size
                    if int(page) == 0 and len(envs['envs']) <= block_size:
                        # end = -1
                        pass
                    else:
                        if begin >= len(envs['envs']):
                            end = -1
                            envs['envs'] = []
                        else:
                            if len(envs['envs']) - begin >= block_size:
                                end = int(page)*block_size + block_size
                            else:
                                end = len(envs['envs'])
                            envs['envs'] = envs['envs'][begin:end]
                envs['end'] = end
                envs['size'] = len(envs['envs'])
                return fk.Response(json.dumps(envs, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                project = ProjectModel.objects.with_id(project_id)
                if project ==  None or (project != None and project.owner != current_user and project.access != 'public' and current_user.group != "admin"):
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
                else:
                    envs = {'size':0, 'envs':[]}
                    for env_id in project.history:
                        env = EnvironmentModel.objects.with_id(env_id)
                        env_info = env.info()
                        env_info['project'] = project.info()
                        envs['envs'].append(env_info)
                    block_size = 45
                    end = block_size
                    if fk.request.args:
                        page = int(fk.request.args.get("page"))
                        begin = int(page)*block_size
                        if int(page) == 0 and len(envs['envs']) <= block_size:
                            # end = -1
                            pass
                        else:
                            if begin >= len(envs['envs']):
                                end = -1
                                envs['envs'] = []
                            else:
                                if len(envs['envs']) - begin >= block_size:
                                    end = int(page)*block_size + block_size
                                else:
                                    end = len(envs['envs'])
                                envs['envs'] = envs['envs'][begin:end]
                    envs['end'] = end
                    envs['size'] = len(envs['envs'])
                    return fk.Response(json.dumps(envs, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))  

@app.route(CLOUD_URL + '/private/dashboard/record/diff/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def record_diff(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/record/diff/<record_id>')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            logAccess(CLOUD_URL, 'cloud', '/private/dashboard/record/diff/<record_id>')
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if (record.project.owner == current_user) or record.access == 'public' or current_user.group == "admin":
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
                    block_size = 45
                    end = block_size
                    if fk.request.args:
                        page = int(fk.request.args.get("page"))
                        begin = int(page)*block_size
                        if int(page) == 0 and len(record_info['diffs']) <= block_size:
                            # end = -1
                            pass
                        else:
                            if begin >= len(record_info['diffs']):
                                end = -1
                                record_info['diffs'] = []
                            else:
                                if len(record_info['diffs']) - begin >= block_size:
                                    end = int(page)*block_size + block_size
                                else:
                                    end = len(record_info['diffs'])
                                record_info['diffs'] = record_info['diffs'][begin:end]
                    record_info['end'] = end         
                    return fk.Response(json.dumps(record_info, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
                else:
                    return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/reproducibility/assess/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def reproducibility_assess(record_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/reproducibility/assess/<record_id>')
    if fk.request.method == 'GET':
        hash_session = basicAuthSession(fk.request)
        access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
        current_user = access_resp[1]
        if current_user is not None:
            try:
                logAccess(CLOUD_URL, 'cloud', '/private/dashboard/reproducibility/assess/<record_id>')
                record = RecordModel.objects.with_id(record_id)
            except:
                print(str(traceback.print_exc()))
            if record is None:
                return fk.redirect('{0}:{1}/error/?code=204'.format(VIEW_HOST, VIEW_PORT))
            else:
                if request.args:
                    if record.project.owner == current_user or record.access == 'public' or current_user.group == "admin":
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

@app.route(CLOUD_URL + '/public/dashboard/search', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_search():
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/search')
    if fk.request.method == 'GET':
        logAccess(CLOUD_URL, 'cloud', '/public/dashboard/search')
        if fk.request.args:
            _request = ""
            page = 0
            for key, value in fk.request.args.items():
                if key == "req":
                    _request = "{0}".format(value)
                elif key == "page":
                    page = int(value)
                else:
                    _request = "{0}&{1}{2}".format(_request, key, value)
            if not any(el in _request for el in ["[", "]", "!", "?", "|", "&"]):
                _request = "![{0}]?[]".format(_request)
            message, contexts = processRequest(_request)
            if contexts is None:
                return cloud_response(500, 'Error processing the query', message)
            else:
                users = []
                applications = []
                projects = []
                records = []
                envs = []
                diffs = []
                for context_index in range(len(contexts)):
                    context = contexts[context_index]
                    user_filter = []
                    for user in context["user"]:
                        if user.email not in user_filter:
                            user_filter.append(user.email)
                            profile = ProfileModel.objects(user=user)[0]
                            users.append({"created":str(user.created_at),"id":str(user.id), "email":user.email, "name":"{0} {1}".format(profile.fname, profile.lname), "organisation":profile.organisation, "about":profile.about, "apps": user.info()['total_apps'], "projects":user.info()['total_projects'], "records":user.info()['total_records']})
                    for profile in context["profile"]:
                        if profile.user.email not in user_filter:
                            user_filter.append(profile.user.email)
                            user = profile.user
                            users.append({"created":str(user.created_at),"id":str(user.id), "email":user.email, "name":"{0} {1}".format(profile.fname, profile.lname), "organisation":profile.organisation, "about":profile.about, "apps": user.info()['total_apps'], "projects":user.info()['total_projects'], "records":user.info()['total_records']})
                    for appli in context["tool"]:
                        skip = False
                        for cn_i in range(context_index):
                            if appli in contexts[cn_i]["tool"]:
                                skip = True
                                break
                        if not skip:
                            applications.append(appli.extended())
                    for project in context["project"]:
                        skip = False
                        for cn_i in range(context_index):
                            if project in contexts[cn_i]["project"]:
                                skip = True
                                break
                        if not skip:
                            if project.access == 'public':
                                projects.append(project.extended())
                    for record in context["record"]:
                        skip = False
                        for cn_i in range(context_index):
                            if record in contexts[cn_i]["record"]:
                                skip = True
                                break
                        if not skip:
                            if record.access == 'public':
                                records.append(json.loads(record.summary_json()))
                    for env in context["env"]:
                        skip = False
                        for cn_i in range(context_index):
                            if env in contexts[cn_i]["env"]:
                                skip = True
                                break
                        if not skip:
                            for project in ProjectModel.objects():
                                if str(env.id) in project.history:
                                    if project.access == 'public':
                                        envs.append(env.info())
                                    break
                    for diff in context["diff"]:
                        skip = False
                        for cn_i in range(context_index):
                            if diff in contexts[cn_i]["diff"]:
                                skip = True
                                break
                        if not skip:
                            if (diff.record_from.access == 'public' and diff.record_to.access == 'public'):
                                diffs.append({"id":str(diff.id), "created":str(diff.created_at), "from":diff.record_from.info(), "to":diff.record_to.info(), "sender":diff.sender.info(), "targeted":diff.targeted.info(), "proposition":diff.proposition, "method":diff.method, "status":diff.status, "comments":len(diff.comments)})
                response = {}
                response['users'] = {'count':len(users), 'result':users}
                response['applications'] = {'count':len(applications), 'result':applications}
                response['projects'] = {'count':len(projects), 'result':projects}
                response['envs'] = {'count':len(envs), 'result':envs}
                response['records'] = {'count':len(records), 'result':records}
                response['diffs'] = {'count':len(diffs), 'result':diffs}
                return cloud_response(200, message, response)
        else:
            return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))


@app.route(CLOUD_URL + '/public/dashboard/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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
        block_size = 45
        end = block_size
        if fk.request.args:
            page = int(fk.request.args.get("page"))
            begin = int(page)*block_size
            if int(page) == 0 and len(summaries) <= block_size:
                # end = -1
                pass
            else:
                if begin >= len(summaries):
                    end = -1
                    summaries = []
                else:
                    if len(summaries) - begin >= block_size:
                        end = int(page)*block_size + block_size
                    else:
                        end = len(summaries)
                    summaries = summaries[begin:end]
        return fk.Response(json.dumps({'end':end, 'number':len(summaries), 'projects':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_dashboard_records(project_id):
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/records/<project_id>')
    if fk.request.method == 'GET':
        p = ProjectModel.objects.with_id(project_id)
        if p.access == 'public':
            project = {"project":json.loads(p.summary_json())}
            records = RecordModel.objects(project=p)
            records_object = []
            end = -1
            block_size = 45
            if fk.request.args:
                page = fk.request.args.get("page")
                begin = int(page) * block_size
                if int(page) == 0 and len(records) <= block_size:
                    end = -1
                else:
                    if begin > len(records):
                        end = -1
                        records = []
                    else:
                        if len(records) >= begin + block_size:
                            end = begin + block_size
                        else:
                            end = len(records)
                        records = records[begin, end]
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


@app.route(CLOUD_URL + '/public/dashboard/record/diff/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
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
                block_size = 45
                end = block_size
                if fk.request.args:
                    page = int(fk.request.args.get("page"))
                    begin = int(page)*block_size
                    if int(page) == 0 and len(record_info['diffs']) <= block_size:
                        # end = -1
                        pass
                    else:
                        if begin >= len(record_info['diffs']):
                            end = -1
                            record_info['diffs'] = []
                        else:
                            if len(record_info['diffs']) - begin >= block_size:
                                end = int(page)*block_size + block_size
                            else:
                                end = len(record_info['diffs'])
                            record_info['diffs'] = record_info['diffs'][begin:end]  
                record_info['end'] = end        
                return fk.Response(json.dumps(record_info, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/traffic/api', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def traffic_api():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="api")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/public/dashboard/traffic/cloud', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def traffic_cloud():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="cloud")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/developer/apps', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_all():
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/apps')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            # Show all the apps for now. Only admin can create them anyways.
            apps = ApplicationModel.objects()
            # if current_user.group == "admin":
            #     apps = ApplicationModel.objects()
            # else:
            #     apps = ApplicationModel.objects(developer=current_user)
            apps_json = {'total_apps':len(apps), 'apps':[]}
            for application in apps:
                apps_json['apps'].append(application.extended())
            return cloud_response(200, 'Developers tools', apps_json)
        else:
            return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))

@app.route(CLOUD_URL + '/private/dashboard/developer/app/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_create():
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/create')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
    else:
        if current_user.group != "admin":
            return fk.Response('Only admins can now create tools.', status.HTTP_401_UNAUTHORIZED)
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
                    logo_description = 'This is the default image used for tools logos.'
                    logo_name = '{0}-logo.png'.format(name)
                    logo_location = 'remote'
                    logo_group = 'logo'
                    
                    query_app = ApplicationModel.objects(developer=developer, name=name).first()
                    if query_app:
                        return fk.Response('Tool already exists.', status.HTTP_403_FORBIDDEN)
                    else:
                        logo, logo_created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), encoding=logo_encoding, name=logo_name, mimetype=logo_mimetype, size=logo_size, storage=logo_storage, location=logo_location, group=logo_group, description=logo_description)
                        app, created = ApplicationModel.objects.get_or_create(developer=developer, name=name, about=about, logo=logo, access=access, network=network, visibile=visibile)
                        if not created:
                            return fk.Response('For some reason the tool was not created. Try again later.', status.HTTP_500_INTERNAL_SERVER_ERROR)
                        else:
                            logStat(application=app)
                            return cloud_response(201, 'Tool created', app.extended())
                else:
                    return fk.Response('No content provided for this creation.', status.HTTP_204_NO_CONTENT)
            else:
                return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/dashboard/developer/app/show/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_show(app_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/show/<app_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return fk.Response('Unable to find this tool.', status.HTTP_404_NOT_FOUND)
            else:
                return cloud_response(200, 'Tool %s'%app.name, app.extended())
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/dashboard/developer/app/retoken/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_retoken(app_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/retoken/<app_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return fk.Response('Unable to find this tool.', status.HTTP_404_NOT_FOUND)
            else:
                app.retoken();
                return fk.Response(app.api_token, status.HTTP_200_OK)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/dashboard/developer/app/remove/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_remove(app_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/remove/<app_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.Response('Unauthorized action on this endpoint.', status.HTTP_401_UNAUTHORIZED)
    else:
        if fk.request.method in ['GET', 'DELETE']:
            appli = ApplicationModel.objects.with_id(app_id)
            if appli == None:
                return fk.Response('Unable to find this tool.', status.HTTP_404_NOT_FOUND)
            elif appli.developer != current_user and current_user.group != "admin":
                return fk.Response('Unauthorized action on this tool.', status.HTTP_401_UNAUTHORIZED)
            else:
                # if app.logo.location == 'local':
                #     storage_manager.storage_delete_file('logo', app.logo.location)
                # app.logo.delete()
                appli.delete()
                logStat(deleted=True, application=appli)
                return cloud_response(200, 'Deletion succeeded', 'The tool %s was succesfully deleted.'%app.name)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/dashboard/developer/app/update/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_update(app_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/update/<app_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
    current_user = access_resp[1]
    if current_user is None:
        return fk.redirect('{0}:{1}/error/?code=401'.format(VIEW_HOST, VIEW_PORT))
    else:
        if fk.request.method == 'POST':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return fk.Response('Unable to find this tool.', status.HTTP_404_NOT_FOUND)
            # elif app.developer != current_user or current_user.group != "admin":
            elif current_user.group != "admin":
                return fk.Response('Unauthorized action on this tool.', status.HTTP_401_UNAUTHORIZED)
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
                    return cloud_response(201, 'Tool updated', app.info())
                else:
                    return fk.Response('No content provided for the update.', status.HTTP_204_NO_CONTENT)
        else:
            return fk.Response('Endpoint does not support this HTTP method.', status.HTTP_405_METHOD_NOT_ALLOWED)

@app.route(CLOUD_URL + '/private/dashboard/developer/app/logo/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def app_logo(app_id):
    logTraffic(CLOUD_URL, endpoint='/private/dashboard/developer/app/logo/<app_id>')
    hash_session = basicAuthSession(fk.request)
    access_resp = access_manager.check_cloud(hash_session, ACC_SEC, CNT_SEC)
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


@app.route(CLOUD_URL + '/public/dashboard/query', methods=['GET','POST','PUT','UPDATE','DELETE','POST', 'OPTIONS'])
@crossdomain(fk=fk, app=app, origin='*')
def public_query_dashboard():
    logTraffic(CLOUD_URL, endpoint='/public/dashboard/projects')
    if fk.request.method == 'GET':
        _request = ""
        for key, value in fk.request.args.items():
            if key == "req":
                _request = "{0}".format(value)
            else:
                _request = "{0}&{1}{2}".format(_request, key, value)
        message, context = processRequest(_request)
        return cloud_response(200, message, queryResponseDict(context))
    else:
        return fk.redirect('{0}:{1}/error/?code=405'.format(VIEW_HOST, VIEW_PORT))