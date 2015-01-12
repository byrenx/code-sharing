from google.appengine.api import channel
from ferris import Behavior
from app.models.beck_user import BeckUser
import logging


class Notify(Behavior):
    def after_put(self, instance):
        users = BeckUser.list_all()
        for user in users:
            if user.channel_token is not None:
                message = {
                    "action": "UPDATE_" + instance.key.kind().upper() + "_" + instance.status,
                    "is_locked": instance.locked,
                    "data": instance.to_dict()
                }
                channel.send_message(user.channel_token, str(message))

    def after_delete(self, instance):
        users = BeckUser.list_all()
        for user in users:
            if user.channel_token is not None:
                message = {
                    "action": "DELETE_" + instance.key.kind().upper() + "_" + instance.status,
                    "is_locked": instance.locked,
                    "data": instance.to_dict()
                }
                channel.send_message(user.channel_token, str(message))


class ChannelApi(object):

    def create(self, token):
        channel_token = channel.create_channel(token)
        return channel_token
