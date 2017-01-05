import boto3
from io import StringIO
from io import BytesIO
import zipfile
import simplejson as json
import time
import traceback 
import datetime
import requests
import os
import glob

class StorageManager:
    def __init__(self, app):
        """Initializes a storage manager instance.
        """
        self.app = app
        self.config = app.config['FILE_STORAGE']
        if self.config['type'] == 's3':
            aws_path = '~/.aws'
            if not os.path.exists(aws_path):
                os.makedirs(aws_path)
                with open('{0}/config'.format(aws_path), 'w') as config_file:
                    config_file.write('[default]\nregion = {0}'.format(self.config['location']))
                with open('{0}/credentials'.format(aws_path), 'w') as credentials_file:
                    credentials_file.write('[default]\naws_access_key_id = {0}\naws_secret_access_key = {1}'.format(self.config['id'], self.config['key']))
            # Boto s3 instance
            self.s3 =  boto3.resource('s3')

            # S3 bucket location
            try:
                self.bucket = config['name']
            except:
                self.bucket = ""
        elif self.config['type'] == 'filesystem':
            self.storage_path = '{0}{1}'.format(self.config['location'], self.config['name'])
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)
                os.makedirs('{0}/corr-bundles'.format(self.storage_path))
                os.makedirs('{0}/corr-files'.format(self.storage_path))
                os.makedirs('{0}/corr-logos'.format(self.storage_path))
                os.makedirs('{0}/corr-outputs'.format(self.storage_path))
                os.makedirs('{0}/corr-pictures'.format(self.storage_path))
                os.makedirs('{0}/corr-resources'.format(self.storage_path))
        elif self.config['type'] == 'mdcs': # TODO
            pass
        elif self.config['type'] == 'ftp' or self.config['type'] == 'sftp' : # TODO
            pass

    def storage_get_file(self, group='', key=''):
        """Retreive a file from the file storage.
            Returns:
                File buffer.
        """
        try:
            obj = None
            content = None
            if key != '':
                if self.config['type'] == 's3':
                    obj = self.s3.Object(bucket_name=S3_BUCKET, key='corr-{0}s/{1}'.format(group,key))
                    res = obj.get()
                    content = res['Body'].read()
                elif self.config['type'] == 'filesystem':
                    with open('{0}/corr-{1}s/{2}'.format(self.storage_path, group, key), "rb") as obj:
                        content = obj.read()
            else:
                content = None

        except:
            print(traceback.print_exc())
            content = None

        try:
            if self.config['type'] == 's3':
                file_buffer = StringIO()
            elif self.config['type'] == 'filesystem':
                file_buffer = BytesIO()
            file_buffer.write(content)
            file_buffer.seek(0)
            return file_buffer
        except:
            self.app.logger.error(traceback.print_exc())
            print(traceback.print_exc())
            return None

    def storage_upload_file(self, file_meta=None, file_obj=None):
        """Upload a file into the s3 bucket.
            Returns:
                an array of two elements. one is the status
                of the upload and the other is a message 
                accompanying it.
        """
        if file_meta != None and file_obj != None:
            if file_meta.location == 'local':
                dest_filename = file_meta.storage
                try:
                    group = 'corr-resources'
                    if file_meta.group != 'descriptive':
                        group = 'corr-%ss'%file_meta.group
                    print(group)
                    if self.config['type'] == 's3':
                        s3_files = self.s3.Bucket(self.bucket)
                        s3_files.put_object(Key='{0}/{1}'.format(group, dest_filename), Body=file_obj.read())
                    elif self.config['type'] == 'filesystem':
                        self.app.logger.info('{0}/{1}/{2}'.format(self.storage_path, group, dest_filename))
                        print('{0}/{1}/{2}'.format(self.storage_path, group, dest_filename))
                        with open('{0}/{1}/{2}'.format(self.storage_path, group, dest_filename), "wb") as obj:
                            obj.write(file_obj.read())
                    return [True, "File uploaded successfully"]
                except:
                    self.app.logger.error(traceback.print_exc())
                    return [False, traceback.format_exc()]
            else:
                return [False, "Cannot upload a file that is remotely set. It has to be local targeted."]
        else:
            return [False, "file meta data does not exist or file content is empty."]

    def agent_delete(self, group, path):
        """Agent function that deletes a file in the storage.
            Returns:
                Deletion status of file.
        """
        found = False
        for file_path in glob.glob('{0}/corr-{1}s'.format(path, group)):
            if key in file_path:
                os.remove(file_path)
                found = True
                break
        return found

    def agent_prepare(self, zf, group, object_dict):
        """Agent function that prepares a dictionary for storage in a compressed files.
            Returns:
                Zipping status
        """
        object_buffer = StringIO()
        object_buffer.write(json.dumps(object_dict, sort_keys=True, indent=4, separators=(',', ': ')))
        object_buffer.seek(0)
        data = zipfile.ZipInfo("{0}.json".format(group))
        data.date_time = time.localtime(time.time())[:6]
        data.compress_type = zipfile.ZIP_DEFLATED
        data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
        return zf.writestr(data, object_buffer.read())

    def storage_delete_file(self, group='', key=''):
        """Delete a file from the s3 bucket.
            Returns:
                The status of the deletion. True for success
                and False for failure.
        """
        deleted = False
        if key not in ["default-logo.png", "default-picture.png"]:
            if self.config['type'] == 's3':
                s3_files = self.s3.Bucket(self.bucket)
                for _file in s3_files.objects.all():
                    if _file.key == 'corr-{0}s/{1}'.format(group, key): 
                        _file.delete()
                        print("File deleted!")
                        deleted = True
                        break
            elif self.config['type'] == 'filesystem':
                found = self.agent_delete('bundle', self.storage_path)
                if not found:
                    found = self.agent_delete('file', self.storage_path)
                if not found:
                    found = self.agent_delete('logo', self.storage_path)
                if not found:
                    found = self.agent_delete('output', self.storage_path)
                if not found:
                    found = self.agent_delete('picture', self.storage_path)
                if not found:
                    found = self.agent_delete('resource', self.storage_path)
            if not deleted:
                print("File not deleted")
        return deleted

    def delete_project_files(self, project):
        """Delete a project files.
        """
        from corrdb.common.models import FileModel
        from corrdb.common.models import EnvironmentModel

        for _file in project.resources:
            file_ = FileModel.objects.with_id(_file)
            if file_:
                result = self.storage_delete_file(file_.group, file_.storage)
                if result:
                    logStat(deleted=True, file_obj=file_)
                    file_.delete()

        for record in project.records:
            result = self.delete_record_files(record)
            if result:
                logStat(deleted=True, record=record)
                record.delete()

        for environment_id in project.history:
            _environment = EnvironmentModel.objects.with_id(environment_id)
            if _environment.bundle["scope"] == "local":
                result = self.storage_delete_file('bundle', _environment.bundle.location)
                if result:
                    logStat(deleted=True, bundle=_environment.bundle)
                    logStat(deleted=True, environment=_environment)
                    _environment.bundle.delete()
                    _environment.delete()
            else:
                logStat(deleted=True, environment=_environment)
            _environment.delete()

    def delete_record_files(self, record):
        """Delete a record files.
            Returns:
                True if all files are deleted.
        """
        from corrdb.common.models import FileModel
        final_result = True
        for _file_id in record.resources:
            _file = FileModel.objects.with_id(_file_id)
            result = self.delete_record_file(_file)
            if not result:
                final_result = result
        return final_result

    def delete_record_file(self, record_file):
        """Delete a record file and log the stats.
            Returns:
                Return of the storage_delete_file call.
        """
        result = self.storage_delete_file(record_file.group, record_file.storage)
        if result:
            logStat(deleted=True, file_obj=record_file)
            record_file.delete()
        return result

    def web_get_file(self, url):
        """Retrieve a externaly hosted file.
            Returns:
                File buffer.
        """
        try:
            print(url)
            response = requests.get(url, verify='/corr-ssl/corr.crt')
            file_buffer = BytesIO(response.content)
            file_buffer.seek(0)
            return file_buffer
        except:
            print(traceback.print_exc())
            return None

    def prepare_env(self, project=None, env=None):
        """Bundle a project's environment.
            Returns:
                Zip file buffer of the environment's content.
        """
        if project == None or env == None:
            return [None, '']
        else:
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w') as zf:
                if env.bundle != None and env.bundle.location != '':
                    try:
                        bundle_buffer = StringIO()
                        if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                            bundle_buffer = self.web_get_file(env.bundle.location)
                        else:
                            bundle_buffer = self.storage_get_file('bundle', env.bundle.location)

                        data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = zipfile.ZIP_DEFLATED
                        data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                        zf.writestr(data, bundle_buffer.read())
                    except:
                        print(traceback.print_exc())

                try:
                    json_buffer = StringIO()
                    json_buffer.write(env.to_json())
                    json_buffer.seek(0)

                    data = zipfile.ZipInfo("env.json")
                    data.date_time = time.localtime(time.time())[:6]
                    data.compress_type = zipfile.ZIP_DEFLATED
                    data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                    zf.writestr(data, json_buffer.read())
                except:
                    print(traceback.print_exc())
            memory_file.seek(0)

        return [memory_file, "project-%s-env-%s.zip"%(str(project.id), str(env.id))]

    def prepare_project(self, project=None):
        """Bundle an entire project
            Returns:
                Zip file buffer of the project's content.
        """
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
                    self.agent_prepare(zf, 'project', project_dict)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'comments', comments)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'resources', resources)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'environments', history)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'records', records)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'application', application)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'diffs', diffs)
                except:
                    print(traceback.print_exc())
            memory_file.seek(0)

        return [memory_file, "project-%s.zip"%str(project.id)]

    def prepare_record(self, record=None):
        """Bundle a record.
            Returns:
                Zip file buffer of a record's content.
        """
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
                    self.agent_prepare(zf, 'project', project)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'comments', comments)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'resources', resources)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'inputs', inputs)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'outputs', outputs)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'dependencies', dependencies)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'application', application)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'parent', parent)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'body', body)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'execution', execution)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'environment', environment)
                except:
                    print(traceback.print_exc())
                try:
                    self.agent_prepare(zf, 'record', record_dict)
                except:
                    print(traceback.print_exc())
                if env != None and env.bundle != None and env.bundle.location != '':
                    try:
                        bundle_buffer = StringIO()
                        if 'http://' in env.bundle.location or 'https://' in env.bundle.location:
                            bundle_buffer = self.web_get_file(env.bundle.location)
                        else:
                            bundle_buffer = self.storage_get_file('bundle', env.bundle.location)

                        data = zipfile.ZipInfo("bundle.%s"%(env.bundle.location.split("/")[-1].split(".")[-1]))
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = zipfile.ZIP_DEFLATED
                        data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                        zf.writestr(data, bundle_buffer.read())
                    except:
                        print(traceback.print_exc())
                for resource in resources:
                    try:
                        bundle_buffer = StringIO()
                        data = None
                        if 'http://' in resource['storage'] or 'https://' in resource['storage']:
                            bundle_buffer = self.web_get_file(resource['storage'])
                            data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage'].split('/')[-1]))
                        else:
                            bundle_buffer = self.storage_get_file(resource['group'], resource['storage'])
                            data = zipfile.ZipInfo("%s-%s"%(resource['group'], resource['storage']))
                        data.date_time = time.localtime(time.time())[:6]
                        data.compress_type = zipfile.ZIP_DEFLATED
                        data.external_attr |= 0o777 << 16 # -rwx-rwx-rwx
                        zf.writestr(data, bundle_buffer.read())
                    except:
                        print(traceback.print_exc())
                
            memory_file.seek(0)

        return [memory_file, "project-%s-record-%s.zip"%(str(record.project.id), str(record.id))]
        