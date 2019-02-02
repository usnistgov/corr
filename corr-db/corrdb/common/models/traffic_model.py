from ..core import db
import datetime
import json
from bson import ObjectId

class TrafficModel(db.Document):
    """CoRR backend traffic model.
    The traffic model countes the hits on all entities of the platform.

    Attributes:
        created_at: A string value of the creation timestamp.
        possible_service: A list of entities considered for the traffic tracking.
        service: A string value for the concerned traffic entity with undefined as default.
        endpoint: A string value of the endpoint being hit.
        periode: A string value of the current interval periode with undefined as default.
        interactions: A long value of all the hits on the endpoint.
        extend: A dictionary of to add other fields to the traffic model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    possible_service = ["api", "cloud", "web", "undefined"]
    service = db.StringField(default="undefined", choices=possible_service)
    endpoint = db.StringField()
    interactions = db.LongField(default=0)
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an traffic model instance content.

        Returns:
          The dictionary content of the traffic model.
        """
        data = {'created':str(self.created_at), 'id': str(self.id),
        'service':str(self.service), 'endpoint':self.endpoint}
        return data

    def extended(self):
        """Add the extend, interactions fields to the built dictionary content.

        Returns:
          The augmented dictionary.
        """
        data = self.info()
        data['interactions'] = self.interactions
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
