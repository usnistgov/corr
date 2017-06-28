import json

from flask.ext.api import status
import flask as fk

from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from api import app, storage_manager, access_manager, secure_content ,API_URL, api_response, data_pop, merge_dicts
from corrdb.common.models import UserModel
from corrdb.common.models import AccessModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import FileModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import StatModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import RecordModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import DiffModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import CommentModel
from corrdb.common.models import MessageModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import BundleModel
from corrdb.common.models import VersionModel

import mimetypes
import simplejson as json
import traceback
import datetime
import random
import string
import os
import _thread

@app.route(API_URL + '/admin/<api_token>/search/<key_words>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_search(api_token, key_words):
    logTraffic(API_URL, endpoint='/admin/<api_token>/search/<key_words>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        logAccess(API_URL,'api', '/admin/<api_token>/search/<key_words>')
        if fk.request.method == 'GET':
            results = {'results':{}, 'total-results':0}
            results['results']['users'] = {'users-list':[], 'users-total':0}
            results['results']['apps'] = {'apps-list':[], 'apps-total':0}
            results['results']['projects'] = {'projects-list':[], 'projects-total':0}
            results['results']['records'] = {'records-list':[], 'records-total':0}
            results['results']['envs'] = {'envs-list':[], 'envs-total':0}
            results['results']['bundles'] = {'bundles-list':[], 'bundles-total':0}
            results['results']['files'] = {'files-list':[], 'files-total':0}
            results['results']['versions'] = {'versions-list':[], 'versions-total':0}

            words = key_words.split('-')

            for user in UserModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                profile = ProfileModel.objects(user=user).first()
                index = 0
                for word in words:
                    if word != '':
                        if profile != None:
                            try:
                                if word.lower() in user.email.lower():
                                    exists[index] = True
                            except:
                                pass
                            try:
                                if word.lower() in profile.fname.lower():
                                    exists[index] = True
                            except:
                                pass
                            try:
                                if word.lower() in profile.lname.lower():
                                    exists[index] = True
                            except:
                                pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['users']['users-list'].append({'user':user.info(), 'profile':profile.info()})
                results['results']['users']['users-total'] = len(results['results']['users']['users-list'])

            for app in ApplicationModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in app.possible_access.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in app.network.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in app.storage.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in app.about.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in app.name.lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['apps']['apps-list'].append(app.info())
                results['results']['apps']['apps-total'] = len(results['results']['apps']['apps-list'])

            for project in ProjectModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in project.name.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.description.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.goals.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(project.tags).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.access.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in project.group.lower():
                                exists[index] = True
                        except:
                            pass
                        
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['projects']['projects-list'].append(project.info())
                results['results']['projects']['projects-total'] = len(results['results']['projects']['projects-list'])

            for record in RecordModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in record.label.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.tags).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.system).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.execution).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.preparation).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.inputs).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.outputs).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.dependencies).lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in record.status.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in record.access.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(record.rationels).lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['records']['records-list'].append(record.info())
                results['results']['records']['records-total'] = len(results['results']['records']['records-list'])

            for env in EnvironmentModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in env.group.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in env.system.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in str(env.specifics).lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['envs']['envs-list'].append(env.info())
                results['results']['envs']['envs-total'] = len(results['results']['envs']['envs-list'])

            for bundle in BundleModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in bundle.scope.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in bundle.location.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in bundle.mimetype.lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['bundles']['bundles-list'].append(bundle.info())
                results['results']['bundles']['bundles-total'] = len(results['results']['bundles']['bundles-list'])

            for file_ in FileModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in file_.mimetype.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.name.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.path.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.storage.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.location.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.group.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in file_.description.lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['files']['files-list'].append(file_.info())
                results['results']['files']['files-total'] = len(results['results']['files']['files-list'])

            for version in VersionModel.objects():
                exists = [False for word in words]
                condition = [True for word in words]
                index = 0
                for word in words:
                    if word != '':
                        try:
                            if word.lower() in version.system.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in version.baseline.lower():
                                exists[index] = True
                        except:
                            pass
                        try:
                            if word.lower() in version.marker.lower():
                                exists[index] = True
                        except:
                            pass
                    else:
                        exists[index] = True
                    index += 1
                if exists == condition:
                    results['results']['versions']['versions-list'].append(app.info())
                results['results']['versions']['versions-total'] = len(results['results']['versions']['versions-list'])

            results['total-results'] += results['results']['users']['users-total']
            results['total-results'] += results['results']['apps']['apps-total']
            results['total-results'] += results['results']['projects']['projects-total']
            results['total-results'] += results['results']['records']['records-total']
            results['total-results'] += results['results']['envs']['envs-total']
            results['total-results'] += results['results']['bundles']['bundles-total']
            results['total-results'] += results['results']['files']['files-total']
            results['total-results'] += results['results']['versions']['versions-total']
            
            return api_response(200, 'Search results for: [%s]'%key_words, results)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# admin stuff
