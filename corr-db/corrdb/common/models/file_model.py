from ..core import db
import datetime
import json
from bson import ObjectId
from ..models import UserModel

class FileModel(db.Document):
    """CoRR backend file model.
    Model that represents the meta-data about a file in CoRR.

    Attributes:
        created_at: A string value of the creation timestamp.
        owner: A reference to the owner of the file.
        encoding: A string value of the file encoding.
        mimetype: A string value of the file type/format.
        size: A Long value of the file size.
        name: A string holding the file name.
        path: A string containing the file origin path.
        storage: A string value of the location.
        possible_location: A list of the file storage type.
        location: A string value of the file current location with undefined as default.
        possible_group: A list of possible CoRR tags to which the file can be associated to.
        group: A string value of the current tag (in terme of utility) with undefined as default.
        description: A string value of the file description.
        extend: A dictionary of to add other fields to the file model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    owner = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE)
    encoding = db.StringField()
    mimetype = db.StringField()
    size = db.LongField()
    name = db.StringField()
    path = db.StringField()
    storage = db.StringField()
    possible_location = ["local", "remote", "undefined"]
    location = db.StringField(default="undefined", choices=possible_location)
    possible_group = ["file", "bundle", "input", "output", "dependencie", "descriptive", "diff", "attach", "picture" , "logo" , "resource", "undefined"]
    group = db.StringField(default="undefined", choices=possible_group)
    description = db.StringField()
    extend = db.DictField()


    def info(self):
        """Build a dictionary structure of an file model instance content.
        Returns:
            The dictionary content of the file model.
        """
        data = {'created_at':str(self.created_at), 'id': str(self.id), 
        'name':self.name, 'encoding':self.encoding, 'mimetype': self.mimetype, 'size': self.size, 'storage': self.storage, 'location':self.location}
        if self.owner != None:
            data['owner'] = str(self.owner.id)
        else:
            data['owner'] = 'public'
        return data

    def extended(self):
        """Add the extend, storage, group, description, owner fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['storage'] = self.storage
        data['group'] = self.group
        data['description'] = self.description
        data['extend'] = self.extend
        if self.owner != None:
            data['owner'] = self.owner.info()
        else:
            data['owner'] = 'public'
        return data

    def to_json(self):
        """Transform the extended dictionary into a pretty json.
        Returns:
            The pretty json of the extended dictionary.
        """
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
    
    def summary_json(self):
        """Transform the info dictionary with comments field into a pretty json.
        Returns:
            The pretty json of the info dictionary. 
        """
        data = self.info()
        data['comments'] = len(self.comments)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))