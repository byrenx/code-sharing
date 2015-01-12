from google.appengine.api import urlfetch
import urlparse  # for urlparse and urljoin
import os  # for os.path.dirname
import json  # for dumps
import logging
from app.settings import settings
from google.appengine.api import app_identity
from packages.firebase_token_generator import create_token
import datetime


class FirebaseRest():
    ROOT_URL = ''  # no trailing slash

    def __init__(self, bucket, auth_token=None):
        firebase_setting = self.get_env_settings()
        FIREBASE_URL = firebase_setting['url']
        self.ROOT_URL = FIREBASE_URL + bucket.rstrip('/')

        #setting = self.get_env_settings()
        #firebase_secret = setting['secret']
        #data = {'user_type': 'omda', "admin": True}

        #today = datetime.datetime.now()
        #expiration = today + datetime.timedelta(hours=24)
        #options = {"expires": expiration, "admin": True}

        #auth_token = create_token(firebase_secret, data, options)
        self.auth_token = None

    def get_env_settings(self):
        DEV = settings.get('firebase').get('DEV')
        QA = settings.get('firebase').get('QA')
        PROD = settings.get('firebase').get('PROD')

        if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):  # local environment falls here
            return settings['firebase']['local']
        else:
            if str(app_identity.get_application_id()) == 'cs-becktaxi-omda-dev':
                return DEV

            elif str(app_identity.get_application_id()) == 'cs-becktaxi-omda-qa':
                return QA

            return PROD

    # These methods are intended to mimic Firebase API calls.

    def child(self, path):
        root_url = '%s/' % self.ROOT_URL
        url = urlparse.urljoin(root_url, path.lstrip('/'))
        return Firebase(url)

    def parent(self):
        url = os.path.dirname(self.ROOT_URL)
        # If url is the root of your Firebase, return None
        up = urlparse.urlparse(url)
        if up.path == '':
            return None  # maybe throw exception here?
        return Firebase(url)

    def name(self):
        return os.path.basename(self.ROOT_URL)

    def toString(self):
        return self.__str__()

    def __str__(self):
        return self.ROOT_URL

    def set(self, value):
        return self.put(value)

    def push(self, data):
        return self.post(data)

    def update(self, data):
        return self.patch(data)

    def remove(self):
        return self.delete()

    # These mirror REST API functionality

    def put(self, data):
        return self.__request(urlfetch.PUT, data=data)

    def patch(self, data):
        return self.__request(urlfetch.PATCH, data=data)

    def get(self):
        return self.__request(urlfetch.GET)

    # POST differs from PUT in that it is equivalent to doing a 'push()' in
    # Firebase where a new child location with unique name is generated and
    # returned
    def post(self, data):
        return self.__request(urlfetch.POST, data=data)

    def delete(self):
        return self.__request(urlfetch.DELETE)

    # Private

    def __request(self, method, **kwargs):
        # Firebase API does not accept form-encoded PUT/POST data. It needs to
        # be JSON encoded.
        # if 'data' in kwargs:
            # kwargs['data'] = json.dumps(kwargs['data'])

        params = {}
        if self.auth_token:
            if 'params' in kwargs:
                params = kwargs['params']
                del kwargs['params']
            params.update({'auth': self.auth_token})

        result = urlfetch.fetch(
            url=self.__url(),
            payload=kwargs['data'] if 'data' in kwargs else None,
            method=method,
            headers={'Content-Type': 'application/json'}
        )

        if 'data' in kwargs:
            # logging.info('Data to be sent to Firebase ==> %s' % kwargs['data'])
            pass

        # logging.info('Firebase Result ==> %s' % result)

        if result.status_code == 200:
            result = json.loads(result.content)
            return result
        else:
            logging.info('Error status code %s' % result.status_code)
            logging.info('Error status code %s' % result.content)

        # r = requests.request(method, self.__url(), params=params, **kwargs)
        # r.raise_for_status()  # throw exception if error
        # return r.json()

    def __url(self):
        # We append .json to end of ROOT_URL for REST API.
        if self.auth_token:
            return '%s.json?auth=%s' % (self.ROOT_URL, self.auth_token)
        else:
            return '%s.json' % self.ROOT_URL
