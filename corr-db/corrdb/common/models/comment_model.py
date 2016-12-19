import datetime
from ..core import db
import json
from bson import ObjectId

from ..models import UserModel
from ..models import FileModel
          
class CommentModel(db.Document):
    """CoRR backend comment model.
    The model that stores interaction between users and some objects.
    The objects can be: project, record, diff and environment.

    Attributes:
        created_at: A string value of the creation timestamp.
        sender: A reference to the user that created the comment.
        resource: A reference to the file on which the comment was made.
        title: A string value of the comment title if any.
        content: A string holding the content of the comment.
        attachments: A list of file references attached to the comment.
        useful: A list of all the users references that find this comment useful.
        extend: A dictionary of to add other fields to the comment model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    sender = db.ReferenceField(UserModel, required=True)
    resource = db.ReferenceField(FileModel, reverse_delete_rule=db.CASCADE)
    title = db.StringField()
    content = db.StringField()
    attachments = db.ListField(db.StringField())
    useful = db.ListField(db.StringField())
    extend = db.DictField()

    def _useful(self):
        """Retrieve the list of users that marked the comment to be useful.
        Returns:
            The users list.
        """
        useful = []
        for u_id in self.useful:
            u = UserModel.objects.with_id(u_id)
            if u != None:
                useful.append(u)
        return useful

    def _attachments(self):
        """Gather the files attached to the comment.
        Returns:
            The comment attachments files.
        """
        attachments = []
        for f_id in self.attachments:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                attachments.append(f)
        return attachments

    def info(self):
        """Build a dictionary structure of an comment model instance content.
        Returns:
            The dictionary content of the comment model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'sender':str(self.sender.id), 'title':self.title,
        'content':self.content}
        if self.resource != None:
            data['resource'] = str(self.resource.id)
        data['useful'] = len(self.useful)
        data['attachments'] = len(self.attachments)
        return data

    def extended(self):
        """Add the extend, resource, useful and attachments fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        if self.resource != None:
            data['resource'] = self.resource.extended()
        data['useful'] = []
        for us in self._useful():
            us_profile = ProfileModel.objects(user=us).first()
            if us_profile == None:
                data['useful'].append({'email_only':us.email})
            else:
                data['useful'].append(us_profile.info())
        data['attachments'] = [attachment.extended() for attachment in self._attachments()]
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