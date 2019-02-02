import datetime
from ..core import db
import json
from bson import ObjectId
from ..models import BundleModel
from ..models import VersionModel
from ..models import CommentModel
from ..models import FileModel
from ..models import ApplicationModel

class EnvironmentModel(db.Document):
    """CoRR backend environment model.
    Model that represents how the environment is recorded.
    The environment can be computational, experimental or both.

    Attributes:
        created_at: A string value of the creation timestamp.
        application: A reference to the application that produced the environment.
        possible_group: A list of the possible nature of the environment.
        group: The environment current nature with unknown as default.
        possible_system: A list of possible systems on which is based the environment.
        system: A string value of teh system that caracterise the environment the best.
        specifics: A dictionary of the specifics about the system being used.
            {'container-system':'docker|rocket', 'container-version':'1.0'} |
            {'tool-system':'guilogger', 'tool-version':'1.0'} |
            {'device-system':'dft-machine', 'device-version':'electron 2700'}
        version: A reference to the version model of the environment.
        bundle: A reference to the bundle file model of the environment.
        comments: A list of the comments done on the environment resources.
        resources: A list of files associated to the environment.
        extend: A dictionary of to add other fields to the environment model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    application = db.ReferenceField(ApplicationModel)
    possible_group = ["computational", "experimental", "hybrid", "unknown"]
    group = db.StringField(default="unknown", choices=possible_group)
    possible_system = ["container-based", "vm-based", "tool-based", "cloud-based", "device-based", "lab-based", "custom-based", "undefined"]
    system = db.StringField(default="undefined", choices=possible_system)
    specifics = db.DictField()
    version = db.ReferenceField(VersionModel)
    bundle = db.ReferenceField(BundleModel)
    comments = db.ListField(db.StringField())
    resources = db.ListField(db.StringField())
    extend = db.DictField()

    def _comments(self):
        """Gather the environment comments.

        Returns:
          The environment comments.
        """
        comments = []
        for com_id in self.comments:
            com = CommentModel.objects.with_id(com_id)
            if com != None:
                comments.append(com)
        return comments

    def _resources(self):
        """Filter out the environment resources files.

        Returns:
          The environment files.
        """
        resources = []
        for f_id in self.resources:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                resources.append(f)
        return resources

    def info(self):
        """Build a dictionary structure of an environment model instance content.

        Returns:
          The dictionary content of the environment model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'group':self.group,
        'system':self.system, 'specifics':self.specifics}
        if self.application != None:
            data['application'] = self.application.info()
        else:
            data['application'] = {'id':None, 'name':'unknown'}
        if self.version != None:
            data['version'] = str(self.version.id)
        else:
            data['version'] = ''

        if self.bundle != None:
            data['bundle'] = str(self.bundle.id)
        else:
            data['bundle'] = '************************'

        data['comments'] = len(self.comments)
        data['resources'] = len(self.resources)

        return data

    def extended(self):
        """Add the extend, comments, resources, application, version, bundle fields
        to the built dictionary content.

        Returns:
          The augmented dictionary.
        """
        data = self.info()
        data['comments'] = [comment.extended() for comment in self._comments()]
        data['resources'] = [resource.extended() for resource in self._resources()]
        data['extend'] = self.extend
        if self.application != None:
            data['application'] = self.application.info()
        else:
            data['application'] = {}
        if self.version != None:
            data['version'] = self.version.extended()
        else:
            data['version'] = ''

        if self.bundle != None:
            data['bundle'] = self.bundle.extended()
        else:
            data['bundle'] = ''
        return data

    def to_json(self):
        """Transform the extended dictionary into a pretty json.

        Returns:
          The pretty json of the extended dictionary.
        """
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def summary_json(self):
        """Transform the info dictionary with comments, resources fields into a pretty json.

        Returns:
          The pretty json of the info dictionary. 
        """
        data = self.info()
        data['comments'] = len(self.comments)
        data['resources'] = len(self.resources)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
