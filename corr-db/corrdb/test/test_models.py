"""Usage: run.py [--host=<host>] [--port=<port>] [--debug | --no-debug]

--host=<host>   set the host address or leave it to 0.0.0.0.
--port=<port>   set the port number or leave it to 5100.

"""
from flask import Flask
from flask_mongoengine import MongoEngine
import unittest

from corrdb.common import logAccess, logStat, logTraffic, crossdomain
from corrdb.common.core import setup_app
from corrdb.common.tools.converters import ObjectIDConverter
from corrdb.common.models import TrafficModel
from corrdb.common.models import StatModel
from corrdb.common.models import BundleModel
from corrdb.common.models import VersionModel
from corrdb.common.models import UserModel
from corrdb.common.models import FileModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import MessageModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import CommentModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import AccessModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import RecordModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import DiffModel

class TestModels(unittest.TestCase):

    def setUp(self):
        db = MongoEngine()
        app = Flask("corrdb")
        # app.config.MONGODB_SETTINGS = { 'db': 'corrdb', 'host': '0.0.0.0', 'port': 27017 }
        print(app.config.db)
        app.config.from_object({'db': 'corrdb', 'host': '0.0.0.0', 'port': 27017 })
        app.logger_name = "corrdb.app"

        # Flask-MongoEngine instance
        db.init_app(app)

        # Custom Converters
        app.url_map.converters['objectid'] = ObjectIDConverter

        app.run(debug='--no-debug', host='0.0.0.0', port=5000, threaded=True)

    def test_traffic(self):
        now = str(datetime.datetime.utcnow())
        traffic_created = TrafficModel(created_at=now, service="api", endpoint="/test/corrdb", interactions=1)
        traffic_created.save()
        traffic_fetched = TrafficModel.objects.with_id(traffic_created.id)
        self.assertEqual(traffic_created, traffic_fetched)
        self.assertIn(traffic_created.service, ["api", "cloud", "web", "undefined"])

    def test_stat(self):
        today = datetime.date.today()
        now = str(datetime.datetime.utcnow())
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)
        stat_created = StatModel(created_at=now, interval=interval, category="storage", periode="daily")
        stat_created.save()
        stat_fetched = StatModel.objects.with_id(stat_created.id)
        self.assertEqual(stat_created, stat_fetched)
        self.assertIn(stat_created.periode, ["yearly", "monthly", "daily", "undefined"])

    def test_bundle(self):
        now = str(datetime.datetime.utcnow())
        storage = db.StringField()
        mimetype = db.StringField()
        checksum = db.StringField()
        size = db.LongField()
        bundle_created = BundleModel(created_at=now, scope="local", storage="test_file.csv")
        bundle_created.save()
        bundle_fetched = BundleModel.objects.with_id(bundle_created.id)
        self.assertEqual(bundle_created, bundle_fetched)
        self.assertIn(bundle_created.scope, ["local", "remote", "unknown"])

    def test_version(self):
        now = str(datetime.datetime.utcnow())
        version_created = VersionModel(created_at=now, service="api", endpoint="/test/corrdb", interactions=1)
        version_created.save()
        version_fetched = VersionModel.objects.with_id(version_created.id)
        self.assertEqual(version_created, version_fetched)
        self.assertIn(version_created.service, ["api", "cloud", "web", "undefined"])

    def tearDown(self):
        # Delete all documents
        # Stop mongodb instance.
        for traffic in TrafficModel.objects():
          traffic.delete()
        for stat in StatModel.objects():
          stat.delete()
        for bundle in BundleModel.objects():
          bundle.delete()
        for version in VersionModel.objects():
          version.delete()
        for user in UserModel.objects():
          user.delete()
        for file in FileModel.objects():
          file.delete()
        for profile in ProfileModel.objects():
          profile.delete()
        for message in MessageModel.objects():
          message.delete()
        for project in ProjectModel.objects():
          project.delete()
        for comment in CommentModel.objects():
          comment.delete()
        for application in ApplicationModel.objects():
          application.delete()
        for access in AccessModel.objects():
          access.delete()
        for environment in EnvironmentModel.objects():
          environment.delete()
        for record in RecordModel.objects():
          record.delete()
        for record in RecordBodyModel.objects():
          record.delete()
        for diff in DiffModel.objects():
          diff.delete()
