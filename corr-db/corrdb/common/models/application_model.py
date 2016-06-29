import datetime
from ..core import db
import json
from bson import ObjectId

from ..models import UserModel
from ..models import FileModel
import hashlib
          
class ApplicationModel(db.Document):
    """CoRR backend application model.
    Information concerning a simulation management tool.
    An application developer will most likely register 
    the app to allow users to push records using the 
    appropriate API key.

    Attributes:
        created_at: A string value of the creation timestamp.
        developer: A reference to the application developer.
        name: A string containing the application's name.
        about: A string content of the application description.
        logo: A reference to the application logo file.
        possible_access: A list of the application possible access.
        access: A string indicating the access state of the application.
        app_token: A string holding the application access credential.
        users: A list of all the users that push records with this application.
        resources: A list of file resources associated to the application.
        storage: A long value of the total amount of data pushed with this application.
        network: A String value for the application ip address if online.
        visibile: A boolean indicating if the application can be viewed in queries results.
        extend: A dictionary of to add other fields to the application model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    developer = db.ReferenceField(UserModel, required=True)
    name = db.StringField(required=True, unique=True)
    about = db.StringField()
    logo = db.ReferenceField(FileModel)
    possible_access = ["activated", "blocked", "deactivated"]
    access = db.StringField(default="deactivated", choices=possible_access)
    app_token = db.StringField(max_length=256, unique=True)
    users = db.ListField(db.StringField())
    resources = db.ListField(db.StringField())
    storage = db.LongField()
    network = db.StringField(default="0.0.0.0")
    visibile = db.BooleanField(default=False)
    extend = db.DictField()

    def _users(self):
        """Gather all the users that used the application.
        Returns:
            The users that used the application.
        """
        users = []
        for u_id in self.users:
            u = UserModel.objects.with_id(u_id)
            if u != None:
                users.append(u)
        return users

    def _resources(self):
        """Extract all the files associated as resources to the applicatin.
        Returns:
            The files list.
        """
        resources = []
        for f_id in self.resources:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                resources.append(f)
        return resources

    def save(self, *args, **kwargs):
        """Overwrite the save function of the application mongoengine Document.
        Returns:
            The call to the based mongoengine Document save function.
        """
        if not self.app_token:
            self.app_token = hashlib.sha256(b'CoRRApp_%s'%(str(datetime.datetime.utcnow()))).hexdigest()

        return super(ApplicationModel, self).save(*args, **kwargs)

    def retoken(self):
        """Regenerates the application api token.
        """
        self.api_token = hashlib.sha256(b'CoRRApp_%s_%s'%(str(self.developer.id), str(datetime.datetime.utcnow()))).hexdigest()
        self.save()

    def info(self):
        """Build a dictionary structure of an application model instance content.
        Returns:
            The dictionary content of the application model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'developer':str(self.developer.id), 'name':self.name,
        'about':self.about, 'access':self.access, 'network':self.network, 'visibile':self.visibile}
        if self.logo != None:
            data['logo'] = str(self.logo.id)
        else:
            data['logo'] = ''
        data['resources'] = len(self.resources)
        return data

    def extended(self):
        """Add the extend, resources, token, users, storage fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['resources'] = [resource.extended() for resource in self._resources()]
        data['extend'] = self.extend
        data['token'] = self.app_token
        data['users'] = self._users()
        data['storage'] = self.storage
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