from ..core import db
import datetime
import json
from bson import ObjectId

class StatModel(db.Document):
    """CoRR backend stat model.
    This model stores all the stats around  the platform usage.

    Attributes:
        created_at: A string value of the creation timestamp.
        interval: A string calue of the stat interval; yearly, monthly or daily 
        ("2015_01-2015_12", "2015_08_1-2015_08_31", "2015_08_14_0_0_0-2015_08_14_23_59_59")
        possible_category: A list of stats categories.
        category: A string value for the concerned stat category with undefined as default.
        possible_periode: A list of all possible interval periodes.
        periode: A string value of the current interval periode with undefined as default.
        traffic: A long value of the traffic counter for the appropriate category.
            For user it is the number for the storage it is the size of the files, etc.
        extend: A dictionary of to add other fields to the stat model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    interval = db.StringField(required=True)
    possible_category = ["user", "project", "record", "storage", "message", "application", "comment", "undefined", "collaboration"]
    category = db.StringField(default="undefined", choices=possible_category)
    possible_periode = ["yearly", "monthly", "daily", "undefined"]
    periode = db.StringField(default="undefined", choices=possible_periode)
    traffic = db.LongField(default=0)
    extend = db.DictField()

    def info(self):
        """Build a dictionary structure of an stat model instance content.
        Returns:
            The dictionary content of the stat model.
        """
        data = {'created':str(self.created_at), 'interval':str(self.interval), 'category': str(self.category), 
        'periode':str(self.periode), 'volume':self.traffic}
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