@app.route(API_URL + '/admin/<api_token>/stats', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_stats(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/stats')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            stats = StatModel.objects()
            stats_dict = {'total_stats':len(stats), 'stats':[]}
            for stat in stats:
                stats_dict['stats'].append(stat.extended())
            return api_response(200, 'CoRR stats', stats_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/stats/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_stats_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/stats/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            stats = StatModel.objects()
            for stat in stats:
                stat.delete()
            return api_response(200, 'CoRR stats clear', 'All the stats in CoRR have been cleared.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/traffic', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_traffic(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/traffic')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            traffics = TrafficModel.objects()
            traffics_dict = {'total_traffics':len(traffics), 'traffics':[]}
            for traffic in traffics:
                traffics_dict['traffics'].append(traffic.extended())
            return api_response(200, 'CoRR traffic', traffics_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/traffic/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_traffic_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            traffics = TrafficModel.objects()
            for traffic in traffics:
                traffic.delete() 
            return api_response(200, 'CoRR traffic cleared', 'All the traffic in CoRR have been cleared.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/access', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_access(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/access')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            accesses = AccessModel.objects()
            accesses_dict = {'total_accesses':len(accesses), 'accesses':[]}
            for access in accesses:
                accesses_dict['accesses'].append(access.extended())
            return api_response(200, 'CoRR access', accesses_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/comments', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comments(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comments')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            comments = CommentModel.objects()
            comments_json = {'total_comments':len(comments), 'comments':[]}
            for comment in comments:
                comments_json['comments'].append(comment.extended())
            return api_response(200, 'All comments', comments_json)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/comments/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comments_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comments/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            comments = CommentModel.objects()
            comments.delete()
            return api_response(200, 'All comments cleared', 'All comments deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


# admin comment
@app.route(API_URL + '/admin/<api_token>/comment/<group>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comment_send(group, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comment/<group>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                item_id = data.get('item', None)
                sender_id = data.get('sender', None)
                title = data.get('title', '')
                content = data.get('content', '')
                attachments = data.get('attachments', [])
                if item_id == None or sender_id == None:
                    return api_response(400, 'Missing mandatory fields', 'A comment creation requires an item and a sender.')
                if title == '' and content == '':
                    return api_response(400, 'Missing mandatory fields', 'A comment must contains at least a title or a content.')        
                item = None
                sender = None
                if group == 'project':
                    item = ProjectModel.objects.with_id(item_id)
                elif group == 'record':
                    item = RecordModel.objects.with_id(item_id)
                elif group == 'diff':
                    item = DiffModel.objects.with_id(item_id)
                elif group == 'env':
                    item = EnvironmentModel.objects.with_id(item_id)
                elif group == 'file':
                    item = FileModel.objects.with_id(item_id)
                else:
                    return api_response(405, 'Comment group not allow', 'Comments are only possible with: project, record, diff, env and file.')
                sender = UserModel.objects(session=sender_id).first()
                if item == None or sender == None:
                    return api_response(400, 'Missing mandatory fields', 'A comment creation requires a existing item and a existing sender.')
                comment, created = CommentModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), sender=sender, title=title, content=content)
                logStat(comment=comment)
                item.comments.append(str(comment.id))
                item.save()
                return api_response(200, 'Comment delivered', comment.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the comment information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/comment/all/<group>/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comment_all(group, item_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comment/<group>/<item_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            if item_id == None:
                return api_response(400, 'Missing mandatory fields', 'Listing all the comments of an item requires the item id.')
            item = None
            if group == 'project':
                item = ProjectModel.objects.with_id(item_id)
            elif group == 'record':
                item = RecordModel.objects.with_id(item_id)
            elif group == 'diff':
                item = DiffModel.objects.with_id(item_id)
            elif group == 'env':
                item = EnvironmentModel.objects.with_id(item_id)
            elif group == 'file':
                item = FileModel.objects.with_id(item_id)
            else:
                return api_response(405, 'Comment group not allowed', 'Comments are only possible with: project, record, diff, env and file.')
            if item == None:
                return api_response(400, 'Missing mandatory fields', 'This item does not exist. It is invalid to pull comments from an non existing item.')
            else:
                comments = [comment.extended() for comment in item._comments()]
                return api_response(200, '%s %s comments list'%(group, item_id), comments)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/comment/update/<comment_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comment_update(comment_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comment/update/<comment_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                comment = CommentModel.objects.with_id(comment_id)
                if comment == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this comment.')
                else:
                    comment.title = data.get('title', comment.title)
                    comment.content = data.get('content', comment.content)
                    comment.extend(data.get('attachments', []))
                    comment.save()
                    return api_response(200, 'comment %s updated'%comment_id, comment.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the information to update.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/comment/show/<comment_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comment_show(comment_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comment/show/<comment_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            comment = CommentModel.objects.with_id(comment_id)
            if comment == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this comment.')
            else:
                return api_response(200, 'Comment %s'%str(comment.id), comment.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/comment/delete/<comment_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_comment_delete(comment_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/comment/delete/<comment_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            comment = CommentModel.objects.with_id(comment_id)
            if comment == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this comment.')
            else:
                comment.delete()
                return api_response(200, 'Comment %s'%comment_id, 'All information about the comment was removed.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# admin developer apps
@app.route(API_URL + '/admin/<api_token>/apps', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_apps(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/apps')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            apps = ApplicationModel.objects()
            apps_json = {'total_apps':len(apps), 'apps':[]}
            for application in apps:
                apps_json['apps'].append(application.extended())
            return api_response(200, 'Developers applications', apps_json)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/app/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                developer_id = data.get('developer', '')
                name = data.get('name', '')
                if developer_id == '' or name == '':
                    return api_response(400, 'Missing mandatory fields', 'An application creation requires a developer and a name.')
                else:
                    about = data.get('about', '')
                    logo_storage = 'default-logo.png'
                    access = 'deactivated'
                    network = '0.0.0.0'
                    visibile = False
                    developer = UserModel.objects.with_id(developer_id)
                    logo_encoding = ''
                    logo_mimetype = mimetypes.guess_type(logo_storage)[0]
                    logo_buffer = storage_manager.storage_get_file('logo', logo_storage)
                    if logo_buffer != None:
                        old_file_position = logo_buffer.tell()
                        logo_buffer.seek(0, os.SEEK_END)
                        logo_size = logo_buffer.tell()
                        logo_buffer.seek(old_file_position, os.SEEK_SET)
                    else:
                        logo_size = 0
                    logo_name = 'default-logo.png'
                    logo_location = 'local'
                    logo_group = 'logo'
                    logo_description = 'This is the default image used for the application logo in case none is provided.'
                    
                    # if logo_storage == 'default-logo':
                    #     logo_buffer = storage_manager.storage_get_file('logo', logo_storage)
                    #     logo_size = logo_buffer.tell() if logo_buffer != None else 0
                    #     logo_name = 'Default application logo'
                    #     logo_storage = 'default-logo.png'
                    #     logo_location = 'local'
                    #     logo_group = 'logo'
                    #     logo_description = 'This is the default image used for the application logo in case none is provided.'
                        
                    # elif 'http://' in logo_storage:
                    #     logo_buffer = storage_manager.web_get_file(logo_storage)
                    #     logo_size = logo_buffer.tell() if logo_buffer != None else 0
                    #     logo_name = '%s logo'%name
                    #     logo_storage = logo_storage
                    #     logo_location = 'remote'
                    #     logo_group = 'logo'
                    #     logo_description = 'This is the application %s logo.'%name
                    # else:
                    #     logo_buffer = storage_manager.storage_get_file('logo', logo_storage)
                    #     logo_size = logo_buffer.tell() if logo_buffer != None else 0
                    #     logo_name = '%s logo'%name
                    #     logo_storage = logo_storage
                    #     logo_location = 'local'
                    #     logo_group = 'logo'
                    #     logo_description = 'This is the application %s logo.'%name
                    logo, logo_created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), encoding=logo_encoding, name=logo_name, mimetype=logo_mimetype, size=logo_size, storage=logo_storage, location=logo_location, group=logo_group, description=logo_description)
                    app, created = None, False
                    if developer == None or developer.group != 'developer':
                        return api_response(400, 'A field is not applicable', 'The application user has to be a developer.')
                    # elif logo == None:
                    #     app, created = ApplicationModel.objects.get_or_create(developer=developer, name=name, about=about, access=access, network=network, visibile=visibile)
                    else:
                        app, created = ApplicationModel.objects.get_or_create(developer=developer, name=name, about=about, logo=logo, access=access, network=network, visibile=visibile)
                    if not created:
                        return api_response(200, 'Application already exists', app.info())
                    else:
                        logStat(application=app)
                        return api_response(201, 'Application created', app.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the application information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/app/show/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_show(app_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/show/<app_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
            else:
                return api_response(200, 'Application %s'%app.name, app.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/app/delete/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_delete(app_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/delete/<app_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
            else:
                if app.logo.location == 'local':
                    storage_manager.storage_delete_file('logo', app.logo.location)
                app.logo.delete()
                app.delete()
                logStat(deleted=True, application=application)
                return api_response(200, 'Deletion succeeded', 'The application %s was succesfully deleted.'%app.name)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/app/delete/all', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_delete_all(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/delete/all')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            apps = ApplicationModel.objects
            apps.delete()
            return api_response(200, 'Deletion succeeded', 'All the apps were succesfully deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/admin/<api_token>/app/update/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_update(app_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/update/<app_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            app = ApplicationModel.objects.with_id(app_id)
            if app == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)

                    developer_id = data.get('developer', None)
                    name = data.get('name', app.name)
                    about = data.get('about', app.about)
                    logo_storage = data.get('logo', None)
                    access = data.get('access', app.access)
                    network = data.get('network', app.network)
                    visibile = data.get('visibile', app.visibile)
                    logo = app.logo
                    developer = None
                    if developer_id == None:
                        developer = app.developer
                    else:
                        developer = UserModel.objects.with_id(developer_id)
                        if developer_id == None:
                            developer = app.developer
                    if developer.group != 'developer':
                        return api_response(400, 'A field is not applicable', 'The application user has to be a developer.')
                    else:
                        # I should think of ways to keep this logo section clean.
                        # Normaly i should be able to upload a new logo with the file endpoint.
                        # It is supposed to figure all the stuff below out.
                        if logo_storage != None:
                            logo_encoding = ''
                            logo_mimetype = mimetypes.guess_type(logo_storage)[0]
                            
                            if logo_storage == 'default-logo.png':
                                logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                                # logo_size = logo_buffer.tell() if logo_buffer != None else 0
                                logo_name = 'default-logo.png'
                                logo_storage = 'default-logo.png'
                                logo_location = 'local'
                                logo_group = 'logo'
                                logo_description = 'This is the default image used for the application logo in case none is provided.'
                                
                            elif 'http://' in logo_storage:
                                logo_buffer = storage_manager.web_get_file(logo.storage)
                                # logo_size = logo_buffer.tell() if logo_buffer != None else 0
                                logo_name = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_storage = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_location = 'remote'
                                logo_group = 'logo'
                                logo_description = 'This is the application %s logo.'%name
                            else:
                                # Do not use this one to update the logo.
                                # Not recommended.
                                logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                                # logo_size = logo_buffer.tell() if logo_buffer != None else 0
                                logo_name = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_storage = '%s_%s'%(str(app.logo.id), logo_buffer.filename)
                                logo_location = 'local'
                                logo_group = 'logo'
                                logo_description = 'This is the application %s logo.'%name
                            if logo_buffer != None:
                                old_file_position = logo_buffer.tell()
                                logo_buffer.seek(0, os.SEEK_END)
                                logo_size = logo_buffer.tell()
                                logo_buffer.seek(old_file_position, os.SEEK_SET)
                            else:
                                logo_size = 0
                            if app.logo.storage != 'default-logo.png' and 'http://' not in app.logo.storage:
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
                        return api_response(201, 'Application updated', app.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the application information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/app/logo/<app_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_app_logo(app_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/app/logo/<app_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            app = ApplicationModel.objects.with_id(app_id)
            if app != None:
                name = app.name if app.name != '' and app.name != None else 'unknown'
                logo = app.logo
                if logo.location == 'local' and 'http://' not in logo.storage:
                    logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at [%s].'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                elif logo.location == 'remote':
                    logo_buffer = storage_manager.web_get_file(logo.storage)
                    if logo_buffer != None:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    # solve the file situation and return the appropriate one.
                    if 'http://' in logo.storage:
                        logo.location = 'remote'
                        logo.save()
                        logo_buffer = storage_manager.web_get_file(logo.storage)
                        if logo_buffer != None:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                        else:
                            logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                            if logo_buffer == None:
                                return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                            else:
                                return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo.location = 'local'
                        logo.save()
                        logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            else:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

### admin users
@app.route(API_URL + '/admin/<api_token>/users', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_users(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/users')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            users = UserModel.objects()
            users_dict = {'total_users':len(users), 'users':[]}
            for user in users:
                users_dict['users'].append(user.extended())
            return api_response(200, 'Users list', users_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/profiles/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_profiles_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/profiles/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            profiles = ProfileModel.objects()
            profiles.delete()
            return api_response(200, 'Profiles cleared', 'All the profiles have been deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


#@TODO
# @app.route(API_URL + '/admin/<api_token>/user/home', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

@app.route(API_URL + '/admin/<api_token>/user/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                email = data.get('email', '')
                pswd1 = data.get('password', None)
                pswd2 = data.get('passwordAgain', None)
                group = data.get('group', 'unknown')
                if email == '' or pswd1 == None or pswd2 == None :
                    return api_response(400, 'Missing mandatory fields', 'A user creation should have at least an email and two identical password.')
                elif (pswd1 != None or pswd2 != None) and pswd1 != pswd2:
                    return api_response(400, 'Mismatching requirement', 'password and passwordAgain should be equal.')
                else:
                    # Add stormpath to test the link for password handling.
                    user, created = UserModel.objects.get_or_create(email=email, group=group)
                    if not created:
                        return api_response(302, 'User already exists', user.info())
                    else:
                        logStat(user=user)
                        ProfileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), user=user, fname='', lname='', organisation='', about='')

                        return api_response(201, 'User account created', user.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/login', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_login(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/login')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                email = data.get('email', '')
                pswd1 = data.get('password', None)
                pswd2 = data.get('passwordAgain', None)
                if email == '' or pswd1 == None or pswd2 == None :
                    return api_response(400, 'Missing mandatory fields', 'A user login should have at least an email and two identical password.')
                elif (pswd1 != None or pswd2 != None) and pswd1 != pswd2:
                    return api_response(400, 'Mismatching requirement', 'password and passwordAgain should be equal.')
                else:
                    # Add stormpath to test the link for password handling.
                    user = UserModel.objects(email=email).first()
                    if user == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to find this user account.')
                    else:
                        user.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                        return api_response(201, 'User account login succeeded', user.extended())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/token/update/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_token_update(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/token/update/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                if user.allowed() != session_id:
                    return api_response(401, 'Unauthorized access', 'This session is not authorized.')
                else:
                    user.retoken()
                    return api_response(200, 'User %s token updated'%user.email, user.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/logout/<session_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_logout(session_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/logout/<session_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects(session=session_id).first()
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                if user.allowed() != session_id:
                    return api_response(401, 'Unauthorized access', 'This session is not authorized.')
                else:
                    s=string.lowercase+string.digits
                    user.renew(''.join(random.sample(s,25)))
                    return api_response(200, 'User %s logged out'%user.email, 'The session is terminated.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/password/lost', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_password_lost(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/password/lost')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                email = data.get('email', '')
                if email == '':
                    return api_response(400, 'Missing mandatory field', 'A user password recovery requires the user email address.')
                else:
                    # Add stormpath to test the link for password handling.
                    user = UserModel.objects(email=email).first()
                    if user == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to find this user account.')
                    else:
                        user.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                        # Send an email
                        link = 'http://localhost:5100/user/session/recover/%s'%user.session
                        return api_response(200, 'Recovery session link.', 'The user acces his account at %s and change his password rigth away.'%link)
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/session/recover/<session_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_session_recover(session_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/session/recover/<session_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects(session=session_id).first()
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                if user.session != session_id:
                    return api_response(401, 'Unauthorized access', 'This recovery session is not authorized.')
                else:
                    user.renew("%s%s"%(fk.request.headers.get('User-Agent'),fk.request.remote_addr))
                    return fk.redirect('http://localhost:5100/?session=%s'%user.session)
                    # return api_response(200, 'User %s session redirection to account page'%user.email, 'The user is authorized to access his account')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/profile/create/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_profile_create(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/profile/create/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user account.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)
                    fname = data.get('fname', '')
                    lname = data.get('lname', '')
                    picture_storage = 'default-picture.png'
                    organisation = data.get('organisation', '')
                    about = data.get('about', '')
                    picture_encoding = ''
                    picture_mimetype = mimetypes.guess_type(picture_storage)[0]
                    picture_buffer = storage_manager.storage_get_file('picture', picture_storage)
                    if picture_buffer != None:
                        old_file_position = picture_buffer.tell()
                        picture_buffer.seek(0, os.SEEK_END)
                        picture_size = picture_buffer.tell()
                        picture_buffer.seek(old_file_position, os.SEEK_SET)
                    else:
                        picture_size = 0
                    picture_name = 'default-picture.png'
                    picture_location = 'local'
                    picture_group = 'picture'
                    picture_description = 'This is the default image used for the user profile picture in case none is provided.'
                        

                    # if picture_storage == 'default-picture':
                    #     picture_buffer = storage_manager.storage_get_file('picture', picture_storage)
                    #     picture_size = picture_buffer.tell() if picture_buffer != None else 0
                    #     picture_name = 'Default user picture'
                    #     picture_storage = 'default-picture.png'
                    #     picture_location = 'local'
                    #     picture_group = 'picture'
                    #     picture_description = 'This is the default image used for the user profile picture in case none is provided.'
                        
                    # elif 'http://' in picture_storage:
                    #     picture_buffer = storage_manager.web_get_file(picture_storage)
                    #     picture_size = picture_buffer.tell() if picture_buffer != None else 0
                    #     picture_name = '%s picture'%fname
                    #     picture_storage = picture_storage
                    #     picture_location = 'remote'
                    #     picture_group = 'picture'
                    #     picture_description = 'This is the user %s profile picture.'%fname
                    # else:
                    #     picture_buffer = storage_manager.storage_get_file('picture', picture_storage)
                    #     picture_size = picture_buffer.tell() if picture_buffer != None else 0
                    #     picture_name = '%s picture'%fname
                    #     picture_storage = picture_storage
                    #     picture_location = 'local'
                    #     picture_group = 'picture'
                    #     picture_description = 'This is the user %s profile picture.'%fname
                    picture, picture_created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), encoding=picture_encoding, name=picture_name, mimetype=picture_mimetype, size=picture_size, storage=picture_storage, location=picture_location, group=picture_group, description=picture_description)
                    profile, created = None, False
                    if picture == None:
                        profile, created = ProfileModel.objects.get_or_create(user=user, fname=fname, lname=lname, organisation=organisation, about=about)
                    else:
                        profile, created = ProfileModel.objects.get_or_create(user=user, fname=fname, lname=lname, picture=picture, organisation=organisation, about=about)
                    if not created:
                        return api_response(200, 'Profile already exists', profile.info())
                    else:
                        return api_response(201, 'Profile created', profile.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the profile information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/show/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_show(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/show/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                return api_response(200, 'User %s account'%user.email, user.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/profile/show/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_profile_show(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/profile/show/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                profile = ProfileModel.objects(user=user).first()
                if profile == None:
                    return api_response(404, 'User %s profile is empty'%user.email, 'You have to create a profile for this user.')
                else:
                    return api_response(200, 'User %s profile'%user.email, profile.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/delete/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_delete(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/delete/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                profile = ProfileModel.objects(user=user)
                if profile != None:
                    if profile.picture.location == 'local':
                        storage_manager.storage_delete_file('picture', profile.picture.location)
                profile.picture.delete()
                profile.delete()
                logStat(deleted=True, user=user)
                return api_response(200, 'Deletion succeeded', 'The user %s was succesfully deleted.'%user.email)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/user/update/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_update(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/update/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)
                    email = data.get('email', user.email)
                    pswd1 = data.get('password', None)
                    pswd2 = data.get('passwordAgain', None)
                    group = data.get('group', user.group)
                    if pswd1 == None or pswd2 == None or (pswd1 == pswd2 and pswd1 != None, api_token):
                        return api_response(404, 'Mismatching requirement', 'password and passwordAgain should be equal when provided.')
                    else:
                        user.email = email
                        user.group = group
                        user.save()
                    return api_response(201, 'User account updated', user.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the user information you want to update.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/profile/update/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_profile_update(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/profile/update/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            user = UserModel.objects.with_id(user_id)
            if user == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
            else:
                profile = ProfileModel.objects(user=user).first()
                if profile == None:
                    return api_response(404, 'User %s profile is empty'%user.email, 'You have to create a profile for this user.')
                else:
                    if fk.request.data:
                        secure_content(fk.request.data)
                        data = json.loads(fk.request.data)
                        user_id_new = data.get('user', None)
                        fname = data.get('fname', profile.fname)
                        lname = data.get('lname', profile.lname)
                        picture_storage = data.get('picture', None)
                        organisation = data.get('organisation', profile.organisation)
                        about = data.get('about', profile.about)
                        picture = profile.picture
                        new_user = None
                        if user_id_new == None:
                            new_user = profile.user
                        else:
                            new_user = UserModel.objects.with_id(user_id_new)
                            if user_id_new == None:
                                new_user = profile.user
                        if picture_storage != None:
                            picture_encoding = ''
                            picture_mimetype = mimetypes.guess_type(picture_storage)[0]
                            if picture_storage == 'default-picture.png':
                                picture_buffer = storage_manager.storage_get_file('picture', picture_storage)
                                # picture_size = picture_buffer.tell() if picture_buffer != None else 0
                                picture_name = 'default-picture.png'
                                picture_storage = 'default-picture.png'
                                picture_location = 'local'
                                picture_group = 'picture'
                                picture_description = 'This is the default image used for the user profile picture in case none is provided.'
                                
                            elif 'http://' in picture_storage:
                                picture_buffer = storage_manager.web_get_file(picture_storage)
                                # picture_size = picture_buffer.tell() if picture_buffer != None else 0
                                picture_name = '%s_%s'%(str(profile.picture.id), picture_buffer.filename)
                                picture_storage = '%s_%s'%(str(profile.picture.id), picture_buffer.filename)
                                picture_location = 'remote'
                                picture_group = 'picture'
                                picture_description = 'This is the user %s profile picture.'%fname
                            else:
                                picture_buffer = storage_manager.storage_get_file('picture', picture_storage)
                                # picture_size = picture_buffer.tell() if picture_buffer != None else 0
                                picture_name = '%s_%s'%(str(profile.picture.id), picture_buffer.filename)
                                picture_storage = '%s_%s'%(str(profile.picture.id), picture_buffer.filename)
                                picture_location = 'local'
                                picture_group = 'picture'
                                picture_description = 'This is the user %s profile picture.'%fname
                            if picture_buffer != None:
                                old_file_position = picture_buffer.tell()
                                picture_buffer.seek(0, os.SEEK_END)
                                picture_size = picture_buffer.tell()
                                picture_buffer.seek(old_file_position, os.SEEK_SET)
                            else:
                                picture_size = 0
                            # picture, picture_created = FileModel.objects.get_or_create(encoding=picture_encoding, name=picture_name, mimetype=picture_mimetype, size=picture_size, storage=picture_storage, location=picture_location, group=picture_group, description=picture_description)
                            if profile.picture.storage != 'default-picture.png' and 'http://' not in profile.picture.storage:
                                storage_manager.storage_delete_file('picture', profile.picture.storage)
                            picture.name = picture_name
                            picture.mimetype=picture_mimetype
                            picture.size=picture_size
                            picture.storage=picture_storage
                            picture.location=picture_location
                            picture.group=picture_group
                            picture.description=picture_description
                            picture.save()
                        profile.user = new_user
                        profile.fname = fname
                        profile.lname = lname
                        profile.organisation = organisation
                        profile.about = about
                        profile.save()
                        return api_response(201, 'User profile updated', profile.info())
                    else:
                        return api_response(204, 'Nothing created', 'You must provide the user information you want to update.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/user/picture/<user_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_user_picture(user_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/user/picture/<user_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            user = UserModel.objects.with_id(user_id)
            if user != None:
                profile = ProfileModel.objects(user=user).first()
                if profile == None:
                    picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                    if picture_buffer == None:
                        return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                    else:
                        return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                else:
                    picture = profile.picture
                    if picture == None:
                        picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                        if picture_buffer == None:
                            return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                        else:
                            return fk.send_file(picture_buffer, attachment_filename='default-picture.png', mimetype='image/png')
                    elif picture.location == 'local' and 'http://' not in picture.storage:
                        picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                        if picture_buffer == None:
                            return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%logo.storage)
                        else:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    elif picture.location == 'remote':
                        picture_buffer = storage_manager.web_get_file(picture.storage)
                        if picture_buffer != None:
                            return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                            if picture_buffer == None:
                                return api_response(404, 'No picture found', 'We could not fetch the picture [default-picture.png].')
                            else:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                    else:
                        # solve the file situation and return the appropriate one.
                        if 'http://' in picture.storage:
                            picture.location = 'remote'
                            picture.save()
                            picture_buffer = storage_manager.web_get_file(picture.storage)
                            if picture_buffer != None:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                            else:
                                picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                                if picture_buffer == None:
                                    return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                                else:
                                    return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
                        else:
                            picture.location = 'local'
                            picture.save()
                            picture_buffer = storage_manager.storage_get_file('picture', picture.storage)
                            if picture_buffer == None:
                                return api_response(404, 'No picture found', 'We could not fetch the picture [%s].'%picture.storage)
                            else:
                                return fk.send_file(picture_buffer, attachment_filename=picture.name, mimetype=picture.mimetype)
            else:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this user.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


### admin projects
@app.route(API_URL + '/admin/<api_token>/projects', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_projects(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/projects')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            projects = ProjectModel.objects()
            projects_dict = {'total_projects':len(projects), 'projects':[]}
            for project in projects:
                projects_dict['projects'].append(project.extended())
            return api_response(200, 'Projects list', projects_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/projects/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_projects_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/projects/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            projects = ProjectModel.objects()
            projects.delete()
            return api_response(200, 'Projects deleted', 'All the projects have been deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/envs/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_envs_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/envs/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            envs = EnvironmentModel.objects()
            envs.delete()
            return api_response(200, 'Environments deleted', 'All the environments have been deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

### admin projects
# 566728709f9d5109b8de3f91
# [{u'useful': [], u'sender': u'5666ee079f9d5171fd03a565', u'extend': {}, u'title': u'This is a comment on the MKS project', u'created': u'2015-12-10 16:57:19.539104', u'content': u'Can we do some phase field simulations with PyMKS?', u'id': u'5669aeef9f9d5162d84546bf', u'attachments': []}]
# 566728709f9d5109b8de3f92
# []
# 566728709f9d5109b8de3f93
# []

# @app.route(API_URL + '/admin/<api_token>/projects/comments/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
# @crossdomain(fk=fk, app=app, origin='*')
# def admin_projects_comments_clear(api_token):
#     logTraffic(API_URL, endpoint='/admin/<api_token>/comments/clear')
#     if fk.request.method == 'GET':
#         projects = ProjectModel.objects()
#         for project in projects:
#             project.comments = []
#             project.save()
#         project = ProjectModel.objects.with_id('566728709f9d5109b8de3f91')
#         project.comments.append('5669aeef9f9d5162d84546bf')
#         project.save()
#         return api_response(200, 'Done', 'Projects comments cleared.')
#     else:
#         return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_comments(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/comments/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                comments = project._comments()
                comments_dict = {'total_comments':0, 'comments':[]}
                for comment_id in comments:
                    comment = CommentModel.objects.with_id(comment_id)
                    if comment != None:
                        comments_dict['comments'].append(comment.info())
                comments_dict['total_comments'] = len(comments_dict['comments'])
                return api_response(200, 'Project comment list', comments_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                # application_id = data.get('app_token', None)
                owner_id = data.get('api_token', None)
                name = data.get('name', '')
                description = data.get('description', '')
                goals = data.get('goals', '')
                tags = data.get('tags', [])
                access = data.get('access', 'private')
                history = data.get('history', [])
                cloned_from_id = data.get('original', '')
                resources = data.get('resources', [])
                group = data.get('group', 'undefined')

                if owner_id == None or name == '':
                    return api_response(400, 'Missing mandatory fields', ' project should have a owner api token and a name.')
                else:
                    logo_storage = 'default-project.png'
                    logo_encoding = ''
                    logo_mimetype = mimetypes.guess_type(logo_storage)[0]
                    logo_buffer = storage_manager.storage_get_file('logo', logo_storage)
                    if logo_buffer != None:
                        old_file_position = logo_buffer.tell()
                        logo_buffer.seek(0, os.SEEK_END)
                        logo_size = logo_buffer.tell()
                        logo_buffer.seek(old_file_position, os.SEEK_SET)
                    else:
                        logo_size = 0
                    logo_name = 'default-project.png'
                    logo_location = 'local'
                    logo_group = 'logo'
                    logo_description = 'This is the default image used for the project logo in case none is provided.'
                    logo, logo_created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), encoding=logo_encoding, name=logo_name, mimetype=logo_mimetype, size=logo_size, storage=logo_storage, location=logo_location, group=logo_group, description=logo_description)
                    
                    # application = None
                    owner = None
                    cloned_from = ''
                    owner = UserModel.objects(api_token=owner_id).first()
                    if cloned_from_id != '':
                        cloned = RecordModel.objects.with_id(cloned_from_id)
                        if cloned != None:
                            cloned_from = str(clone.id)
                    # if application_id != None:
                    #     application = ApplicationModel.objects(app_token=application_id).first()
                    if owner == None or (cloned_from == '' and cloned_from_id != ''):
                        return api_response(400, 'Missing references mandatory fields', 'A project should have an existing owner api token and when provided an existing application token and original record.')
                    # if application != None:
                    #     project, created = ProjectModel.objects.get_or_create(application=application, owner=owner, name=name)
                    # else:
                    project, created = ProjectModel.objects.get_or_create(owner=owner, name=name)
                    if not created:
                        return api_response(200, 'Project already exists', project.info())
                    else:
                        project.description = description
                        project.goals = goals
                        project.tags = tags
                        project.history = history
                        project.cloned_from = cloned_from
                        project.resources = resources
                        project.group = group
                        project.logo = logo
                        project.save()
                        logStat(project=project)
                        return api_response(201, 'Project created', project.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/records/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_records(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/records/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                records = RecordModel.objects(project=project)
                records_dict = {'total_records':len(records), 'records':[]}
                for record in records:
                    records_dict['records'].append(record.extended())
                return api_response(200, 'Project [%s] Records list'%project.name, records_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/admin/<api_token>/project/show/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_show(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/show/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                return api_response(200, 'Project %s'%project.name, project.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/logo/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_logo(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/logo/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project != None:
                logo = project.logo
                if logo.location == 'local' and 'http://' not in logo.storage:
                    logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                    if logo_buffer == None:
                        return api_response(404, 'No logo found', 'We could not fetch the logo at [%s].'%logo.storage)
                    else:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                elif logo.location == 'remote':
                    logo_buffer = storage_manager.web_get_file(logo.storage)
                    if logo_buffer != None:
                        return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                else:
                    # solve the file situation and return the appropriate one.
                    if 'http://' in logo.storage:
                        logo.location = 'remote'
                        logo.save()
                        logo_buffer = storage_manager.web_get_file(logo.storage)
                        if logo_buffer != None:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                        else:
                            logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                            if logo_buffer == None:
                                return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                            else:
                                return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
                    else:
                        logo.location = 'local'
                        logo.save()
                        logo_buffer = storage_manager.storage_get_file('logo', logo.storage)
                        if logo_buffer == None:
                            return api_response(404, 'No logo found', 'We could not fetch the logo at %s.'%logo.storage)
                        else:
                            return fk.send_file(logo_buffer, attachment_filename=logo.name, mimetype=logo.mimetype)
            else:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this application.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/delete/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_delete(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/delete/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                #Delete all attachements and record files too
                project.delete()
                logStat(deleted=True, project=project)
                return api_response(200, 'Deletion succeeded', 'The project %s was succesfully deleted.'%project.name)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/update/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_update(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/update/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)
                    
                    # application_id = data.get('application', None)
                    owner_id = data.get('owner', None)
                    name = data.get('name', project.name)
                    description = data.get('description', project.description)
                    goals = data.get('goals', project.goals)
                    tags = data.get('tags', [])
                    access = data.get('access', project.access)
                    history = data.get('history', [])
                    cloned_from_id = data.get('original', None)
                    resources = data.get('resources', [])
                    group = data.get('group', project.group)
                    application = None
                    owner = None
                    cloned_from = None
                    # if application_id == None:
                    #     application = project.application
                    # else:
                    #     project = ApplicationModel.objects.with_id(application_id)
                    #     if application == None:
                    #         application = project.application
                    if owner_id == None:
                        owner = project.owner
                    else:
                        project = UserModel.objects.with_id(owner_id)
                        if owner == None:
                            owner = project.owner
                    if cloned_from_id == None:
                        cloned_from = project.cloned_from
                    else:
                        cloned_from = None
                        clone = ProjectModel.objects.with_id(cloned_from_id)
                        if clone != None:
                            cloned_from = str(clone.id)
                        if cloned_from == None:
                            cloned_from = project.cloned_from

                    # project.application = application
                    project.owner = owner
                    project.name = name
                    project.description = description
                    project.goals = goals
                    project.tags.extend(tags)
                    project.access = access
                    project.history.extend(history)
                    project.cloned_from = cloned_from
                    project.resources.extend(resources)
                    project.group = group
                    project.save()
                    return api_response(201, 'Project updated', project.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the project information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/download/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_download(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/download/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                prepared = storage_manager.prepare_project(project)
                if prepared[0] == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                else:
                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


@app.route(API_URL + '/admin/<api_token>/project/envs/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_envs(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/envs/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                history_dict = {'total_environments':0, 'environments':[]}
                for env_dict in project.history:
                    env = EnvironmentModel.objects.with_id(env_dict)
                    if env != None:
                        history_dict['environments'].append(env.info())
                history_dict['total_environments'] = len(history_dict['environments'])
                return api_response(200, 'Project %s environments'%project.name, history_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/envs/head/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_envs_head(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/envs/head')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                head = {}
                if len(project.history) > 0:
                    head = project.history[-1]
                return api_response(200, 'Project %s environments head'%project.name, head)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/env/show/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_env_show(project_id, env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/show/<project_id>/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                if env_id not in project.history:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
                else:
                    env = EnvironmentModel.objects.with_id(env_id)
                    if env == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                    else:
                        return api_response(200, 'Project %s environment %s'%(project.name, env_id), env.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/env/next/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_env_push(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/next/<project_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                application_id = data.get('app_token', None)
                group = data.get('group', 'undefined')
                system = data.get('system', 'undefined')
                specifics = data.get('specifics', {})
                version_dict = data.get('version', None)
                bundle_dict = data.get('bundle', None)

                project = ProjectModel.objects.with_id(project_id)

                if project == None:
                    return api_response(400, 'Missing mandatory fields', 'Unable to find this project.')
                else:
                    application = None
                    if application_id != None:
                        application = ApplicationModel.objects(app_token=application_id).first()
                    env, created = EnvironmentModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), group=group, system=system, specifics=specifics)
                    if application != None:
                        env.application = application
                    if not created:
                        return api_response(500, 'Internal Platform Error', 'There is a possible issue with the MongoDb instance.')
                    else:
                        version, created = VersionModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                        if version_dict != None:
                            version.system = version_dict.get('system','unknown')
                            version.baseline = version_dict.get('baseline','')
                            version.marker = version_dict.get('marker','')
                            version.save()
                            env.version = version
                        bundle, created = BundleModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                        if bundle_dict != None:
                            bundle.scope = bundle_dict.get('scope','unknown')
                            location = bundle_dict.get('location', '')
                            if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                                bundle.location = location
                                bundle.save()
                                def handle_file_resolution(_bundle, api_token):
                                    # print _bundle
                                    bundle = BundleModel.objects.with_id(_bundle)
                                    bundle_buffer = storage_manager.web_get_file(location)
                                    bundle.mimetype = mimetypes.guess_type(location)[0]
                                    old_file_position = bundle_buffer.tell()
                                    bundle_buffer.seek(0, os.SEEK_END)
                                    bundle.size = bundle_buffer.tell()
                                    bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                    bundle.save()
                                thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                            env.bundle = bundle
                        env.save()
                        project.history.append(str(env.id))
                        project.save()
                        return api_response(201, 'Environment created', env.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/env/update/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_env_update(project_id, env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/update/<project_id>/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                project = ProjectModel.objects.with_id(project_id)
                if project == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
                else:
                    if env_id not in [str(e.id) for e in project._history()]:
                        return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
                    else:
                        env = EnvironmentModel.objects.with_id(env_id)
                        if env == None:
                            return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                        else:
                            group = data.get('group', env.group)
                            system = data.get('system', env.system)
                            specifics = data.get('specifics', env.specifics)
                            version_dict = data.get('version', None)
                            bundle_dict = data.get('bundle', None)
                            if version_dict != None:
                                version =  env.version
                                version.system = version_dict.get('system', version.system)
                                version.baseline = version_dict.get('baseline', version.baseline)
                                version.marker = version_dict.get('marker', version.marker)
                                version.save()
                            if bundle_dict != None:
                                bundle =  env.bundle
                                location = bundle_dict.get('location', '')
                                bundle.scope = bundle_dict.get('scope', bundle.scope)
                                if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                                    bundle.location = location
                                    bundle.save()
                                    def handle_file_resolution(_bundle, api_token):
                                        # print _bundle
                                        bundle = BundleModel.objects.with_id(_bundle)
                                        bundle_buffer = storage_manager.web_get_file(location)
                                        bundle.mimetype = mimetypes.guess_type(location)[0]
                                        old_file_position = bundle_buffer.tell()
                                        bundle_buffer.seek(0, os.SEEK_END)
                                        bundle.size = bundle_buffer.tell()
                                        bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                        bundle.save()
                                    thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                            env.group = group
                            env.system = system
                            env.specifics = specifics
                            env.save()
                            return api_response(200, 'Project %s environment %s updated'%(project.name, env_id), env.extended())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/env/update/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_env_update(env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/update/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                env = EnvironmentModel.objects.with_id(env_id)
                if env == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                else:
                    group = data.get('group', env.group)
                    system = data.get('system', env.system)
                    specifics = data.get('specifics', env.specifics)
                    version_dict = data.get('version', None)
                    bundle_dict = data.get('bundle', None)
                    if version_dict != None:
                        version =  env.version
                        version.system = version_dict.get('system', version.system)
                        version.baseline = version_dict.get('baseline', version.baseline)
                        version.marker = version_dict.get('marker', version.marker)
                        version.save()
                    if bundle_dict != None:
                        bundle =  env.bundle
                        location = bundle_dict.get('location', '')
                        bundle.scope = bundle_dict.get('scope', bundle.scope)
                        if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                            bundle.location = location
                            bundle.save()
                            def handle_file_resolution(_bundle, api_token):
                                # print _bundle
                                bundle = BundleModel.objects.with_id(_bundle)
                                bundle_buffer = storage_manager.web_get_file(location)
                                bundle.mimetype = mimetypes.guess_type(location)[0]
                                old_file_position = bundle_buffer.tell()
                                bundle_buffer.seek(0, os.SEEK_END)
                                bundle.size = bundle_buffer.tell()
                                bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                bundle.save()
                            thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                    env.group = group
                    env.system = system
                    env.specifics = specifics
                    env.save()
                    return api_response(200, 'Project %s environment %s updated'%(project.name, env_id), env.extended())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/env/show/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_env_show(env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/show/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            env = EnvironmentModel.objects.with_id(env_id)
            if env == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
            else:
                return api_response(200, 'Project %s environment %s'%(project.name, env_id), env.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/env/delete/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_env_delete(env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/delete/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            env = EnvironmentModel.objects.with_id(env_id)
            if env == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
            else:
                env.delete()
                bundle = env.bundle
                if 'http://' not in bundle.location and 'https://' not in bundle.location:
                    storage_manager.storage_delete_file('bundle', bundle.location)
                #delete the files
                return api_response(200, 'Environment %s deleted'%env_id, 'All the information about this environment was deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/env/download/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_env_download(project_id, env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/download/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            env = EnvironmentModel.objects.with_id(env_id)
            if env == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
            else:
                prepared = storage_manager.prepare_env(project, env)
                if prepared[0] == None:
                    return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                else:
                    return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/project/env/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_env_push(project_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)

                group = data.get('group', 'undefined')
                system = data.get('system', 'undefined')
                specifics = data.get('specifics', {})
                version_dict = data.get('version', None)
                bundle_dict = data.get('bundle', None)
                env, created = EnvironmentModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), group=group, system=system, specifics=specifics)
                if not created:
                    return api_response(500, 'Internal Platform Error', 'There is a possible issue with the MongoDb instance.')
                else:
                    version, created = VersionModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                    if version_dict != None:
                        version.system = version_dict.get('system','unknown')
                        version.baseline = version_dict.get('baseline','')
                        version.marker = version_dict.get('marker','')
                        version.save()
                        env.version = version
                    bundle, created = BundleModel.objects.get_or_create(created_at=datetime.datetime.utcnow())
                    if bundle_dict != None:
                        bundle.scope = bundle_dict.get('scope','unknown')
                        location = bundle_dict.get('location', '')
                        if 'http://' in location or 'https://' in location: #only allow web hosted third party content links to be updated here.
                            bundle.location = location
                            bundle.save()
                            def handle_file_resolution(_bundle, api_token):
                                # print _bundle
                                bundle = BundleModel.objects.with_id(_bundle)
                                bundle_buffer = storage_manager.web_get_file(location)
                                bundle.mimetype = mimetypes.guess_type(location)[0]
                                old_file_position = bundle_buffer.tell()
                                bundle_buffer.seek(0, os.SEEK_END)
                                bundle.size = bundle_buffer.tell()
                                bundle_buffer.seek(old_file_position, os.SEEK_SET)
                                bundle.save()
                            thread.start_new_thread(handle_file_resolution, (str(bundle.id),))
                        env.bundle = bundle
                    env.save()
                    return api_response(201, 'Environment created', env.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/project/env/download/<project_id>/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_project_env_download(project_id, env_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/project/env/download/<project_id>/<env_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            project = ProjectModel.objects.with_id(project_id)
            if project == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                if env_id not in project.history:
                    return api_response(404, 'Request suggested an empty response', 'Unable to find this project environment.')
                else:
                    env = EnvironmentModel.objects.with_id(env_id)
                    if env == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to load this project environment.')
                    else:
                        prepared = storage_manager.prepare_env(project, env)
                        if prepared[0] == None:
                            return api_response(404, 'Request suggested an empty response', 'Unable to retrieve an environment to download.')
                        else:
                            return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# @TODO
# Get a zip of any environment
# @app.route(API_URL + '/admin/<api_token>/environment/<env_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

### admin records
@app.route(API_URL + '/admin/<api_token>/records', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_records(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/records')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            records = RecordModel.objects()
            records_dict = {'total_records':len(records), 'records':[]}
            for record in records:
                records_dict['records'].append(record.extended())
            return api_response(200, 'Records list', records_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/records/clear', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_records_clear(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/records/clear')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            records = RecordModel.objects()
            records.delete()
            return api_response(200, 'Records cleared', 'All the records have been deleted.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')


# @TODO
# Get the record comments
# @app.route(API_URL + '/admin/<api_token>/record/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

@app.route(API_URL + '/admin/<api_token>/record/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_record_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/record/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                project_id = data.get('project', None)
                data_pop(data, 'project')
                # application_id = data.get('app_token', None)
                # data_pop(data, 'app_token')
                parent_id = data.get('parent', '')
                data_pop(data, 'parent')
                label = data.get('label', 'Recorded at %s'%str(datetime.datetime.utcnow()))
                data_pop(data, 'label')
                tags = data.get('tags', [])
                data_pop(data, 'tags')
                system = data.get('system', {})
                data_pop(data, 'system')
                inputs = data.get('inputs', [])
                data_pop(data, 'inputs')
                outputs = data.get('outputs', [])
                data_pop(data, 'outputs')
                dependencies = data.get('dependencies', [])
                data_pop(data, 'dependencies')
                status = data.get('status', 'unknown')
                data_pop(data, 'status')
                environment_id = data.get('environment', None)
                data_pop(data, 'environment')
                cloned_from_id = data.get('cloned_from', '')
                data_pop(data, 'cloned_from')
                access = data.get('access', 'private')
                data_pop(data, 'access')
                # resources_ids = data.get('resources', [])
                # data_pop(data, 'resources')
                rationels = data.get('rationels', [])
                data_pop(data, 'rationels')
                # resources = []
                if project_id == None:
                    return api_response(400, 'Missing mandatory fields', ' record should have a record to reference itself to.')
                else:
                    project = None
                    # application = None
                    environment = None
                    cloned_from = ''
                    parent = ''
                    project = ProjectModel.objects.with_id(project_id)
                    # if application_id != None:
                    #     application = ApplicationModel.objects(app_token=application_id).first()
                    if environment_id != None:
                        environment = EnvironmentModel.objects.with_id(environment_id)

                    if cloned_from_id != '':
                        cloned = RecordModel.objects.with_id(cloned_from_id)
                        if cloned != None:
                            cloned_from = str(clone.id)
                    if parent_id != '':
                        parent_inst = RecordModel.objects.with_id(parent_id)
                        if parent_inst != None:
                            parent = str(parent_inst.id)
                    if (project == None and project_id != None) or (environment == None and environment_id != None) or (cloned_from == '' and cloned_from_id != '') or (parent == '' and parent_id != ''):
                        return api_response(400, 'Missing references mandatory fields', 'A record should have an existing project and when provided an existing application, parent record and original record.')
                    if environment_id == None:
                        history = project.history
                        if len(history) > 0:
                            environment = history[-1] # Create with the latest environment.
                    # if len(resources) > 0:
                    #     for res_id in resources_ids:
                    #         res = FileModel.objects.with_id(res_id)
                    #         if res != None:
                    #             resources.append(res)
                    # print resources
                    # if application != None:
                    #     if environment != None:
                    #         record, created = RecordModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), project=project, application=application, environment=environment, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                    #     else:
                    #         record, created = RecordModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), project=project, application=application, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                    # else:
                    if environment != None:
                        record, created = RecordModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), project=project, environment=environment, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                    else:
                        record, created = RecordModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), project=project, parent=parent, label=label, tags=tags, system=system, inputs=inputs, outputs=outputs, dependencies=dependencies, status=status, access=access, rationels=rationels)
                    if len(data) != 0:
                        body, created = RecordBodyModel.objects.get_or_create(head=record, data=data)
                    logStat(record=record)
                    return api_response(201, 'Record created', record.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/record/show/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_record_show(record_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/record/show/<record_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            record = RecordModel.objects.with_id(record_id)
            if record == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
            else:
                return api_response(200, 'Record info', record.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/record/delete/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_record_delete(record_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/record/delete/<record_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            record = RecordModel.objects.with_id(record_id)
            if record == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
            else:
                # Delete all comments and attachements and files.
                record.delete()
                logStat(deleted=True, record=record)
                return api_response(200, 'Deletion succeeded', 'The record %s was succesfully deleted.'%str(record.id))
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/record/update/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_record_update(record_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/record/update/<record_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            record = RecordModel.objects.with_id(record_id)
            if record == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this project.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)

                    project_id = data.get('project', None)
                    data_pop(data, 'project')
                    # application_id = data.get('application', None)
                    # data_pop(data, 'application')
                    parent_id = data.get('parent', None)
                    data_pop(data, 'parent')
                    label = data.get('label', record.label)
                    data_pop(data, 'label')
                    tags = data.get('tags', [])
                    data_pop(data, 'tags')
                    system = data.get('system', record.system)
                    data_pop(data, 'system')
                    inputs = data.get('inputs', [])
                    data_pop(data, 'inputs')
                    outputs = data.get('outputs', [])
                    data_pop(data, 'outputs')
                    dependencies = data.get('dependencies', [])
                    data_pop(data, 'dependencies')
                    status = data.get('status', record.status)
                    data_pop(data, 'status')
                    environment_id = data.get('environment', None)
                    data_pop(data, 'environment')
                    cloned_from_id = data.get('cloned_from', None)
                    data_pop(data, 'cloned_from')
                    access = data.get('access', record.access)
                    data_pop(data, 'access')
                    resources = data.get('resources', [])
                    data_pop(data, 'resources')
                    rationels = data.get('rationels', [])
                    data_pop(data, 'rationels')
                    project = None
                    application = None
                    parent = None
                    environment = None
                    cloned_from = None
                    if project_id == None:
                        project = record.project
                    else:
                        project = ProjectModel.objects.with_id(project_id)
                        if project == None:
                            project = record.project
                    # if application_id == None:
                    #     application = record.application
                    # else:
                    #     record = ApplicationModel.objects.with_id(application_id)
                    #     if application == None:
                    #         application = record.application
                    if parent_id == None:
                        parent = record.parent
                    else:
                        parent = None
                        parent_inst = RecordModel.objects.with_id(parent_id)
                        if parent_inst != None:
                            parent = str(parent_inst.id)
                        if parent == None:
                            parent = record.parent
                    if environment_id == None:
                        environment = record.environment
                    else:
                        environment = EnvironmentModel.objects.with_id(environment_id)
                        if environment == None:
                            environment = record.environment
                    if cloned_from_id == None:
                        cloned_from = record.cloned_from
                    else:
                        cloned_from = None
                        clone = RecordModel.objects.with_id(parent_id)
                        if clone != None:
                            cloned_from = str(clone.id)
                        if cloned_from == None:
                            cloned_from = record.cloned_from
                    record.project = project
                    # record.application = application
                    record.parent = parent
                    record.label = label
                    record.system = system
                    record.status = status
                    record.tags.extend(tags)
                    record.access = access
                    record.inputs.extend(inputs)
                    record.outputs.extend(outputs)
                    record.dependencies.extend(dependencies)
                    record.rationels.extend(rationels)
                    record.cloned_from = cloned_from
                    record.environment = environment
                    record.resources.extend(resources)
                    record.save()
                    if len(data) != 0:
                        body, created = RecordBodyModel.objects.get_or_create(head=record)
                        if created:
                            body.data = data
                            body.save()
                        else:
                            body.data = merge_dicts(body.data, data)
                            body.save()
                    return api_response(201, 'Record updated', project.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the project information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/record/download/<project_id>/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_record_download(project_id, record_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/record/download/<project_id>/<record_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            record = RecordModel.objects.with_id(record_id)
            if record == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this record.')
            else:
                if str(record.project.id) != project_id:
                    return api_response(401, 'Unauthorized access to this record', 'This record is not part of the provided project.')
                else:
                    prepared = storage_manager.prepare_record(record)
                    if prepared[0] == None:
                        return api_response(404, 'Request suggested an empty response', 'Unable to retrieve a record to download.')
                    else:
                        return fk.send_file(prepared[0], as_attachment=True, attachment_filename=prepared[1], mimetype='application/zip')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# @TODO
# Get a zip of the whole record
# @app.route(API_URL + '/admin/<api_token>/record/download/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

# @TODO
# Get a zip of the record environment
# @app.route(API_URL + '/admin/<api_token>/record/env/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

# @TODO
# Get a zip of the record files
# @app.route(API_URL + '/admin/<api_token>/record/env/<record_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

### admin diffs
@app.route(API_URL + '/admin/<api_token>/diffs', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_diffs(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/diffs')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            diffs = DiffModel.objects()
            diffs_dict = {'total_diffs':len(diffs), 'diffs':[]}
            for diff in diffs:
                diffs_dict['diffs'].append(diff.extended())
            return api_response(200, 'Diffs list', diffs_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# @TODO
# Get the diff comments
# @app.route(API_URL + '/admin/<api_token>/diff/comments/<project_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])

@app.route(API_URL + '/admin/<api_token>/diff/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_diff_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/diff/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                sender_id =  data.get('session', None)
                record_from_id = data.get('from', None)
                record_to_id = data.get('to', None)
                method = data.get('method', 'undefined')
                resources = data.get('resources', [])
                proposition = data.get('proposition', 'undefined')
                status = data.get('status', 'undefined')
                if sender_id == None or record_from_id == None or record_to_id == None:
                    return api_response(400, 'Missing mandatory fields', 'A diff should have at least a sender, a record from where the diff is linked and a record to which it is linked.')
                else:
                    sender = None
                    record_from = None
                    record_to = None
                    sender = UserModel.objects(session=sender_id).first()
                    record_from = RecordModel.objects.with_id(record_from_id)
                    record_to = RecordModel.objects.with_id(record_to_id)
                    if sender == None or record_from == None or record_to == None:
                        return api_response(400, 'Missing references mandatory fields', 'A diff should have at least an existing sender, an existing record from where the diff is linked and an existing record to which it is linked.')
                    if (record_to.access != 'private' or (record_from.access == 'private' and record_from.project.owner == sender)) and ((record_from.access == 'private' and record_from.project.owner == sender) or record_from.access != 'private', api_token):
                        diff, created = DiffModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), sender=sender, targeted=record_to.project.owner, record_from=record_from, record_to=record_to, method=method, resources=resources, proposition=proposition, status=status)
                        if not created:
                            return api_response(200, 'Diff already exists', diff.info())
                        else:
                            logStat(diff=diff)
                            return api_response(201, 'Diff created', diff.info())
                    else:
                        return api_response(401, 'Unauthorized access to records', 'To be able to reference a record you either have to own it or have a non private access to it.')
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/diff/show/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_diff_show(diff_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/diff/show/<diff_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            diff = DiffModel.objects.with_id(diff_id)
            if diff == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                return api_response(200, 'Diff info', diff.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/diff/delete/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_diff_delete(diff_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/diff/delete/<diff_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            diff = DiffModel.objects.with_id(diff_id)
            if diff == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                #Delete all the files
                diff.delete()
                logStat(deleted=True, diff=diff)
                return api_response(200, 'Deletion succeeded', 'The diff %s was succesfully deleted.'%str(diff.id))
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/diff/update/<diff_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_diff_update(diff_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/diff/update/<diff_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            diff = DiffModel.objects.with_id(diff_id)
            if diff == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)

                    sender_id =  data.get('sender', None)
                    record_from_id = data.get('from', None)
                    record_to_id = data.get('to', None)
                    method = data.get('method', 'undefined')
                    resources = data.get('resources', [])
                    proposition = data.get('proposition', 'undefined')
                    status = data.get('status', 'undefined')
                    sender = None
                    record_from = None
                    record_to = None
                    if sender_id == None:
                        sender = diff.sender
                    else:
                        sender = UserModel.objects.with_id(sender_id)
                        if sender == None:
                            sender = message.sender
                    if record_from_id == None:
                        record_from = diff.record_from
                    else:
                        record_from = RecordModel.objects.with_id(record_from_id)
                        if record_from == None:
                            record_from = diff.record_from
                    if record_to_id == None:
                        record_to = diff.record_to
                    else:
                        record_to = RecordModel.objects.with_id(record_to_id)
                        if record_to == None:
                            record_to = diff.record_to

                    diff.sender = sender
                    diff.receiver = record_to.project.owner
                    diff.record_from = record_from
                    diff.record_to = record_to
                    diff.method = method
                    diff.resources.extend(resources)
                    diff.proposition = proposition
                    diff.status = status
                    diff.save()
                    return api_response(201, 'Diff updated', diff.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the diff information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

### admin files
@app.route(API_URL + '/admin/<api_token>/files', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_files(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/files')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            files = FileModel.objects()
            files_dict = {'total_files':len(files), 'files':[]}
            for _file in files:
                files_dict['files'].append(_file.extended())
            return api_response(200, 'Files list', files_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

# @TODO
@app.route(API_URL + '/admin/<api_token>/file/upload/<group>/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_upload(group, item_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/upload/<group>/<item_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if group not in ["input", "output", "dependencie", "descriptive", "diff", "resource-record", "resource-env", "resource-app", "attach-comment", "attach-message", "picture" , "logo-project" , "logo-app" , "resource", "bundle"]:
                return api_response(405, 'Method Group not allowed', 'This endpoint supports only a specific set of groups.')
            else:
                if fk.request.files:
                    file_obj = fk.request.files['file']
                    filename = '%s_%s'%(item_id, file_obj.filename)
                    _file, created = FileModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), name=filename)
                    if not created:
                        return api_response(200, 'File already exists with same name for this item', _file.info())
                    else:
                        encoding = ''
                        if file_obj != None:
                            old_file_position = file_obj.tell()
                            file_obj.seek(0, os.SEEK_END)
                            size = file_obj.tell()
                            file_obj.seek(old_file_position, os.SEEK_SET)
                        else:
                            size = 0
                        storage = '%s_%s'%(item_id, file_obj.filename)
                        location = 'local'
                        mimetype = mimetypes.guess_type(storage)[0]
                        group_ = group
                        description = ''
                        item = None
                        owner = None
                        if group == 'input':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            description = '%s is an input file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'output':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            description = '%s is an output file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'dependencie':
                            item = RecordModel.objects.with_id(item_id)
                            owner = item.project.owner
                            description = '%s is an dependency file for the record %s'%(file_obj.filename, str(item.id))
                        elif group == 'descriptive':
                            item = ProjectModel.objects.with_id(item_id)
                            owner = item.owner
                            description = '%s is a resource file for the project %s'%(file_obj.filename, str(item.id))
                        elif group == 'diff':
                            item = DiffModel.objects.with_id(item_id)
                            owner = item.sender
                            description = '%s is a resource file for the collaboration %s'%(file_obj.filename, str(item.id))
                        elif 'attach' in group:
                            if 'message' in group:
                                item = MessageModel.objects.with_id(item_id)
                                owner = item.sender
                                description = '%s is an attachement file for the message %s'%(file_obj.filename, str(item.id))
                            elif 'comment' in group:
                                item = CommentModel.objects.with_id(item_id)
                                owner = item.sender
                                description = '%s is an attachement file for the comment %s'%(file_obj.filename, str(item.id))
                            group_ = group.split('-')[0]
                        elif group == 'bundle':
                            item = BundleModel.objects.with_id(item_id)
                        elif group == 'picture':
                            item = ProfileModel.objects.with_id(item_id)
                            owner = item.user
                            description = '%s is the picture file of the profile %s'%(file_obj.filename, str(item.id))
                            _file.delete()
                            _file = item.picture
                        elif 'logo' in group:
                            if 'app' in group:
                                item = ApplicationModel.objects.with_id(item_id)
                                owner = item.developer
                                description = '%s is the logo file of the application %s'%(file_obj.filename, str(item.id))
                            elif 'project' in group:
                                item = ProjectModel.objects.with_id(item_id)
                                owner = item.owner
                                description = '%s is the logo file of the project %s'%(file_obj.filename, str(item.id))
                            _file.delete()
                            _file = item.logo
                        elif 'resource' in group:
                            if 'record' in group:
                                item = RecordModel.objects.with_id(item_id)
                                owner = item.project.owner
                                description = '%s is an resource file for the record %s'%(file_obj.filename, str(item.id))
                            elif 'env' in group:
                                item = EnvironmentModel.objects.with_id(item_id)
                                description = '%s is a resource file for the environment %s'%(file_obj.filename, str(item.id))
                            elif 'app' in group:
                                item = ApplicationModel.objects.with_id(item_id)
                                description = '%s is a resource file for the app %s'%(file_obj.filename, str(item.id))
                            group_ = group.split('-')[0]

                        if item == None:
                            if group != 'picture' or group != 'logo':
                                return api_response(400, 'Missing mandatory instance', 'A file should reference an existing item.')
                        else:
                            _file.description = description
                            _file.encoding = encoding
                            _file.size = size
                            # _file.path = path
                            _file.storage = storage
                            _file.location = location
                            _file.mimetype = mimetype
                            _file.group = group_
                            _file.save()
                            uploaded = storage_manager.storage_upload_file(_file, file_obj)
                            if not uploaded[0]:
                                _file.delete()
                                return api_response(500, 'An error occured', "%s"%uploaded[1])
                            else:
                                if group == 'input':
                                    item.resources.append(str(_file.id))
                                elif group == 'output':
                                    item.resources.append(str(_file.id))
                                elif group == 'dependencie':
                                    item.resources.append(str(_file.id))
                                elif group == 'descriptive':
                                    item.resources.append(str(_file.id))
                                elif group == 'diff':
                                    item.resources.append(str(_file.id))
                                elif group == 'bundle':
                                    _file.delete()
                                    if item.location != storage:
                                        storage_manager.storage_delete_file('bundle',item.location)
                                    item.encoding = encoding
                                    item.size = size
                                    item.scope = 'local'
                                    item.location = storage
                                    item.mimetype = mimetype
                                    item.save()
                                elif 'attach' in group:
                                    item.attachments.append(str(_file.id))
                                elif group == 'picture':
                                    if item.picture.location != storage:
                                        storage_manager.storage_delete_file('picture',item.picture.storage)
                                    if item != None:
                                        item.picture = _file
                                elif 'logo' in group:
                                    if item.logo.location != storage:
                                        storage_manager.storage_delete_file('logo',item.logo.storage)
                                    if item != None:
                                        item.logo = _file
                                elif 'resource' in group:
                                    item.resources.append(str(_file.id))
                                if item != None:
                                    item.save()
                                logStat(file_obj=_file)
                                return api_response(201, 'New file created', _file.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

# @TODO
@app.route(API_URL + '/admin/<api_token>/file/download/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_download(file_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/download/<file_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            file_meta = FileModel.objects.with_id(file_id)
            if file_meta == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
            else:
                file_obj = None
                if file_meta.location == 'remote':
                    file_obj = storage_manager.web_get_file(file_meta.storage)
                elif file_meta.location == 'local':
                    file_obj = storage_manager.storage_get_file(file_meta.group, file_meta.storage)

                if file_obj == None:
                    return api_response(404, 'Request suggested an empty response', 'No content found for this file.')
                else:
                    # return fk.send_file(
                    #     file_obj,
                    #     file_meta.mimetype,
                    #     # as_attachment=True,
                    #     attachment_filename=file_meta.name,
                    # )
                    if file_meta.group == 'logo' or file_meta.group == 'picture':
                        return fk.send_file(
                            file_obj,
                            file_meta.mimetype,
                            # as_attachment=True,
                            attachment_filename=file_meta.name,
                        )
                    else:
                        if file_meta.name.split('.')[1] in ['jpg', 'pdf', 'txt']:
                            return fk.send_file(
                                file_obj,
                                file_meta.mimetype,
                                # as_attachment=True,
                                attachment_filename=file_meta.name,
                            )
                        else:
                            # Check the mimetype for media files to just provide them without attachment.
                            return fk.send_file(
                                    file_obj,
                                    file_meta.mimetype,
                                    as_attachment=True,
                                    attachment_filename=file_meta.name,
                                )

            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                encoding = data.get('developer', '')
                size = data.get('developer', 0)
                name = data.get('developer', '')
                path = data.get('developer', '')
                storage = data.get('developer', '')
                location = data.get('location', 'undefined')
                mimetype = data.get('developer', mimetypes.guess_type(location)[0])
                group = data.get('group', 'undefined')
                description = data.get('description', '')
                if storage == '' or name == '':
                    return api_response(400, 'Missing mandatory fields', 'A file should have at least a name and a storage reference (s3 key or url).')
                else:
                    _file, created = FileModel.objects.get_or_create(encoding=encoding, name=name, mimetype=mimetype, size=size, path=path, storage=storage, location=location, group=group, description=description)
                    if not created:
                        return api_response(200, 'File already exists', _file.info())
                    else:
                        return api_response(201, 'File created', _file.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/file/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                encoding = data.get('encoding', '')
                size = data.get('size', 0)
                name = data.get('name', '')
                storage = data.get('storage', '')
                owner_id = data.get('owner', None)
                location = data.get('location', 'undefined')
                mimetype = data.get('mimetype', mimetypes.guess_type(location)[0])
                group = data.get('group', 'undefined')
                description = data.get('description', '')
                owner = None
                if owner_id != None:
                    owner = UserModel.objects.with_id(owner_id)
                if storage == '' or name == '' or (owner_id != None and owner == None, api_token):
                    return api_response(400, 'Missing mandatory fields', 'A file should have at least a name and a storage reference (s3 key or url). Also when a owner is provided he should exist.')
                else:
                    if owner == None:
                        _file, created = FileModel.objects.get_or_create(encoding=encoding, name=name, mimetype=mimetype, size=size, storage=storage, location=location, group=group, description=description)
                    else:
                        _file, created = FileModel.objects.get_or_create(owner=owner, encoding=encoding, name=name, mimetype=mimetype, size=size, storage=storage, location=location, group=group, description=description)
                    if not created:
                        return api_response(200, 'File already exists', _file.info())
                    else:
                        logStat(file_obj=_file)
                        return api_response(201, 'File created', _file.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/file/show/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_show(file_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/show/<file_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            _file = FileModel.objects.with_id(file_id)
            if _file == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
            else:
                return api_response(200, 'File %s'%_file.name, _file.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/file/delete/<item_id>/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_delete(item_id, file_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/delete/<item_id>/<file_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            _file = FileModel.objects.with_id(file_id)
            if _file == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
            else:
                item = None
                if _file.group == 'input':
                    item = RecordModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            _file.delete()
                            item.inputs.remove(file_id)
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                elif _file.group == 'output':
                    item = RecordModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            _file.delete()
                            item.outputs.remove(file_id)
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                elif _file.group == 'dependencie':
                    item = RecordModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            _file.delete()
                            item.dependencies.remove(file_id)
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                elif _file.group == 'diff':
                    item = DiffModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            _file.delete()
                            item.resources.remove(file_id)
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                elif _file.group == 'attach':
                    item = MessageModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            _file.delete()
                            item.attachments.remove(file_id)
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                    else:
                        item = CommentModel.objects.with_id(item_id)
                        if item != None:
                            try:
                                _file.delete()
                                item.attachments.remove(file_id)
                                if _file.location == 'local':
                                    storage_manager.storage_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                elif _file.group == 'picture':
                    item = ProfileModel.objects.with_id(item_id)
                    if item != None:
                        _file.storage = 'default-picture.png'
                        picture_buffer = storage_manager.storage_get_file('picture', 'default-picture.png')
                        _file.name = 'default-picture.png'
                        _file.location = 'local'
                        _file.group = 'picture'
                        _file.description = 'This is the default image used for the user profile picture in case none is provided.'
                        if picture_buffer != None:
                            old_file_position = picture_buffer.tell()
                            picture_buffer.seek(0, os.SEEK_END)
                            p_file.size = picture_buffer.tell()
                            picture_buffer.seek(old_file_position, os.SEEK_SET)
                        else:
                            _file.size = 0
                        _file.save()
                        if _file.location == 'local':
                            storage_manager.storage_delete_file(_file.group, _file.storage)

                elif _file.group == 'logo':
                    item = ApplicationModel.objects.with_id(item_id)
                    if item != None:
                        _file.storage = 'default-logo.png'
                        logo_buffer = storage_manager.storage_get_file('logo', 'default-logo.png')
                        _file.name = 'default-logo.png'
                        _file.location = 'local'
                        _file.group = 'logo'
                        _file.description = 'This is the default image used for the app logo in case none is provided.'
                        if logo_buffer != None:
                            old_file_position = logo_buffer.tell()
                            logo_buffer.seek(0, os.SEEK_END)
                            p_file.size = logo_buffer.tell()
                            logo_buffer.seek(old_file_position, os.SEEK_SET)
                        else:
                            _file.size = 0
                        _file.save()
                        if _file.location == 'local':
                            storage_manager.storage_delete_file(_file.group, _file.storage)
                    else:
                        item = ProjectModel.objects.with_id(item_id)
                        if item != None:
                            _file.storage = 'default-project.png'
                            logo_buffer = storage_manager.storage_get_file('logo', 'default-project.png')
                            _file.name = 'default-project.png'
                            _file.location = 'local'
                            _file.group = 'logo'
                            _file.description = 'This is the default image used for the project logo in case none is provided.'
                            if logo_buffer != None:
                                old_file_position = logo_buffer.tell()
                                logo_buffer.seek(0, os.SEEK_END)
                                p_file.size = logo_buffer.tell()
                                logo_buffer.seek(old_file_position, os.SEEK_SET)
                            else:
                                _file.size = 0
                            _file.save()
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)

                elif _file.group == 'resource':
                    item = RecordModel.objects.with_id(item_id)
                    if item != None:
                        try:
                            item.resources.remove(file_id)
                            _file.delete()
                            if _file.location == 'local':
                                storage_manager.storage_delete_file(_file.group, _file.storage)
                        except ValueError:
                            pass
                    else:
                        item = EnvironmentModel.objects.with_id(item_id)
                        if item != None:
                            try:
                                item.resources.remove(file_id)
                                _file.delete()
                                if _file.location == 'local':
                                    storage_manager.storage_delete_file(_file.group, _file.storage)
                            except ValueError:
                                pass
                        else:
                            item = ProjectModel.objects.with_id(item_id)
                            if item != None:
                                try:
                                    item.resources.remove(file_id)
                                    _file.delete()
                                    if _file.location == 'local':
                                        storage_manager.storage_delete_file(_file.group, _file.storage)
                                except ValueError:
                                    pass
                            else:
                                item = ApplicationModel.objects.with_id(item_id)
                                if item != None:
                                    try:
                                        item.resources.remove(file_id)
                                        _file.delete()
                                        if _file.location == 'local':
                                            storage_manager.storage_delete_file(_file.group, _file.storage)
                                    except ValueError:
                                        pass
                if item == None:
                    if item_id in _file.storage or item_id in _file.name:
                        _file.delete()
                        storage_manager.storage_delete_file(_file.group, _file.storage)
                        logStat(deleted=True, file_obj=_file)
                        return api_response(200, 'Deletion succeeded', 'The file %s was succesfully deleted.'%_file.name)
                    else:
                        return api_response(400, 'Missing mandatory instance', 'A file should reference an existing item.')
                else:
                    item.save()
                logStat(deleted=True, file_obj=_file)
                return api_response(200, 'Deletion succeeded', 'The file %s was succesfully deleted.'%_file.name)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/file/update/<file_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_file_update(file_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/file/update/<file_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            _file = FileModel.objects.with_id(file_id)
            if _file == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this file.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)

                    encoding = data.get('encoding', _file.encoding)
                    size = data.get('size', _file.size)
                    name = data.get('name', _file.name)
                    path = data.get('path', _file.path)
                    storage = data.get('storage', _file.storage)
                    location = data.get('location', _file.location)
                    mimetype = data.get('mimetype', _file.mimetype)
                    group = data.get('group', _file.group)
                    description = data.get('description', _file.description)
                    if name == '':
                        name = _file.name
                    if location == '':
                        location = _file.location
                    _file.encoding = encoding
                    _file.size = size
                    _file.name = name
                    _file.path = path
                    _file.storage = storage
                    _file.location = location
                    _file.mimetype = mimetype
                    _file.group = group
                    _file.description = description
                    _file.save()
                    return api_response(201, 'File updated', _file.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the file information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

### admin messages
@app.route(API_URL + '/admin/<api_token>/messages', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_messages(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/messages')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            messages = MessageModel.objects()
            messages_dict = {'total_messages':len(messages), 'messages':[]}
            for message in messages:
                messages_dict['messages'].append(message.extended())
            return api_response(200, 'Messages list', messages_dict)
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/message/create', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_message_create(api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/message/create')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            if fk.request.data:
                secure_content(fk.request.data)
                data = json.loads(fk.request.data)
                sender_id = data.get('sender', None)
                receiver_id = data.get('receiver', None)
                title = data.get('title', '')
                content = data.get('content', '')
                attachments = data.get('attachments', [])
                if sender_id == '' or receiver_id == '':
                    return api_response(400, 'Missing mandatory fields', 'A message should have at least a sender and a receiver.')
                else:
                    if title == '' and content == '':
                        return api_response(400, 'Missing mandatory fields', 'A message cannot have title and content empty.')
                    
                    sender = UserModel.objects(session=sender_id).first()
                    receiver = UserModel.objects.with_id(receiver_id)
                    message, created = MessageModel.objects.get_or_create(created_at=str(datetime.datetime.utcnow()), sender=sender, receiver=receiver, title=title, attachments=attachments, content=content)
                    if sender == None or receiver == None:
                        return api_response(400, 'Missing mandatory fields', 'A message should have at least an existing sender and an existing receiver.')
                    if not created:
                        # Impossible only if the time field fails
                        return api_response(200, 'Message already exists', message.info())
                    else:
                        logStat(message=message)
                        return api_response(201, 'Message created', message.info())
            else:
                return api_response(204, 'Nothing created', 'You must provide the message information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/message/show/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_message_show(message_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/message/show/<message_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            message = MessageModel.objects.with_id(message_id)
            if message == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
            else:
                return api_response(200, 'Message %s'%str(message.id), message.extended())
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/message/delete/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_message_delete(message_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/message/delete/<message_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            message = MessageModel.objects.with_id(message_id)
            if message == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
            else:
                # Delete attachements maybe??
                message.delete()
                logStat(deleted=True, message=message)
                return api_response(200, 'Deletion succeeded', 'The message %s was succesfully deleted.'%str(message.id))
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')

@app.route(API_URL + '/admin/<api_token>/message/update/<message_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_message_update(message_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/message/update/<message_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'POST':
            message = MessageModel.objects.with_id(message_id)
            if message == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this message.')
            else:
                if fk.request.data:
                    secure_content(fk.request.data)
                    data = json.loads(fk.request.data)
                    sender_id = data.get('sender', None)
                    receiver_id = data.get('receiver', None)
                    title = data.get('title', message.title)
                    content = data.get('content', message.content)
                    attachments = data.get('attachments', [])
                    sender = None
                    receiver = None
                    if sender_id == None:
                        sender = message.sender
                    else:
                        sender = UserModel.objects(session=sender_id).first()
                        if sender == None:
                            sender = message.sender
                    if receiver_id == None:
                        receiver = message.receiver
                    else:
                        receiver = UserModel.objects.with_id(receiver_id)
                        if receiver == None:
                            receiver = message.receiver
                    message.sender = sender
                    message.receiver = receiver
                    message.title = title
                    message.content = content
                    message.attachments.extend(attachments)
                    message.save()
                    return api_response(201, 'Message updated', message.info())
                else:
                    return api_response(204, 'Nothing created', 'You must provide the message information.')
        else:
            return api_response(405, 'Method not allowed', 'This endpoint supports only a POST method.')

@app.route(API_URL + '/admin/<api_token>/resolve/<item_id>', methods=['GET','POST','PUT','UPDATE','DELETE','POST'])
@crossdomain(fk=fk, app=app, origin='*')
def admin_resolve_item(item_id, api_token):
    logTraffic(API_URL, endpoint='/admin/<api_token>/resolve/<item_id>')
    admin_user = access_manager.check_admin(api_token)
    if admin_user == None:
        return api_response(401, 'Unauthorized access to the API', 'This is not an admin account.')
    else:
        if fk.request.method == 'GET':
            resolution = {'type':'', 'endpoints':[]}
            if item_id == 'root':
                resolution['type'] = 'User'
                # Admin actions in this case.
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['status', '--st'], 'endpoint':'/admin/<api_token>/status'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['profile', '--pf'], 'endpoint':'/admin/<api_token>/profile/show'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['picture', '--pc'], 'endpoint':'/admin/<api_token>/user/picture'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['projects', '--pj'], 'endpoint':'/admin/<api_token>/projects'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['records', '--re'], 'endpoint':'/admin/<api_token>/records'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['messages', '--me'], 'endpoint':'/admin/<api_token>/messages'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['comments', '--cm'], 'endpoint':'/admin/<api_token>/comments'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['diffs', '--di'], 'endpoint':'/admin/<api_token>/diffs'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/admin/<api_token>/files'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['search', '--se'], 'endpoint':'/admin/<api_token>/search/<query>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['search user', '--su'], 'endpoint':'/admin/<api_token>/user/search/<query>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['search project', '--sp'], 'endpoint':'/admin/<api_token>/project/search/<query>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['search app', '--sa'], 'endpoint':'/public/app/search/<query>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['users', '--us'], 'endpoint':'/public/users'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['home', '--ho'], 'endpoint':'/admin/<api_token>/user/home'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['apps', '--ap'], 'endpoint':'/admin/<api_token>/apps'})

                resolution['endpoints'].append({'methods':['POST'], 'struct':{'developer':'string','name':'string','about':'string','logo':'string','access':'string','access':'string','network':'string','visibile':'string'}, 'meta':['app-created', '--apc'], 'endpoint':'/admin/<api_token>/app/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'owner':'string', 'encoding':'string','size':'string','name':'string','path':'string','storage':'string','location':'string','mimetype':'string','group':'string','description':'string'}, 'meta':['file-create', '--fic'], 'endpoint':'/admin/<api_token>/file/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'session':'string','from':'string','to':'string','':'string','method':'string','resources':'list','proposition':'string','status':'string'}, 'meta':['diff-create', '--dic'], 'endpoint':'/admin/<api_token>/diff/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'group':'string', 'system':'string', 'specifics':'dict', 'version':'dict', 'bundle':'dict'}, 'meta':['env-create', '--enc'], 'endpoint':'/admin/<api_token>/env/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'project':'string','application':'string','parent':'string','label':'string','tags':'list','system':'dict','inputs':'list','outputs':'list','dependencies':'list','status':'string','environment':'string','cloned_from':'string','access':'string','resources':'list','rationels':'list'}, 'meta':['record-create', '--rrc'], 'endpoint':'/admin/<api_token>/record/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'application':'string','owner':'string','name':'string','description':'string','goals':'string','tags':'list','access':'string','history':'list','original':'string','resources':'list','group':'string'}, 'meta':['project-create', '--pjc'], 'endpoint':'/admin/<api_token>/project/create'})
                # resolution['endpoints'].append({'methods':['POST'], 'struct':{'title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/<group>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'sender':'string','receiver':'string','title':'string', 'content':'string', 'attachments':'list'}, 'meta':['message-create', '--mec'], 'endpoint':'/admin/<api_token>/message/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'email':'string', 'password':'string', 'passwordAgain':'string', 'group':'string'}, 'meta':['user-create', '--usc'], 'endpoint':'/admin/<api_token>/user/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'fname':'string', 'lname':'string', 'picture':'string','organisation':'string','about':'string'}, 'meta':['profile-create', '--pfc'], 'endpoint':'/admin/<api_token>/user/profile/create/<selected.id>'})
                
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['token', '--tk'], 'endpoint':'/private/<credential.api_token>/<credential.app_token>/*'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'email':'<credential.email>', 'password':'<credential.password>'}, 'meta':['login', '--lg'], 'endpoint':'/admin/<api_token>/user/login'})

                return api_response(200, 'Root resolution results', resolution)
            item = UserModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'User'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/user/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--de'], 'endpoint':'/admin/<api_token>/user/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'email':'string', 'password':'string', 'passwordAgain':'string', 'group':'string'}, 'meta':['user-update', '--uup'], 'endpoint':'/admin/<api_token>/user/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['picture', '--pc'], 'endpoint':'/admin/<api_token>/user/picture/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['profile', '--pf'], 'endpoint':'/admin/<api_token>/profile/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST', 'UPDATE'], 'struct':{'fname':'string', 'lname':'string', 'picture':'string','organisation':'string','about':'string'}, 'meta':['profile-update', '--pup'], 'endpoint':'/admin/<api_token>/user/profile/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['token-update', '--tup'], 'endpoint':'/admin/<api_token>/user/token/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['projects', '--pj'], 'endpoint':'/admin/<api_token>/user/projects/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['records', '--re'], 'endpoint':'/admin/<api_token>/user/records/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/admin/<api_token>/user/comments/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['messages', '--me'], 'endpoint':'/admin/<api_token>/user/messages/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['apps', '--ap'], 'endpoint':'/admin/<api_token>/user/apps/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'developer':'<selected.id>','name':'string','about':'string','logo':'string','access':'string','access':'string','network':'string','visibile':'string'}, 'meta':['app-created', '--apc'], 'endpoint':'/admin/<api_token>/app/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'owner':'<selected.id>','encoding':'string','size':'string','name':'string','path':'string','storage':'string','location':'string','mimetype':'string','group':'string','description':'string'}, 'meta':['file-create', '--fic'], 'endpoint':'/admin/<api_token>/file/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'session':'<selected.session>','from':'string','to':'string','':'string','method':'string','resources':'list','proposition':'string','status':'string'}, 'meta':['diff-create', '--dic'], 'endpoint':'/admin/<api_token>/diff/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'group':'string', 'system':'string', 'specifics':'dict', 'version':'dict', 'bundle':'dict'}, 'meta':['env-create', '--enc'], 'endpoint':'/admin/<api_token>/env/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'project':'string','application':'string','parent':'string','label':'string','tags':'list','system':'dict','inputs':'list','outputs':'list','dependencies':'list','status':'string','environment':'string','cloned_from':'string','access':'string','resources':'list','rationels':'list'}, 'meta':['record-create', '--rrc'], 'endpoint':'/admin/<api_token>/record/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'application':'string','owner':'<selected.id>','name':'string','description':'string','goals':'string','tags':'list','access':'string','history':'list','original':'string','resources':'list','group':'string'}, 'meta':['project-create', '--pjc'], 'endpoint':'/admin/<api_token>/project/create'})
                # resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/<group>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'sender':'<selected.id>','receiver':'string','title':'string', 'content':'string', 'attachments':'list'}, 'meta':['message-create', '--mec'], 'endpoint':'/admin/<api_token>/message/create'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'fname':'string', 'lname':'string', 'picture':'string','organisation':'string','about':'string'}, 'meta':['profile-create', '--pfc'], 'endpoint':'/admin/<api_token>/user/profile/create/<selected.id>'})

                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = MessageModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Message'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/message/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'title':'string', 'content':'string', 'attachments':'list'}, 'meta':['show', '--up'], 'endpoint':'/admin/<api_token>/message/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET','DELETE'], 'struct':{}, 'meta':['show', '--de'], 'endpoint':'/admin/<api_token>/message/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = CommentModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Comment'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/comment/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'title':'string', 'content':'string'}, 'meta':['show', '--up'], 'endpoint':'/admin/<api_token>/comment/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET','DELETE'], 'struct':{}, 'meta':['show', '--de'], 'endpoint':'/admin/<api_token>/comment/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = ProjectModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Project'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/project/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST', 'UPDATE'], 'struct':{'application':'string','owner':'string','name':'string','description':'string','goals':'string','tags':'list','access':'string','history':'list','original':'string','resources':'list','group':'string'}, 'meta':['update', '--up'], 'endpoint':'/admin/<api_token>/project/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET', 'DELETE'], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/project/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['history', '--hi'], 'endpoint':'/admin/<api_token>/project/envs/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['head', '--he'], 'endpoint':'/admin/<api_token>/project/env/head/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'group':'string', 'system':'string', 'specifics':'dict', 'version':'dict', 'bundle':'dict'}, 'meta':['next', '--ne'], 'endpoint':'/admin/<api_token>/project/env/next/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/admin/<api_token>/project/comments/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['records', '--re'], 'endpoint':'/admin/<api_token>/project/records/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/admin/<api_token>/project/files/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET',], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/admin/<api_token>/project/download/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['logo', '--lo'], 'endpoint':'/admin/<api_token>/project/logo/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/project'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = RecordModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Record'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/record/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'project':'string','application':'string','parent':'string','label':'string','tags':'list','system':'dict','inputs':'list','outputs':'list','dependencies':'list','status':'string','environment':'string','cloned_from':'string','access':'string','resources':'list','rationels':'list'}, 'meta':['update', '--up'], 'endpoint':'/admin/<api_token>/record/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET','DELETE'], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/record/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['env', '--en'], 'endpoint':'/admin/<api_token>/record/env/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/admin/<api_token>/record/comments/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['diffs', '--di'], 'endpoint':'/admin/<api_token>/record/diffs/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/admin/<api_token>/record/files/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/admin/<api_token>/record/download/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/record'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = EnvironmentModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Environment'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/env/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST', 'UPDATE'], 'struct':{'group':'string', 'system':'string', 'specifics':'dict', 'version':'dict', 'bundle':'dict'}, 'meta':['update', '--up'], 'endpoint':'/admin/<api_token>/env/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET','DELETE'], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/env/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/admin/<api_token>/env/download/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/env'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = DiffModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Diff'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/diff/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'sender':'string','from':'string','to':'string','':'string','method':'string','resources':'list','proposition':'string','status':'string'}, 'meta':['update', '--up'], 'endpoint':'/admin/<api_token>/diff/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET','DELETE'], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/diff/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET',], 'struct':{}, 'meta':['comments', '--co'], 'endpoint':'/admin/<api_token>/diff/comments/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['files', '--fi'], 'endpoint':'/admin/<api_token>/diff/files/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/admin/<api_token>/diff/download/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/diff'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = FileModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'File'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/file/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'encoding':'string','size':'string','name':'string','path':'string','storage':'string','location':'string','mimetype':'string','group':'string','description':'string'}, 'meta':['update', '--ud'], 'endpoint':'/admin/<api_token>/file/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET',], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/file/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['download', '--do'], 'endpoint':'/admin/<api_token>/file/download/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST'], 'struct':{'item':'<selected.id>','title':'string', 'content':'string'}, 'meta':['comment-create', '--coc'], 'endpoint':'/admin/<api_token>/comment/file'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            item = ApplicationModel.objects.with_id(item_id)
            if item != None:
                resolution['type'] = 'Application'
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['show', '--sh'], 'endpoint':'/admin/<api_token>/app/show/<selected.id>'})
                resolution['endpoints'].append({'methods':['POST','UPDATE'], 'struct':{'developer':'string','name':'string','about':'string','logo':'string','access':'string','access':'string','network':'string','visibile':'string'}, 'meta':['update', '--up'], 'endpoint':'/admin/<api_token>/app/update/<selected.id>'})
                resolution['endpoints'].append({'methods':['FILE'], 'struct':{'file':'mimetype'}, 'meta':['upload', '--ul'], 'endpoint':'/admin/<api_token>/file/upload/<group>/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['delete', '--de'], 'endpoint':'/admin/<api_token>/app/delete/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['connectivity', '--co'], 'endpoint':'/admin/<api_token>/app/connectivity/<selected.id>'})
                resolution['endpoints'].append({'methods':['GET'], 'struct':{}, 'meta':['logo', '--lo'], 'endpoint':'/admin/<api_token>/app/logo/<selected.id>'})
                return api_response(200, 'Item %s resolution results'%item_id, resolution)

            if item == None:
                return api_response(404, 'Request suggested an empty response', 'Unable to find this diff.')
            else:
                return api_response(405, 'Method not allowed', 'This endpoint supports only a GET method.')