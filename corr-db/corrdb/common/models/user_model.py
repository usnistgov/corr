import datetime
from ..core import db
import json
import hashlib
import time

# TODO: Issue with connected_at and datetime in general that makes it not stable in mongodb.
# TODO: Add the filemodel to the quota check.

class UserModel(db.Document):
    """CoRR backend user model.
    The model holding the user information.

    Attributes:
        created_at: A string value of the creation timestamp.
        connected_at: A string value of when the user connected last time.
        email: A string value of the user email.
        api_token: A string value of the api token access to the backend.
        session: A string value of the user web session token.
        possible_group: A list of user possible groups.
        group: A string value of the user current group with unknown as default.
        extend: A dictionary of to add other fields to the user model.
    """
    created_at = db.StringField(default=str(datetime.datetime.utcnow()))
    connected_at = db.StringField(default=str(datetime.datetime.utcnow()))
    email = db.StringField(required=True, unique=True)
    api_token = db.StringField(max_length=256, unique=True)
    session = db.StringField(max_length=256, unique=True)
    possible_group = ["admin", "user", "developer", "public", "unknown"]
    group = db.StringField(default="unknown", choices=possible_group)
    extend = db.DictField()

    def is_authenticated(self):
        """Check if the user authenticated.
        Returns:
            The authenticated status.
        """
        return True

    def is_active(self):
        """Check if the user is currently connected.
        Returns:
            The activity status of the user.
        """
        return True

    def is_anonymous(self):
        """Check if the user is anonymous.
        Returns:
            The user anonymous state.
        """
        return False

    def get_id(self):
        """Get the user id properly
        Returns:
            The user object id.
        """
        try:
            return unicode(self.id)
        except NameError:
            return str(self.id)

    def save(self, *args, **kwargs):
        """Overwrite the user mongoengine save
        Returns:
            The call to the mongoengine Document save function.
        """
        if not self.created_at:
            self.created_at = str(datetime.datetime.utcnow())

        if not self.connected_at:
            self.connected_at = str(datetime.datetime.utcnow())

        if not self.api_token:
            self.api_token = hashlib.sha256(b'CoRRToken_%s'%(str(datetime.datetime.utcnow()))).hexdigest()

        if not self.session:
            self.session = hashlib.sha256(b'CoRRSession_%s'%(str(datetime.datetime.utcnow()))).hexdigest()

        return super(UserModel, self).save(*args, **kwargs)

    def sess_sync(self, unic):
        """Update the user session.
        """
        self.session = str(hashlib.sha256(b'CoRRSession_%s_%s_%s'%(self.email, str(self.connected_at), unic)).hexdigest())
        self.save()

    def renew(self, unic):
        """Renew the user session.
        """
        print "connected_at: %s"%str(self.connected_at)
        self.connected_at = str(datetime.datetime.utcnow())
        print "connected_at: %s"%str(self.connected_at)
        print "session: %s"%str(self.session)
        self.session = str(hashlib.sha256(b'CoRRSession_%s_%s_%s'%(self.email, str(self.connected_at), unic)).hexdigest())
        self.save()
        print "connected_at: %s"%str(self.connected_at)
        print "session: %s"%str(self.session)

    def retoken(self):
        """Renew the user api token.
        """
        self.api_token = hashlib.sha256(b'CoRRToken_%s_%s'%(self.email, str(datetime.datetime.utcnow()))).hexdigest()
        self.save()

    def allowed(self, unic):
        """Build the allowence to access the session for the user.
        Returns:
            The hash of the allowence string content.
        """
        print "connected_at: %s"%str(self.connected_at)
        print "session: %s"%str(self.session)
        allowed = hashlib.sha256(b'CoRRSession_%s_%s_%s'%(self.email, str(self.connected_at), unic)).hexdigest()
        print "allowed: %s"%str(allowed)
        return str(allowed)

    def info(self):
        """Build a dictionary structure of an user model instance content.
        Returns:
            The dictionary content of the user model.
        """
        data = {'created':str(self.created_at), 
        'id': str(self.id), 'email' : self.email,
         'group':self.group, 'total_projects' : len(self.projects), 'total_duration':self.duration, 'total_records':self.record_count}
        return data

    def extended(self):
        """Add the extend, apiToken, session fields to the built dictionary content.
        Returns:
            The augmented dictionary.
        """
        data = self.info()
        data['apiToken'] = self.api_token
        data['session'] = self.session
        data['extend'] = self.extend
        return data

    def home(self):
        """Build the dictionary of the user home info.
        Returns:
            The home dictionary.
        """
        from ..models import ProfileModel
        data = {}
        data['account'] = self.extended()
        data['profile'] = ProfileModel.objects(user=self).first().extended()
        data['activity'] = {}
        data['activity']['quota'] = self.quota
        data['activity']['apps'] = {'size':len(self.apps), 'list':[app.info() for app in self.apps]}
        data['activity']['statistics'] = {'size_project':len(self.projects), 'size_records':len(self.records), 'duration':self.duration}
        return data


    def to_json(self):
        """Transform the extended dictionary into a pretty json.
        Returns:
            The pretty json of the extended dictionary.
        """
        data = self.extended()
        return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

    def activity_json(self, admin=False):
        """Build a pretty json of the user activity.
        Returns:
            The pretty json of the user activity.
        """
        projects_summary = [json.loads(p.summary_json()) for p in self.projects if not p.private or admin]
        return json.dumps({'user':self.extended(), 'projects' : projects_summary}, sort_keys=True, indent=4, separators=(',', ': '))

    @property
    def projects(self):
        """Extract the user's projects.
        Returns:
            The projects list.
        """
        from ..models import ProjectModel
        return ProjectModel.objects(owner=self)

    @property
    def apps(self):
        """Extract the user applications.
        Returns:
            The user applications list.
        """
        from ..models import ApplicationModel
        return [p.application for p in self.projects]

    @property
    def records(self):
         """Extract the user's projects' records.
        Returns:
            The user records.
        """
        records = []
        for project in self.projects:
            records.extend(project.records)
        return records

    @property
    def quota(self):
         """Compute the the user quota.
        Returns:
            quota used by the user.
        """
        from ..models import FileModel
        from ..models import EnvironmentModel
        from ..models import CommentModel
        occupation = 0
        for project in self.projects:
            for env in project.history:
                environment = EnvironmentModel.objects.with_id(env)
                if environment != None and environment.bundle != None:
                    try:
                        occupation = occupation + environment.bundle.size
                    except:
                        pass
            for file_id in project.resources:
                _file = FileModel.objects.with_id(file_id)
                if _file != None:
                    try:
                        occupation = occupation + _file.size
                    except:
                        pass
            for file_id in project.resources:
                _file = FileModel.objects.with_id(file_id)
                if _file != None:
                    try:
                        occupation = occupation + _file.size
                    except:
                        pass
            for comment_id in project.comments:
                _comment = CommentModel.objects.with_id(comment_id)
                if _comment != None:
                    for file_id in _comment.attachments:
                        _file = FileModel.objects.with_id(file_id)
                        if _file != None:
                            try:
                                occupation = occupation + _file.size
                            except:
                                pass
            for record in self.records:
                for file_id in record.resources:
                    _file = FileModel.objects.with_id(file_id)
                    if _file != None:
                        try:
                            occupation = occupation + _file.size
                        except:
                            pass
                for comment_id in record.comments:
                    _comment = CommentModel.objects.with_id(comment_id)
                    if _comment != None:
                        for file_id in _comment.attachments:
                            _file = FileModel.objects.with_id(file_id)
                            if _file != None:
                                try:
                                    occupation = occupation + _file.size
                                except:
                                    pass

        return occupation
    
    @property
    def record_count(self):
        """Count all the user records.
        Returns:
            The user total records.
        """
        return sum([p.record_count for p in self.projects])

    @property
    def duration(self):
        """Compute the duration a user used the platform.
        Returns:
            The user usage duration.
        """
        d = 0
        for p in self.projects:
            try:
                d += p.duration.total_seconds()
            except:
                d = d + p.duration
        return str(datetime.timedelta(seconds=d))


            
