# The api module
import flask as fk
from corrdb.common.core import setup_app
from corrdb.common.models import UserModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import ApplicationModel 
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel  
from corrdb.common.models import AccessModel     
import tempfile
import tarfile
from StringIO import StringIO
import zipfile
from io import BytesIO
import os
import json
import difflib
import hashlib
import datetime
import boto3
import traceback

import requests
from datetime import date, timedelta
from functools import update_wrapper
from calendar import monthrange
import time

# from difflib_data import *

app = setup_app(__name__)

s3 =  boto3.resource('s3')


# from flask.ext.stormpath import StormpathManager

# stormpath_manager = StormpathManager(app)

def check_api(token):
    for user in UserModel.objects():
        print "%s -- %s." %(user.email, user.api_token)
    return UserModel.objects(api_token=token).first()

def check_app(token):
    for application in ApplicationModel.objects():
        print "%s -- %s." %(str(application.developer.id), application.name)
    return ApplicationModel.objects(app_token=token).first()

def check_admin(token):
    user_model = UserModel.objects(api_token=token).first()
    if user_model == None:
        return None
    else:
        print user_model.group
        return user_model if user_model.group == "admin" else None

# def docker_gen(current_user, project):
#     docker_tar = tarfile.open("/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar", "w")
#     # print project.docker
#     # print project.requirements
#     if project.docker != "":
#         dockerfile = open("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile", "w")
#         dockerfile.write(project.docker)
#         dockerfile.close()
#         docker_tar.add("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile", "Dockerfile")
#     if project.requirements != "":
#         required_libs = open("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt", "w")
#         required_libs.write(project.requirements)
#         required_libs.close()
#         docker_tar.add("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt", "requirements.txt")
#     docker_tar.close()
#     try:
#       os.remove("/tmp/"+str(current_user.id)+"-"+project.name+"-Dockerfile")
#       os.remove("/tmp/"+str(current_user.id)+"-"+project.name+"-requirements.txt")
#     except:
#       pass

#     comp_buffer = StringIO()
#     with open("/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar", 'rb') as fh:
#         comp_buffer.write(fh.read())
#     comp_buffer.seek(0)
#     return [comp_buffer, "/tmp/"+str(current_user.id)+"-"+project.name+"-docker.tar"]

# def upload_image(current_user, container, file_obj):
#     dest_filename = str(current_user.id)+"-"+str(container.id)+"_%s"%file_obj.filename #kind is record| signature

#     print "About to write..."
#     # with open(dest_filename, 'wb') as fh:
#     #     # print "Content: %s" %file_obj.read()
#     #     # file_obj.seek(0)
#     #     fh.write(file_obj.read())

#     try:
#         s3.Bucket('reproforge-images').put_object(Key=str(current_user.id)+"-"+str(container.id)+"_%s"%file_obj.filename, Body=file_obj.read())
#         container.image['location'] = dest_filename
#         container.image['size'] = file_obj.tell()
#         print "%s saving..."%file_obj.filename
#         container.save()
#         return True
#         # s3_client = boto3.client('s3')
#         # print s3_client.get_bucket_location(Bucket='ddsm-bucket')
#         # s3_client.put_object(Bucket='ddsm-bucket', Key=str(current_user.id)+"-"+str(container.id)+"-%s.tar"%kind, Body=file_obj.read())
#     except:
#         return False
#         print traceback.print_exc()

    # container.image['location'] = dest_filename
    # container.image['size'] = file_obj.tell()
    # if kind == "binary":
    #     record.image['binary'] = {'type':'executable', 'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    # if kind == "source":
    #     record.image['source'] = {'type':'code', 'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    # if kind == "signature":
    #     record.signature = {'location':dest_filename, 'size':os.path.getsize(dest_filename)}
    # print "%s saving..."%kind
    # container.save()

# def upload_file(current_user, file_model, file_obj):
#     dest_filename = str(current_user.id)+"-"+str(file_model.record.id)+"_%s"%file_obj.filename #kind is record| signature

#     print "About to write..."
#     # with open(dest_filename, 'wb') as fh:
#     #     # print "Content: %s" %file_obj.read()
#     #     # file_obj.seek(0)
#     #     fh.write(file_obj.read())

