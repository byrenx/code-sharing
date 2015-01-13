from ferris import Controller, route, route_with
from google.appengine.api import mail
# google app engine oauth2 API
from ferris.components import csrf
from ferris.components.csrf import csrf_protect
import re

# firebase libraries
from packages.firebase_rest import FirebaseRest

import datetime
import time


class CodeShare(Controller):
    class Meta:
        prefixes = ('api',)
        components = (csrf.CSRF,)

    def check_email_format(self, email):
        match = re.search(
            r'[\w+-]+(?:\.[\w+-]+)*@[\w+-]+(?:\.[\w+-]+)*(?:\.[a-zA-Z]{2,4})',
            email
        )

        if match:
            return True
        else:
            return False

    @route_with("/")
    def index(self):
        pass

    @route_with("/codex")
    def editor(self):
        pass

    # checks if data is 30 days old
    def check_time_difference(self, date):
        # date should be timestamp float
        if date is not None:
            # get current date
            curdate = datetime.datetime.now()
            date_2 = time.mktime(curdate.timetuple())
            time_difference = date_2 - date

            # 30 days == 2,600,000 milliseconds
            if time_difference >= 2600000.0:
                return True
            else:
                return False

    # gets the Firebase ID to be deleted
    def get_firebase_id(self, d):
        id_key = None
        for key, value in d.iteritems():
            id_key = key
            for k, v in value.iteritems():
                if k == "updatedAt":
                    if self.check_time_difference(v):
                        self.delete_firebase_data(id_key)

    # deletes data in Firebase by ID
    def delete_firebase_data(self, fireID):
        f = FirebaseRest(fireID)
        f.delete()
        return 200

    # get reference to the data (for cronjob)
    @route
    def get_firebase_reference(self):
        f = FirebaseRest('')
        data = f.get()
        d = dict(data)
        self.get_firebase_id(d)
        return 200

    # email composer for sending / sharing codex
    def compose(self):
        params = {
            'email': self.request.get('email'),
            'url': self.request.get('url')
        }
        email = params['email']

        if self.check_email_format(email):
            mail.send_mail(
                sender="codex.share@gmail.com",
                to=params['email'].lower(),
                subject="Codex shared to you",
                body=params['url']
            )
            self.context['data'] = params['email']
            return 200
        else:
            return 403

    # creates json data and uses csrf to avoid spam
    @route
    @csrf_protect
    def api_compose(self):
        cs = self.compose()
        return cs
