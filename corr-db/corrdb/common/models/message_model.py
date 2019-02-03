import datetime
from ..core import db
import json
from bson import ObjectId

from ..models import UserModel
from ..models import FileModel

class MessageModel(db.Document):
    """CoRR backend message model.
    The model holding the message interaction between two users.

    Attributes:
        created_at: A string value of the creation timestamp.
        sender: A reference to the sender of the message.
        receiver: A reference to the receiver of the message.
        title: A string value of the message's title.
        content: A string value of the messages's content.
        attachments: A list of files attached to the message.
        extend: A dictionary of to add other fields to the message model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    sender = db.ReferenceField(UserModel, required=True)
    receiver = db.ReferenceField(UserModel, required=True)
    title = db.StringField()
    content = db.StringField()
    attachments = db.ListField(db.StringField())
    extend = db.DictField()

    def _attachments(self):
        """Gather the files attached to the message.

        Returns:
          The message attachments files.
        """
        attachments = []
        for f_id in self.attachments:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                attachments.append(f)
        return attachments

    def info(self):
        """Build a dictionary structure of an message model instance content.

        Returns:
          The dictionary content of the message model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id), 'sender':str(self.sender.id),
        'receiver':str(self.receiver.id), 'title':self.title}
        data['attachments'] = len(self.attachments)
        return data

    def extended(self):
        """Add the extend, content and attachments fields to the built dictionary content.

        Returns:
          The augmented dictionary.
        """
        data = self.info()
        data['content'] = self.content
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
        """Transform the info dictionary with content, attachments fields into a pretty json.

        Returns:
          The pretty json of the info dictionary. 
        """
        data = self.info()
        if self.content != None:
            data['content'] = self.content[0:96]+"..." if len(self.content) >=100 else self.content
        else:
            data['content'] = None
        if self.attachments != None:
            data['attachments'] = len(self.attachments)
        else:
            data['attachments'] = None
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