#     try:
#         s3.Bucket('reproforge-files').put_object(Key=str(current_user.id)+"-"+str(record.id)+"_%s"%file_obj.filename, Body=file_obj.read())
#         file_model.location = dest_filename
#         file_model.size = file_obj.tell()
#         print "%s saving..."%file_obj.filename
#         container.save()
#         # s3_client = boto3.client('s3')
#         # print s3_client.get_bucket_location(Bucket='ddsm-bucket')
#         # s3_client.put_object(Bucket='ddsm-bucket', Key=str(current_user.id)+"-"+str(container.id)+"-%s.tar"%kind, Body=file_obj.read())
#         return True
#     except:
#         return False
#         print traceback.print_exc()

# def upload_picture(current_user, file_obj):
#     dest_filename = str(current_user.id)+".%s"%file_obj.filename.split('.')[1] #kind is record| signature

#     print "About to write..."
#     # with open(dest_filename, 'wb') as fh:
#     #     # print "Content: %s" %file_obj.read()
#     #     # file_obj.seek(0)
#     #     fh.write(file_obj.read())

#     try:
#         s3.Bucket('reproforge-pictures').put_object(Key=str(current_user.id)+".%s"%file_obj.filename.split('.')[1], Body=file_obj.read())
#         print "%s saving..."%file_obj.filename
#         container.save()
#         # s3_client = boto3.client('s3')
#         # print s3_client.get_bucket_location(Bucket='ddsm-bucket')
#         # s3_client.put_object(Bucket='ddsm-bucket', Key=str(current_user.id)+"-"+str(container.id)+"-%s.tar"%kind, Body=file_obj.read())
#         return True
#     except:
#         return False
        # print traceback.print_exc()

# def against_handler(current_user, record, file_obj):
#     ref_name = os.path.join('/tmp/', record.project.name+"-"+str(record.id)+"-against-"+hashlib.sha256(b'Against%s_%s'%(str(record.id), str(datetime.datetime.now))).hexdigest()+".tar")
#     with open(ref_name, 'wb') as fh:
#         fh.write(file_obj.read())

#     ref_tar = tarfile.open(ref_name)
#     base_tar = tarfile.open(record.signature['location'])
#     exploded = {}
#     exploded["reference"] = validate_signature(ref_tar)
#     exploded["base"] = validate_signature(base_tar)
#     print str(exploded)

#     base_signature = load_signature(record)
#     base_signature[0].seek(0)
#     # print "Base: %s"%base_signature[0].read()
#     ref_buffer = StringIO()
#     with open(ref_name, 'rb') as fh:
#         ref_buffer.write(fh.read())
#     ref_buffer.seek(0)
#     # print "Reference: %s"%ref_buffer.read() 
    

#     # d = difflib.Differ()
#     # diff = difflib.unified_diff(base, ref)

#     ratio = difflib.SequenceMatcher(None, base_signature[0].readlines(), ref_buffer.readlines()).ratio()

#     if ratio == 1.0:
#         record.repeated = record.repeated + 1
#         record.save()
#         return json.dumps({'conclusion':'repeated', 'distance': ratio})
#     else:
#         print "More complicated. We need to split the tar file compare the inputs and the outputs and generate the matrix or reproducibility."
#         # record.repeated = record.repeated + 1 if same input, same output
#         # record.reproduced = record.reproduced + 1 if different input, same output

#         # record.repeated = -1 if same input, different output
#         # print '\n'.join(list(diff))
    
#         return json.dumps({'conclusion':'complex', 'distance': ratio})

# def load_image(container):
#     image_buffer = StringIO()
#     with open(container.image['location'], 'rb') as fh:
#         image_buffer.write(fh.read())
#     image_buffer.seek(0)
#     return [image_buffer, container.image['location']]

# def load_signature(record):
#     signature_buffer = StringIO()
#     with open(record.signature['location'], 'rb') as fh:
#         signature_buffer.write(fh.read())
#     signature_buffer.seek(0)
#     return [signature_buffer, record.signature['location']]

# def validate_signature(tar):
#     members = []
#     for member in tar.getmembers():
#         f=tar.extractfile(member)
#         content=f.read()
#         members.append({"name":member.name, "content":content})
#         print "%s has %d newlines" %(member, content.count("\n"))
#         print "%s has %d spaces" % (member,content.count(" "))
#         print "%s has %d characters" % (member, len(content))
#     tar.close()
#     return members

