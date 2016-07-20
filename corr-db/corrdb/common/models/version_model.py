import datetime
from ..core import db
import json
from bson import ObjectId
          
class VersionModel(db.Document):
    """CoRR backend version model.
    The model holding the environment version.

    Attributes:
        created_at: A string value of the creation timestamp.
        possible_system: A list of possible versioning systems.
        system: A string value of the current versioning system with unknown as default.
        baseline: A string value of version base line  and in most systems it's branches.
        marker: A string value of the version hash and in most systems it's the commit hash.
        extend: A dictionary of to add other fields to the version model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    possible_system = ["git", "mercurial", "subversion", "cvs", "bazaar", "arch", "monotone", "aegis", "fastcst", "opencm", "vesta", "codeville", "darcs", "bitkeeper", "perforce", "clearcase" , "unknown"]
    system = db.StringField(default="unknown", choices=possible_system)
    baseline = db.StringField()
    marker = db.StringField()
    extend = db.DictField()

    def clone(self):
        del self.__dict__['_id']
        del self.__dict__['_created']
        del self.__dict__['_changed_fields']
        self.id = ObjectId()

    def info(self):
        """Build a dictionary structure of an version model instance content.
        Returns:
            The dictionary content of the version model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'system':self.system,
        'baseline':self.baseline, 'marker':self.marker}
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