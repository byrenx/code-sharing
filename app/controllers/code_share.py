from ferris import Controller, route
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
        oauth_scopes = ['https://www.googleapis.com/auth/userinfo.profile']

    def email_check(self, email):
        match = re.search(r'[\w+-]+(?:\.[\w+-]+)*@[\w+-]+(?:\.[\w+-]+)*(?:\.[ a - z A - Z ]{2,4})', email)

        if match:
            return True
        else:
            return False

    @route
    def index(self):
        pass

    @route
    def editor(self):
        pass

    # checks if data is 30 days old
    def check_date(self, date):
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
    def check_del_ID(self, d):
        id_key = None
        for key, value in d.iteritems():
            id_key = key
            for k, v in value.iteritems():
                if k == "updatedAt":
                    if self.check_date(v):
                        self.deleteID(id_key)

    # deletes data in Firebase by ID
    def deleteID(self, fireID):
        f = FirebaseRest(fireID)
        f.delete()
        return 200

    # get reference to the data (for cronjob)
    @route
    def getFire(self):
        f = FirebaseRest('')
        data = f.get()
        d = dict(data)
        self.check_del_ID(d)
        return 200

    # email composer for sending / sharing codex
    def compose(self):
        params = {'email': self.request.get('email'), 'url': self.request.get('url')}
        email = params['email']
        if self.email_check(email):
            mail.send_mail(sender="codex.share@gmail.com",
                to=params['email'].lower(),
                subject="Codex shared to you",
                body=params['url'])
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
