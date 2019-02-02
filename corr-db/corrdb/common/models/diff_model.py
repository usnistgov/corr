import datetime
from ..core import db
from ..models import UserModel
from ..models import FileModel
from ..models import CommentModel
from ..models import RecordModel
from ..models import ProfileModel
import json
from bson import ObjectId

class DiffModel(db.Document):
    """CoRR backend diff model.
    Model that define how the differentiation between two records
    can be stored. It captures the various interactions between
    users around their data and the path to agreement or disagreement
    about diff request from a user based on his record and another's.

    Attributes:
        created_at: A string value of the creation timestamp.
        sender: The diff creator.
        targeted: The record to ower being targeted by the diff.
        record_from: A reference to the record from where the diff is made.
        record_to: A reference to the record toward which the diff is made.
        possible_method: A list of possible diff methods.
        method: The current diff method used with undefined as default.
        resources: A list of files associated to the diff as resources.
        possible_proposition: A list of diff propositions.
        proposition: the current diff proposition with undefined as default.
        possible_status: A list of the diff's possible statuses.
        status: A string value of the diff current statys with undefined as default.
        comments: A list of the comments done on the diff.
        extend: A dictionary of to add other fields to the bundle model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    sender = db.ReferenceField(UserModel, required=True)
    targeted = db.ReferenceField(UserModel, required=True)
    record_from = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    record_to = db.ReferenceField(RecordModel, reverse_delete_rule=db.CASCADE, required=True)
    possible_method = ["default", "visual", "custom", "undefined"]
    method = db.StringField(default="undefined", choices=possible_method)
    resources = db.ListField(db.StringField())
    possible_proposition = ["repeated", "reproduced", "replicated", "non-replicated", "non-repeated", "non-reproduced", "undefined"]
    proposition = db.StringField(default="undefined", choices=possible_proposition)
    possible_status = ["proposed", "agreed", "denied", "undefined", "altered"]
    status = db.StringField(default="undefined", choices=possible_status)
    comments = db.ListField(db.StringField())
    extend = db.DictField()

    def _comments(self):
        """Retrieve the diff's comments objects.

        Returns:
          The diff's comments.
        """
        comments = []
        for com_id in self.comments:
            com = CommentModel.objects.with_id(com_id)
            if com != None:
                comments.append(com)
        return comments

    def _resources(self):
        """Filter out the diff's resources files objects.

        Returns:
          The diff's resources.
        """
        resources = []
        for f_id in self.resources:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                resources.append(f)
        return resources

    def info(self):
        """Build a dictionary structure of an diff model instance content.

        Returns:
          The dictionary content of the diff model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id),
        'from':self.record_from.info(), 'to': self.record_to.info(), 'proposition':self.proposition,
        'method': self.method, 'status': self.status}
        data['sender'] = str(self.sender.id)
        data['targeted'] = str(self.targeted.id)
        data['resources'] = len(self.resources)
        data['comments'] = len(self.comments)
        return data

    def extended(self):
        """Add the extend, sender, targeted, resources, comments fields to the built dictionary content.

        Returns:
          The augmented dictionary.
        """
        data = self.info()
        sender_profile = ProfileModel.objects(user=self.sender).first()
        targeted_profile = ProfileModel.objects(user=self.targeted).first()
        data['resources'] = [resource.extended() for resource in self._resources()]
        data['comments'] = [comment.extended() for comment in self._comments()]
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
        """Transform the info dictionary with sender, targeted, comments, resources fields into a pretty json.

        Returns:
          The pretty json of the info dictionary.
        """
        data = self.info()
        data['sender'] = str(self.sender.id)
        data['targeted'] = str(self.targeted.id)
        data['comments'] = len(self.comments)
        data['resources'] = len(self.resources)
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
