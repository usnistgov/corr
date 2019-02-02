import datetime
from ..core import db
import json
import hashlib
from ..models import ApplicationModel


class AccessModel(db.Document):
    """CoRR backend access model.
    Track the access to the backend per application,
    backend entity (api, cloud or root for web only).

    Attributes:
        created_at: A string value of the creation timestamp.
        application: A reference to the application instance.
        possible_scope: A list of possible backend entity.
        scope: A string indicating which scope was detected.
        endpoint: A string trace of the endpoint called (api/v1/push).
        extend: A dictionary of any extension to include.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    application = db.ReferenceField(ApplicationModel)
    possible_scope = ["api", "cloud", "root"]
    scope = db.StringField(default="root", choices=possible_scope)
    endpoint = db.StringField(max_length=256)
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an access model instance content.

        Returns:
          The dictionary content of the access model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id),
        'scope':str(self.scope), 'endpoint': str(self.endpoint)}
        if self.application != None:
            data['application'] = str(self.application.id)
        else:
            data['application'] = None
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

    @staticmethod
    def application_access(application=None):
        """Filter down the access to a specific application.

        Returns:
          The filtered dictionary of the application access.
        """
        data = {}
        if application != None:
            data = {'total':len(AccessModel.objects(application=application))}
            data['access'] = [acc.info() for acc in AccessModel.objects(application=application).order_by('-created_at')]
            return data
        return data

    @staticmethod
    def activity_json():
        """Build an activity json about the access on the platform.

        Returns:
          The activity json.
        """
        data = {}
        data['api'] = {'total':len(AccessModel.objects(scope='api')), 'endpoints':[]}
        data['api']['endpoints'] = AccessModel.objects(scope='api').order_by('-endpoint')
        data['cloud'] = {'total':len(AccessModel.objects(scope='cloud')), 'endpoints':[]}
        data['cloud']['endpoints'] = AccessModel.objects(scope='cloud').order_by('-endpoint')

        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
