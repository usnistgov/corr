import datetime
from ..core import db
from ..models import UserModel
from ..models import FileModel
import json
from bson import ObjectId
          
class ProfileModel(db.Document):
    """CoRR backend profile model.
    The model holding the user profile.

    Attributes:
        created_at: A string value of the creation timestamp.
        user: A reference to the user model.
        fname: A string value for the user first name.
        lname: A string value for the user last name.
        picture: A reference to the user profile picture.
        organisation: A string value to the user organisation.
        about: A string value to a description about the user.
        extend: A dictionary of to add other fields to the profile model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    user = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    fname = db.StringField(required=True)
    lname = db.StringField(required=True)
    picture = db.ReferenceField(FileModel)
    organisation = db.StringField(default="No organisation provided")
    about = db.StringField(default="Nothing about me yet.")
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an profile model instance content.
        Returns:
            The dictionary content of the profile model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 
        'user':str(self.user.id), 'fname': self.fname, 'lname': self.lname}
        if self.picture != None:
            data['picture'] = str(self.picture.id)
        else:
            data['picture'] = None
        return data

    def extended(self):
        """Add the extend, organisation, about fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['organisation'] = self.organisation
        data['about'] = self.about
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
        """Transform the info dictionary with organisation, about fields into a pretty json.
        Returns:
            The pretty json of the info dictionary. 
        """
        data = self.info()
        data['organisation'] = self.organisation
        if self.about != None:
            data['about'] = self.about[0:96]+"..." if len(self.about) >=100 else self.about
        else:
            data['about'] = None
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
