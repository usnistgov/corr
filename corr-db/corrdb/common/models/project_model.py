import datetime
from ..core import db
from ..models import UserModel
from ..models import FileModel
from ..models import CommentModel
from ..models import EnvironmentModel
import json
from bson import ObjectId
          
class ProjectModel(db.Document):
    """CoRR backend project model.
    This model represents how a project is stored in CoRR.

    Attributes:
        created_at: A string value of the creation timestamp.
        logo: A reference to the project logo file.
        owner: A reference to the creator of the project.
        name: A string value for the project name.
        description: A string value for the project description.
        goals: A string value for the project goals.
        tags: A list of strings that are considered as the project tags.
        possible_access: A list of possible access state of the project.
        access: A string of the project current state with private as default.
        history: The list of environments references.
        cloned_from: A string value of another project id in case of being cloned.
        resources: A list of files references that are attached to the project meta-data.
        possible_group: A list of possible group states regarding the nature of the project.
        group: A string value of the project current group with undefined as default.
        comments: A list of comments on the project resources.
        extend: A dictionary of to add other fields to the profile model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    update_at = db.StringField(default=str(datetime.datetime.utcnow()))
    logo = db.ReferenceField(FileModel)
    owner = db.ReferenceField(UserModel, reverse_delete_rule=db.CASCADE, required=True)
    name = db.StringField(required=True)
    description = db.StringField()
    goals = db.StringField()
    tags = db.ListField(db.StringField())
    possible_access = ["private", "protected", "public"]
    access = db.StringField(default="private", choices=possible_access)
    history = db.ListField(db.StringField())
    cloned_from = db.StringField(max_length=256)
    resources = db.ListField(db.StringField())
    possible_group = ["computational", "experimental", "hybrid", "undefined"]
    group = db.StringField(default="undefined", choices=possible_group)
    comments = db.ListField(db.StringField())
    extend = db.DictField()

    def save(self, *args, **kwargs):
        """Overwrite the project mongoengine save.
        Returns:
            The call to the mongoengine Document save function.
        """
        self.updated_at = str(datetime.datetime.utcnow())
        return super(ProjectModel, self).save(*args, **kwargs)

    def _history(self):
        """Gather the project environments history.
        Returns:
            The environments history.
        """
        history = []
        for env_id in self.history:
            env = EnvironmentModel.objects.with_id(env_id)
            if env != None:
                history.append(env)
        return history

    def _comments(self):
        """Gather the project comments.
        Returns:
            The project comments.
        """
        comments = []
        for com_id in self.comments:
            com = CommentModel.objects.with_id(com_id)
            if com != None:
                comments.append(com)
        return comments

    def _resources(self):
        """Filter out the project resources files.
        Returns:
            The project files.
        """
        resources = []
        for f_id in self.resources:
            f = FileModel.objects.with_id(f_id)
            if f != None:
                resources.append(f)
        return resources

    def info(self):
        """Build a dictionary structure of an project model instance content.
        Returns:
            The dictionary content of the project model.
        """
        data = {'created':str(self.created_at), 'updated':str(self.last_updated), 'id': str(self.id), 
        'owner':self.owner.info(), 'name': self.name, 'access':self.access, 'tags':','.join(self.tags), 
        'duration': str(self.duration), 'records':self.record_count, 'environments':len(self.history),
        'diffs':self.diff_count, 'comments':len(self.comments), 'resources':len(self.resources)}
        # data['owner-profile'] = self.owner.info()['user-name']
        if self.logo != None:
            data['logo'] = str(self.logo.id)
        else:
            data['logo'] = ''
        data['goals'] = self.goals
        data['description'] = self.description
        return data

    def extended(self):
        """Add the extend, goals, history, description, comments, resources fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['history'] = [env.extended() for env in self._history()]
        data['comments'] = [comment.extended() for comment in self._comments()]
        data['resources'] = [resource.extended() for resource in self._resources()]
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
        """Transform the info dictionary with goals, description fields into a pretty json.
        Returns:
            The pretty json of the info dictionary.
        """
        data = self.info()
        if self.goals != None:
            data['goals'] = self.goals[0:96]+"..." if len(self.goals) >=100 else self.goals
        else:
            data['goals'] = None
        if self.description != None:
            data['description'] = self.description[0:96]+"..." if len(self.description) >=100 else self.description
        else:
            data['description'] = None
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self, public=False):
        """Gather all the activity done on the project.
        Returns:
            The pretty json of the project activity.
        """
        if not public:
            records_summary = [json.loads(r.summary_json()) for r in self.records]
            return json.dumps({'project':self.extended(), "records":records_summary}, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            if project.access == 'public':
                records_summary = []
                for record in self.records:
                    if record.access == 'public':
                        records_summary.append(json.loads(r.summary_json()))
                return json.dumps({'project':self.extended(), "records":records_summary}, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                return json.dumps({}, sort_keys=True, indent=4, separators=(',', ': '))

    def compress(self):
        """Extract out a 'compressed' structure of the project with its records and diffs.
        Returns:
            The dictionary of the augmented extended dictionary.
        """
        data = self.extended()
        data['records'] = [record.extended() for record in self.records]
        data['diffs'] = [diff.extended() for diff in self.diffs]
        return data

    @property
    def record_count(self):
        """Count the project's records.
        Returns:
            The number of records in the project.
        """
        return self.records.count()

    @property
    def diff_count(self):
        """Count the project's records' diffs
        Returns:
            The number of records' diffs in the project.
        """
        from ..models import DiffModel
        diffs = []
        for diff in DiffModel.objects():
            if diff.record_from.project == self and str(diff.id) not in [str(d.id) for d in diffs]:
                diffs.append(diff)
            if diff.record_to.project == self and str(diff.id) not in [str(d.id) for d in diffs]:
                diffs.append(diff)
        return len(diffs)

    @property
    def diffs(self):
        """Gather all the project's records' diffs.
        Returns:
            All the project's records' diffs.
        """
        from ..models import DiffModel
        diffs = []
        for diff in DiffModel.objects():
            if diff.record_from.project == self:
                diffs.append(diff)
            if diff.record_to.project == self:
                diffs.append(diff)
        return diffs

    @property
    def records(self):
        """Gather all the project's records.
        Returns:
            The project's records.
        """
        from ..models import RecordModel
        return RecordModel.objects(project=self).order_by('+created_at')

    @property
    def envs(self):
        """Gather all the project's records.
        Returns:
            The project's records.
        """
        envs = []
        for record in self.records:
            if record.environment:
                envs.append(record.environment)
        return envs
    
    @property
    def last_updated(self):
        """Compute the last time the project was updated based on the records history.
        Returns:
            The most recent time a record in the project was record or project data changed.
        """
        try:
            updated = self.update_at
        except:
            if self.record_count >0:
                updated = self.records.order_by('-updated_at').limit(1).first().updated_at
        return updated

    @property
    def duration(self):
        """Compute the project duration from the creation stamp to the last updated.
        Returns:
            The duration of the project from its creation to its latest update.
        """
        last_updated_strp = datetime.datetime.strptime(str(self.last_updated), '%Y-%m-%d %H:%M:%S.%f')
        created_strp = datetime.datetime.strptime(str(self.created_at), '%Y-%m-%d %H:%M:%S.%f')
        return last_updated_strp-created_strp