def load_bundle(record):
    # Include record files later.
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:

        try:
            bundle_buffer = StringIO()
            # with open(record.container.image['location'], 'rb') as fh:
            #     image_buffer.write(fh.read())
            # res = key.get_contents_to_filename(record.container.image['location'])   
            # s3_client = boto3.client('s3')
            # res = s3_client.get_object(Bucket='ddsm-bucket', Key=record.container.image['location']) 
            obj = s3.Object(bucket_name='reproforge-bundles', key=record.environment.bundle['location'])  
            res = obj.get()      
            bundle_buffer.write(res['Body'].read())
            bundle_buffer.seek(0)

            data = zipfile.ZipInfo("%s"%(record.project.name, record.environment.bundle['location'].split('_')))
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
            zf.writestr(data, bundle_buffer.read())
        except:
            print traceback.print_exc()

        try:
            json_buffer = StringIO()
            json_buffer.write(record.to_json())
            json_buffer.seek(0)

            data = zipfile.ZipInfo("%s_%s.json"%(record.project.name, str(record.id)))
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED
            data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
            zf.writestr(data, json_buffer.read())
        except:
            print traceback.print_exc()
    memory_file.seek(0)


    # imz.append('record.tar', image_buffer.read()).append("record.json", json_buffer.read())

    # print record.container.image['location'].split("/")[-1].split(".")[0]+".zip"

    return [memory_file, record.environment.bundle['location'].split("/")[-1].split(".")[0]+".zip"]

