"""CoRR common modules.
"""
from .models import *
from .tools import *
import datetime
from datetime import date, timedelta
from calendar import monthrange
from functools import update_wrapper

def logAccess(component='none', scope='root', endpoint='', app=None):
    """Log the access to the backend.
    """
    (traffic, created) = AccessModel.objects.get_or_create(application=app, scope=scope, endpoint="%s%s"%(component, endpoint))

def logTraffic(component='none', endpoint=''):
    """Log the traffic to the backend.
    """
    (traffic, created) = TrafficModel.objects.get_or_create(service="cloud", endpoint="%s%s"%(component, endpoint))
    if not created:
        traffic.interactions += 1 
        traffic.save()
    else:
        traffic.interactions = 1
        traffic.save()

def logStat(deleted=False, user=None, message=None, application=None, project=None, record=None, diff=None, file_obj=None, comment=None):
    """Log the statistics to the backend.
    """
    category = ''
    periode = ''
    traffic = 0
    interval = ''
    today = datetime.date.today()
    last_day = monthrange(today.year, today.month)[1]

    if user != None:
        category = 'user'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if project != None:
        category = 'project'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if application != None:
        category = 'application'
        periode = 'yearly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_01-%s_12"%(today.year, today.year)

    if message != None:
        category = 'message'
        periode = 'monthly'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_01-%s_%s_%s"%(today.year, today.month, today.year, today.month, last_day)

    if record != None:
        category = 'record'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if diff != None:
        category = 'collaboration'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)

    if file_obj != None:
        category = 'storage'
        periode = 'daily'
        traffic = file_obj.size * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)


    if comment != None:
        category = 'comment'
        periode = 'daily'
        traffic = 1 * (-1 if deleted else 1)
        interval = "%s_%s_%s_0_0_0-%s_%s_%s_23_59_59"%(today.year, today.month, today.day, today.year, today.month, today.day)

    (stat, created) = StatModel.objects.get_or_create(interval=interval, category=category, periode=periode)
    print("Stat Traffic {0}".format(traffic))
    if not created:
        print("Not created stat")
        if (stat.traffic + traffic) >= 0:
            stat.traffic += traffic
        stat.save()
    else:
        print("Created stat")
        stat.traffic = traffic
        stat.save()

def crossdomain(fk=None, app=None, origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    """Allow crossdomain calls from other domains and port.
        Returns:
            decorator to wrap on the endpoints.
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and fk.request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = fk.make_response(f(*args, **kwargs))
            if not attach_to_all and fk.request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

from .managers import *
from .core import *