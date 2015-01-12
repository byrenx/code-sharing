from webapp2_extras.securecookie import SecureCookieSerializer
from app.settings import settings

SECRET_KEY = settings['app_config']['webapp2_extras.sessions']['secret_key']


class CookieHelper():

    cookie = None
    max_age_dir = {}

    def __init__(self, secret_key=None):
        if secret_key:
            self.cookie = SecureCookieSerializer(secret_key)
        else:
            self.cookie = SecureCookieSerializer(SECRET_KEY)

    def _serialize(self, name, value):
        return self.cookie.serialize(name, value)

    def _deserialize(self, name, value, max_age=None):
        return self.cookie.deserialize(name, value, max_age=None)

    def get(self, controller, name, encrypted=True):
        value = controller.request.cookies.get(name)
        max_age = None
        if name in self.max_age_dir:
            max_age = self.max_age_dir[name]
        if encrypted:
            return self._deserialize(name, value, max_age)
        return value

    def write(self, controller, name, value, max_age=None, path='/', domain=None, secure=False, encrypted=True):
        # Saves a cookie in the client.
        if encrypted:
            value = self._serialize(name, value)
        if max_age:
            self.max_age_dir[name] = max_age
        controller.response.set_cookie(name, value, max_age=max_age, path=path, domain=domain, secure=secure)

    def delete(self, controller, name):
        # Deletes a cookie previously set in the client.
        controller.response.delete_cookie(name)

    def unset(self, controller, name):
        # Cancels a cookie previously set in the response.
        controller.response.unset_cookie(name)