def prepare_env(project=None, env=None):
    if project == None or env == None:
        return [None, '']
    else:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            if env.bundle.location != '':
                try:
                    bundle_buffer = StringIO()
                    if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                        bundle_buffer = web_get_file(env.bundle.location)
                    else:
                        bundle_buffer = s3_get_file('bundle', env.bundle.location)

                    data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()

            try:
                json_buffer = StringIO()
                json_buffer.write(env.to_json())
                json_buffer.seek(0)

                data = zipfile.ZipInfo("env.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
        memory_file.seek(0)

    return [memory_file, "project-%s-env-%s.zip"%(str(project.id), str(env.id))]

def prepare_project(project=None):
    if project == None:
        return [None, '']
    else:
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            project_dict = project.compress()
            comments = project_dict['comments']
            del project_dict['comments']
            resources = project_dict['resources']
            del project_dict['resources']
            history = project_dict['history']
            del project_dict['history']
            records = project_dict['records']
            del project_dict['records']
            diffs = project_dict['diffs']
            del project_dict['diffs']
            application = project_dict['application']
            del project_dict['application']
            try:
                project_buffer = StringIO()
                project_buffer.write(json.dumps(project_dict, sort_keys=True, indent=4, separators=(',', ': ')))
                project_buffer.seek(0)
                data = zipfile.ZipInfo("project.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, project_buffer.read())
            except:
                print traceback.print_exc()
            try:
                comments_buffer = StringIO()
                comments_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                comments_buffer.seek(0)
                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, comments_buffer.read())
            except:
                print traceback.print_exc()
            try:
                resources_buffer = StringIO()
                resources_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                resources_buffer.seek(0)
                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, resources_buffer.read())
            except:
                print traceback.print_exc()
            try:
                history_buffer = StringIO()
                history_buffer.write(json.dumps(history, sort_keys=True, indent=4, separators=(',', ': ')))
                history_buffer.seek(0)
                data = zipfile.ZipInfo("environments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, history_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(records, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("records.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
            try:
                records_buffer = StringIO()
                records_buffer.write(json.dumps(diffs, sort_keys=True, indent=4, separators=(',', ': ')))
                records_buffer.seek(0)
                data = zipfile.ZipInfo("diffs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, records_buffer.read())
            except:
                print traceback.print_exc()
        memory_file.seek(0)

    return [memory_file, "project-%s.zip"%str(project.id)]

def prepare_record(record=None):
    if record == None:
        return [None, '']
    else:
        env = record.environment
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            record_dict = record.extended()
            environment = record_dict['head']['environment']
            del record_dict['head']['environment']
            comments = record_dict['head']['comments']
            del record_dict['head']['comments']
            resources = record_dict['head']['resources']
            del record_dict['head']['resources']
            inputs = record_dict['head']['inputs']
            del record_dict['head']['inputs']
            outputs = record_dict['head']['outputs']
            del record_dict['head']['outputs']
            dependencies = record_dict['head']['dependencies']
            del record_dict['head']['dependencies']
            application = record_dict['head']['application']
            del record_dict['head']['application']
            parent = record_dict['head']['parent']
            del record_dict['head']['parent']
            body = record_dict['body']
            del record_dict['body']
            execution = record_dict['head']['execution']
            del record_dict['head']['execution']
            project = record.project.info()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(project, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("project.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(comments, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("comments.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(resources, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("resources.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(inputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("inputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(outputs, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("outputs.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(dependencies, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("dependencies.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(application, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("application.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(parent, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("parent.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(body, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("body.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(execution, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("execution.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(environment, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)

                data = zipfile.ZipInfo("environment.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            try:
                json_buffer = StringIO()
                json_buffer.write(json.dumps(record_dict, sort_keys=True, indent=4, separators=(',', ': ')))
                json_buffer.seek(0)
                data = zipfile.ZipInfo("record.json")
                data.date_time = time.localtime(time.time())[:6]
                data.compress_type = zipfile.ZIP_DEFLATED
                data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                zf.writestr(data, json_buffer.read())
            except:
                print traceback.print_exc()
            if env != None and env.bundle.location != '':
                try:
                    bundle_buffer = StringIO()
                    if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                        bundle_buffer = web_get_file(env.bundle.location)
                    else:
                        bundle_buffer = s3_get_file('bundle', env.bundle.location)

                    data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()
            for resource in resources:
                try:
                    bundle_buffer = StringIO()
                    data = None
                    if 'http://' in resource['storage'] or 'https://' in resource['storage']:
                        bundle_buffer = web_get_file(resource['storage'])
                        data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage'].split('/')[-1]))
                    else:
                        bundle_buffer = s3_get_file(resource['group'], resource['storage'])
                        data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage']))
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0777 << 16L # -rwx-rwx-rwx
                    zf.writestr(data, bundle_buffer.read())
                except:
                    print traceback.print_exc()
            
        memory_file.seek(0)

    return [memory_file, "project-%s-record-%s.zip"%(str(record.project.id), str(record.id))]

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and fk.request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = fk.make_response(f(*args, **kwargs))
            if not attach_to_all and fk.request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def upload_bundle(current_user, environment, file_obj):
    dest_filename = str(current_user.id)+"-"+str(environment.id)+"_%s"%file_obj.filename #kind is record| signature

    print "About to write..."
    try:
        s3.Bucket('reproforge-bundles').put_object(Key=str(current_user.id)+"-"+str(environment.id)+"_%s"%file_obj.filename, Body=file_obj.read())
        environment.bundle['location'] = dest_filename
        environment.bundle['size'] = file_obj.tell()
        print "%s saving..."%file_obj.filename
        environment.save()
        return True
    except:
        print traceback.print_exc()
        return False

def delete_project_files(project):
    s3_files = s3.Bucket('reproforge-pictures')
    s3_bundles = s3.Bucket('reproforge-bundles')

    from corrdb.common.models import ProjectModel
    from corrdb.common.models import RecordModel
    from corrdb.common.models import EnvironmentModel
    from corrdb.common.models import FileModel

    for record in project.records:
        for _file in record.files:
            s3_files.delete_key(_file.location)

    for environment_id in project.history:
        _environment = EnvironmentModel.objects.with_id(environment_id)
        if _environment.bundle["scope"] == "local":
            s3_bundles.delete_key(_environment.bundle["location"])
        del _environment

def delete_record_files(record):
    s3_files = s3.Bucket('reproforge-pictures')

    from corrdb.common.models import RecordModel
    from corrdb.common.models import FileModel

    for record in project.records:
        for _file in record.files:
            s3_files.delete_key(_file.location)

def api_response(code, title, content):
    import flask as fk
    response = {'code':code, 'title':title, 'content':content}
    # print response
    return fk.Response(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')), mimetype='application/json')

def s3_upload_file(file_meta=None, file_obj=None):
    if file_meta != None and file_obj != None:
        if file_meta.location == 'local':
            dest_filename = file_meta.storage
            try:
                group = 'corr-resources'
                if file_meta.group != 'descriptive':
                    group = 'corr-%ss'%file_meta.group
                # print group
                s3_files = s3.Bucket(group)
                s3_files.put_object(Key=dest_filename, Body=file_obj.read())
                return [True, "File uploaded successfully"]
            except:
                return [False, traceback.format_exc()]
        else:
            return [False, "Cannot upload a file that is remotely set. It has to be local targeted."]
    else:
        return [False, "file meta data does not exist or file content is empty."]

def s3_get_file(group='', key=''):
    file_buffer = StringIO()
    try:
        obj = None
        if key != '':
            obj = s3.Object(bucket_name='corr-%ss'%group, key=key)
        else:
            if group == 'picture' or group == 'logo':
                obj = s3.Object(bucket_name='corr-%ss'%group, key='default-%s.png'%group)
    except:
        if group == 'picture' or group == 'logo':
            obj = s3.Object(bucket_name='corr-logos', key='default-%s.png'%group)

    try:
        res = obj.get()
        file_buffer.write(res['Body'].read())
        file_buffer.seek(0)
        return file_buffer
    except:
        return None

def s3_delete_file(group='', key=''):
    if key not in ["default-logo.png", "default-picture.png"]:
        s3_files = s3.Bucket('corr-%ss'%group)
        for _file in s3_files.objects.all():
            if _file.key == key: 
                _file.delete()
                break

# def s3_delete_logo(key=''):
#     s3_files = s3.Bucket('corr-logos')
#     s3_files.delete_key(key)

# def s3_get_logo(key=''):
#     logo_buffer = StringIO()
#     try:
#         if key != '':
#             obj = s3.Object(bucket_name='corr-logos', key=key)
#         else:
#             obj = s3.Object(bucket_name='corr-logos', key='app-default-logo.png')
#     except:
#         obj = s3.Object(bucket_name='corr-logos', key='app-default-logo.png')

#     try:
#         res = obj.get()
#         logo_buffer.write(res['Body'].read())
#         logo_buffer.seek(0)
#         return logo_buffer
#     except:
#         return None

# def s3_delete_picture(key=''):
#     s3_files = s3.Bucket('corr-pictures')
#     s3_files.delete_key(key)

def data_pop(data=None, element=''):
    if data != None:
        try:
            del data[element]
        except:
            pass

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

# def s3_get_picture(key=''):
#     picture_buffer = StringIO()
#     try:
#         if key != '':
#             obj = s3.Object(bucket_name='corr-pictures', key=key)
#         else:
#             obj = s3.Object(bucket_name='corr-pictures', key='user-default-picture.png')
#     except:
#         obj = s3.Object(bucket_name='corr-pictures', key='user-default-picture.png')

#     if obj.get()['Body'].read() == None:
#         obj = s3.Object(bucket_name='corr-pictures', key='user-default-picture.png')
#     try:
#         res = obj.get()
#         picture_buffer.write(res['Body'].read())
#         picture_buffer.seek(0)
#         return picture_buffer
#     except:
#         return None

def web_get_file(url):
    try:
        response = requests.get(url)
        picture_buffer = StringIO(response.content)
        picture_buffer.seek(0)
        return picture_buffer
    except:
        return None


API_VERSION = 0.1
API_URL = '/api/v{0}'.format(API_VERSION)

def logTraffic(endpoint=''):
    # created_at=datetime.datetime.utcnow()
    (traffic, created) = TrafficModel.objects.get_or_create(service="api", endpoint="%s%s"%(API_URL, endpoint))
    if not created:
        traffic.interactions += 1 
        traffic.save()
    else:
        traffic.interactions = 1
        traffic.save()

def logAccess(app=None, scope='root', endpoint=''):
    (traffic, created) = AccessModel.objects.get_or_create(application=app, scope=scope, endpoint="%s%s"%(API_URL, endpoint))

def logStat(deleted=False, user=None, message=None, application=None, project=None, record=None, diff=None, file_obj=None, comment=None):
    category = ''
    periode = ''
    traffic = 0
    interval = ''
    today = datetime.date.today()
    last_day = monthrange(today.year, today.month)[1]

    if user != None:
        category = 'user'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if project != None:
        category = 'project'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if application != None:
        category = 'application'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if message != None:
        category = 'message'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if record != None:
        category = 'record'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if diff != None:
        category = 'collaboration'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)

    if file_obj != None:
        category = 'storage'
        periode = 'daily'
        traffic = file_obj.size * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if comment != None:
        category = 'comment'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    #created_at=datetime.datetime.utcnow()
    (stat, created) = StatModel.objects.get_or_create(interval=interval, category=category, periode=periode)
    if not created:
        if (stat.traffic + traffic) >= 0:
            stat.traffic += traffic
        stat.save()
    else:
        stat.traffic = traffic
        stat.save()


import endpoints
