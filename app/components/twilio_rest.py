# Download the Python helper library from twilio.com/docs/python/install
from twilio.rest import TwilioRestClient
from ferris import settings


class TwilioRest(object):

    def __init__(self):
        # Your Account Sid and Auth Token from twilio.com/user/account

        account_sid = settings.get('twilio').get('account_sid')
        auth_token = settings.get('twilio').get('auth_token')

        self.from_number = "+17602784278"
        self.client = TwilioRestClient(account_sid, auth_token)

    def send_sms(self, to, message):
        message = self.client.messages.create(
            body=message,
            to=to,
            from_=self.from_number)
        print message.sid
