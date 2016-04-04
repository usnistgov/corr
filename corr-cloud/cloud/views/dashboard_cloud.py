from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import DiffModel
from corrdb.common.models import RecordModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from flask.ext.stormpath import user
from flask.ext.stormpath import login_required
import flask as fk
from cloud import app, stormpath_manager, crossdomain, CLOUD_URL
import datetime
import json
import traceback

#Only redirects to pages that signify the state of the problem or the result.
#The API will return some json response at all times. 
#I will handle my own status and head and content and stamp

@app.route(CLOUD_URL + '/<hash_session>/dashboard/search', methods=['GET'])
@crossdomain(origin='*')
def private_search(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/dashboard/search")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                if fk.request.args:
                    query = fk.request.args.get("query").split(' ') #single word for now.
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
                        if project.access == 'public' or (project.access != 'public' and current_user == project.owner):
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
                                if record.access == 'public' or (record.project.access != 'public' and current_user == record.project.owner):
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
                        if (diff.record_from.access == 'public' and diff.record_to.access == 'public') or (diff.record_from.access != 'public' and current_user == diff.record_from.project.owner) or (diff.record_to.access != 'public' and current_user == diff.record_to.project.owner):
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
                    # return fk.redirect('http://0.0.0.0:5000/error-400/')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/dashboard/projects', methods=['GET'])
@crossdomain(origin='*')
def project_dashboard(hash_session):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/dashboard/projects")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                projects = ProjectModel.objects(owner=current_user).order_by('+created_at')
                summaries = []
                for p in projects:
                    project = {"project":json.loads(p.summary_json())}
                    records = RecordModel.objects(project=p)
                    project["activity"] = {"number":len(records), "records":[{"id":str(record.id), "created":str(record.created_at), "updated":str(record.updated_at), "status":str(record.status)} for record in records]}
                    summaries.append(project)
                return fk.Response(json.dumps({'number':len(summaries), 'projects':summaries}, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/dashboard/records/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def dashboard_records(hash_session, project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/dashboard/records/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is None:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_denied')
        else:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                p = ProjectModel.objects.with_id(project_id)
                project = {"project":json.loads(p.summary_json())}
                records = RecordModel.objects(project=p)
                records_object = []
                for record in records:
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
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')  


@app.route(CLOUD_URL + '/<hash_session>/dashboard/record/diff/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def record_diff(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/dashboard/record/diff/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            allowance = current_user.allowed("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
            print "Allowance: "+allowance
            if allowance == hash_session:
                try:
                    record = RecordModel.objects.with_id(record_id)
                except:
                    print str(traceback.print_exc())
                if record is None:
                    return fk.redirect('http://0.0.0.0:5000/error-204/')
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
                        return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
            else:
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/<hash_session>/dashboard/reproducibility/assess/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def reproducibility_assess(hash_session, record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/private/dashboard/reproducibility/assess/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        current_user = UserModel.objects(session=hash_session).first()
        print fk.request.path
        if current_user is not None:
            try:
                record = RecordModel.objects.with_id(record_id)
            except:
                print str(traceback.print_exc())
            if record is None:
                return fk.redirect('http://0.0.0.0:5000/error-204/')
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
                        return fk.redirect('http://0.0.0.0:5000/error-401/?action=repeats_failed')
                else:
                    return fk.redirect('http://0.0.0.0:5000/error-415/')
        else:
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=view_denied')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')      


### Public access

@app.route(CLOUD_URL + '/public/dashboard/search', methods=['GET'])
@crossdomain(origin='*')
def public_search():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/dashboard/search")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
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
            return fk.redirect('http://0.0.0.0:5000/error-400/')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')


@app.route(CLOUD_URL + '/public/dashboard/projects', methods=['GET'])
@crossdomain(origin='*')
def public_project_dashboard():
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/dashboard/projects")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
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
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/dashboard/records/<project_id>', methods=['GET'])
@crossdomain(origin='*')
def public_dashboard_records(project_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/dashboard/records/<project_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
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
            return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')  


@app.route(CLOUD_URL + '/public/dashboard/record/diff/<record_id>', methods=['GET'])
@crossdomain(origin='*')
def public_record_diff(record_id):
    (traffic, created) = TrafficModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), service="cloud", endpoint="/public/dashboard/record/diff/<record_id>")
    if not created:
        traffic.interactions += 1 
        traffic.save()
        
    if fk.request.method == 'GET':
        try:
            record = RecordModel.objects.with_id(record_id)
        except:
            print str(traceback.print_exc())
        if record is None:
            return fk.redirect('http://0.0.0.0:5000/error-204/')
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
                return fk.redirect('http://0.0.0.0:5000/error-401/?action=dashboard_failed')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/dashboard/traffic/api', methods=['GET'])
@crossdomain(origin='*')
def traffic_api():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="api")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')

@app.route(CLOUD_URL + '/public/dashboard/traffic/cloud', methods=['GET'])
@crossdomain(origin='*')
def traffic_cloud():
    if fk.request.method == 'GET':
        api_traffics = TrafficModel.objects(service="cloud")
        return fk.Response(json.dumps([json.loads(traffic.to_json()) for traffic in api_traffics], sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')
    else:
        return fk.redirect('http://0.0.0.0:5000/error-405/')