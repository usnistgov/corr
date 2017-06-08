from ..core import db
from ..models import FileModel
from ..models import CommentModel
from ..models import ProjectModel
from ..models import EnvironmentModel
import datetime
import json
from bson import ObjectId

# TODO: for system field, look into providing os version, gpu infos, compiler infos.
# TODO: for preparation field, what are the steps to get this ready to be recorded.
# TODO: for the dependencies field, check for c++ libs here. {'type':lib|compiler|interpretor|language|software|prorietary}

class RecordModel(db.Document):
    """CoRR backend record model.
    The record model in the CoRR backend.

    Attributes:
        project: A reference to the record's project.
        parent: A reference to the record's parent if any (useful in case of distributed or parallel runs).
        label: A string value for the record label. Here we store the record id as its label.
        tags: A list of strings for tagging the reocrds.
        created_at: A string value of the creation timestamp.
        updated_at: A string value of the update timestamp.
        system: A dict value of the system meta-data in the record.
        execution: A dict value about how the investigation execution.
        preparation: A dict field about how the investigation was setup.
        inputs: A list of dict fields giving information about the investigation inputs.
        outputs: A list of dict fields giving information about the investigation outputs.
        dependencies: A list of dict fields giving information about the investigation dependencies.
        possible_status: A list of possible states in which the investigation can be at.
        status: A string value of the state at which the investigation is with unknown as default.
        environment: A reference to the record environment.
        cloned_from: A reference to another record in case it is recorded from another one.
        possible_access: A list of possible access policies for the record.
        access: A string value of the record current access policy with the default to private.
        resources: A list of files attached to the record.
        rationels: A list of strings representing the rationels around why the record was done.
        comments: A list of comments on the record resources.
        extend: A dictionary of to add other fields to the record model.
    """
    project = db.ReferenceField(ProjectModel, reverse_delete_rule=db.CASCADE, required=True)
    parent = db.StringField(max_length=256)
    label = db.StringField()
    tags = db.ListField(db.StringField())
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    system = db.DictField()
    execution = db.DictField()
    preparation = db.DictField()
    inputs = db.ListField(db.DictField())
    outputs = db.ListField(db.DictField())
    dependencies = db.ListField(db.DictField())
    possible_status = ["starting", "started", "paused", "sleeping", "finished", "crashed", "terminated", "resumed", "running", "unknown"]
    status = db.StringField(default="unknown", choices=possible_status)
    environment = db.ReferenceField(EnvironmentModel, reverse_delete_rule=db.CASCADE)
    cloned_from = db.StringField(max_length=256)
    possible_access = ["private", "protected", "public"]
    access = db.StringField(default="private", choices=possible_access)
    resources = db.ListField(db.StringField())
    rationels = db.ListField(db.StringField())
    comments = db.ListField(db.StringField())
    extend = db.DictField()

    def save(self, *args, **kwargs):
        """Overwite the record mongoengine save.
        Returns:
            The call to the mongoengine Document save function.
        """
        self.updated_at = str(datetime.datetime.utcnow())
        self.project.save()
        return super(RecordModel, self).save(*args, **kwargs)
    
    def update_fields(self, data):
        """Update the fields based on the data.
        """
        for k, v in self._fields.iteritems():
            if not v.required:
                if k != 'created_at':
                        yield k, v
    
    def update(self, data):
        """Overwite the record mongoengine update.
        """
        for k, v in self.update_fields(data):
            if k in data.keys():
                if k == 'created_at':
                    pass
                else:
                    setattr(self, k, data[k])
                del data[k]
        self.save()       
        if data:
            body, created = RecordBodyModel.objects.get_or_create(head=self)
            body.data.update(data)
            body.save()

    @property
    def body(self):
        """Retrieve the record body.
        Returns:
            The record body.
        """
        return RecordBodyModel.objects(head=self).first()

    @property
    def duration(self):
        """Compute the record duration.
        Returns:
            The record duration.
        """

        updated_strp = datetime.datetime.strptime(str(self.updated_at), '%Y-%m-%d %H:%M:%S.%f')
        # created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
        today_strp = datetime.datetime.strptime(str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f')
        value = today_strp-updated_strp
        return value

    def info(self):
        """Build a dictionary structure of an record model instance content.
        Returns:
            The dictionary content of the record model.
        """
        data = {}
        data['head'] = {'updated':str(self.updated_at),
         'id': str(self.id), 'duration': str(self.duration),
         'label': self.label, 'created':str(self.created_at), 'status' : self.status, 'access':self.access}

        if '0:00' in str(self.duration):
            data['head']['duration'] = 'few secondes'
        if self.project:
            data['head']['project'] = self.project.info()
        else:
            print("Orphan record.")
        data['head']['tags'] = ' '.join(self.tags)
        data['head']['comments'] = len(self.comments)
        data['head']['resources'] = len(self.resources)
        data['head']['inputs'] = len(self.inputs)
        data['head']['outputs'] = len(self.outputs)
        data['head']['dependencies'] = len(self.dependencies)
        data['head']['rationels'] = ' '.join(self.rationels)
        if self.environment != None:
            data['head']['environment'] = str(self.environment.id)
        else:
            data['head']['environment'] = None
        if self.parent != None:
            data['head']['parent'] = self.parent
        else:
            data['head']['parent'] = None
        if self.body != None:
            data['body'] = str(self.body.id)
        else:
            data['body'] = None
        return data

    def _comments(self):
        """Gather the project comments.
        Returns:
            The project comments.
        """
        comments = []
        for com_id in self.comments:
            com = CommentModel.objects.with_id(com_id)
            if com != None:
                comments.append(com)
        return comments

    def _resources(self):
        """Filter out the project resources files.
        Returns:
            The project files.
        """
        resources = []
        for f_id in self.resources:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                resources.append(f)
        return resources

    def extended(self):
        """Add the extend, system, execution, preparation, inputs, outputs, dependencies, comments,
        resources, rationels fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['head']['system'] = self.system
        data['head']['execution'] = self.execution
        data['head']['preparation'] = self.preparation
        data['head']['inputs'] = self.inputs
        data['head']['outputs'] = self.outputs
        data['head']['dependencies'] = self.dependencies
        data['head']['comments'] = [comment.extended() for comment in self._comments()]
        data['head']['resources'] = [resource.extended() for resource in self._resources()]
        if self.environment != None:
            if self.environment.application != None:
                data['head']['application'] = self.environment.application.extended()
            else:
                data['head']['application'] = {}
        else:
            data['head']['application'] = {}
        data['extend'] = self.extend
        if self.environment != None:
            data['head']['environment'] = self.environment.extended()
        else:
            data['head']['environment'] = {}
        if self.parent != None and self.parent != '':
            data['head']['parent'] = RecordModel.objects.with_id(self.parent).info()
        else:
            data['head']['parent'] = {}
        if self.body != None:
            data['body'] = self.body.extended()
        else:
            data['body'] = {}
        return data

    def to_json(self):
        """Transform the extended dictionary into a pretty json.
        Returns:
            The pretty json of the extended dictionary.
        """
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        """Transform the info dictionary with inputs, outputs, dependencies, comments, resources, rationels fields into a pretty json.
        Returns:
            The pretty json of the info dictionary. 
        """
        data = self.info()
        data['head']['inputs'] = len(self.inputs)
        data['head']['outputs'] = len(self.outputs)
        data['head']['dependencies'] = len(self.dependencies)
        data['head']['comments'] = len(self.comments)
        data['head']['resources'] = len(self.resources)
        data['head']['rationels'] = '.'.join(self.rationels)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

class RecordBodyModel(db.Document):
    """CoRR backend record body model.
    This model contains anything else that cannot fit into the record head.
    It is in some sense regarding the other models the extend class for the record.
    But is not a simple extend as all the heavy meta-data should be put here to
    leave the record head light weight.

    Attributes:
        updated_at: A string value of the creation timestamp.
        head: A reference to the record model.
        extend: A dictionary of to add other fields to the reocrd body model.
    """
    updated_at = db.StringField(default=str(datetime.datetime.utcnow()))
    head = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, unique=True, required=True)
    data = db.DictField()
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an record body model instance content.
        Returns:
            The dictionary content of the record body model.
        """
        data = {}
        data['head'] = str(self.head.id)
        data['body'] = {'updated':str(self.updated_at), 'id':str(self.id), 'content':self.data}
        return data

    def extended(self):
        """Add the extend field to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['extend'] = self.extend
        return data

    def to_json(self):
        """Transform the extended dictionary into a pretty json.
        Returns:
            The pretty json of the extended dictionary.
        """
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def summary_json(self):
        """Transform the info dictionary into a pretty json.
        Returns:
            The pretty json of the info dictionary. 
        """
        data = self.info()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


        

