import json

from flask.ext.api import status
import flask as fk

from api import app, API_URL, crossdomain, check_api, check_app, api_response, s3_delete_file, s3_get_file, web_get_file, s3_upload_file, data_pop, merge_dicts, logStat, logTraffic, logAccess, prepare_env, prepare_record, prepare_project
from corrdb.common.models import UserModel
from corrdb.common.models import AccessModel
from corrdb.common.models import TrafficModel
from corrdb.common.models import FileModel
from corrdb.common.models import ProfileModel
from corrdb.common.models import StatModel
from corrdb.common.models import ProjectModel
from corrdb.common.models import RecordModel
from corrdb.common.models import RecordBodyModel
from corrdb.common.models import DiffModel
from corrdb.common.models import ApplicationModel
from corrdb.common.models import CommentModel
from corrdb.common.models import MessageModel
from corrdb.common.models import EnvironmentModel
from corrdb.common.models import BundleModel
from corrdb.common.models import VersionModel

import mimetypes
import json
import traceback
import datetime
import random
import string
import os
import thread
