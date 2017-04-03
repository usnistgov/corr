import datetime
from ..core import db
import json
from bson import ObjectId
          
class BundleModel(db.Document):
    """CoRR backend bundle model.
    Meta-data about the environment bundle is stored in
    this model.

    Attributes:
        created_at: A string value of the creation timestamp.
        possible_scope: A list of all the possible places to get the bundle.
        scope: A string value of the current location with unknown as default.
        location: A string containing the url to the location of the bundle file.
        mimetype: A string the type/format of the bundle file.
        size: A Long value of the bundle size.
        extend: A dictionary of to add other fields to the bundle model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    possible_scope = ["local", "remote", "unknown"]
    scope = db.StringField(default="unknown", choices=possible_scope)
    location = db.StringField()
    mimetype = db.StringField()
    checksum = db.StringField()
    size = db.LongField()
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an bundle model instance content.
        Returns:
            The dictionary content of the bundle model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'scope':self.scope,
        'location':self.location, 'size':self.size, 'mimetype':self.mimetype}
        try:
            data["checksum"] = self.checksum
        except:
            self.checksum = ""
            self.save()
            data["checksum"] = self.checksum
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