from ferris import BasicModel, ndb

from google.appengine.api import users
from google.appengine.api import app_identity
from app.models.beck_user import BeckUser
from app.models.customer import Customer
from app.settings import settings
import logging
import uuid
from plugins.firebase_rest import FirebaseRest


def user_authorization(controller):

    from_mobile = False
    is_admin = False
    user = None

    public_routes = (
        'refresh_token',
        'register',
        'vehicle_refresh_token',
        'web_order',
        'get_all_orders',
        'auth_refresh_token_cron'
    )

    # filter route with no credentials needed
    if controller.route.action in public_routes:
        return True

    # Special testing override for the automated performance tests.
    # Enabled only on localhost and the QA server.
    # Hardcoded testing only token.
    testing_token = controller.request.headers.get('testing_token')
    if (app_identity.get_application_id() == 'cs-becktaxi-omda-dev' \
        or app_identity.get_application_id() == 'cs-becktaxi-omda-qa') \
        and testing_token \
        and testing_token == settings['testing_override']['token']:
        user = BeckUser.get_by_email_address(
            settings['testing_override']['email']
        )
        # Create a new testing override user
        if not user:
            user = BeckUser()
            user.first_name = 'testing'
            user.last_name = 'override'
            user.email = settings['testing_override']['email']
            user.role = "SYSTEM_ADMINISTRATOR"
            user.put()
        controller.context['user_role'] = 'SYSTEM_ADMINISTRATOR'
        logging.info("Test token authentication successful")
        # return True

    # # route with temporary access
    # if controller.route.action in ('validate_sms', 'request_sms'):
    #     from_mobile = True
    #     temp_code = controller.request.headers.get('temporary_code')
    #     user = Auth.validate_temp(temp_code)

    # get user by token
    token = controller.request.headers.get('token')
    logging.info("TOKEN ===> %s" % token)
    if token:
        from_mobile = True
        user = Auth.validate(token)
        if user:
            # user exist but check if pending or locked
            if user.status == 'PENDING' or user.status == 'SUSPENDED' or user.locked:
                user = None

    # if no token, check if has google credentials logged in
    if user is None:
        # get user by google credentials
        try:
            user_email = str(users.get_current_user().email())
            user = BeckUser.get_by_id(user_email)

            if not user:
                # allow admin and create profile
                if users.is_current_user_admin():
                    user = BeckUser(id=user_email)
                    user.first_name = user_email
                    user.last_name = user_email
                    user.email = user_email
                    user.role = "SYSTEM_ADMINISTRATOR"
                    user.put()
        except:
            pass

        if user:
            # check IP address if allowed
            ip = controller.request.remote_addr
            allowed_ip = settings.get('allowed_ip')

            if ip in allowed_ip or user.role in ('SYSTEM_ADMINISTRATOR', 'ADMINISTRATOR'):
                pass
            else:
                return False

    if user is None:
        """ Unauthorized """
        return False

    else:
        logging.info('=== USER IS %s ===' % str(user))
        """ valid users """
        if not from_mobile:

            """ users from google """

            if user.locked:
                return False

            controller.context['user_role'] = user.role
            if user.email == settings['testing_override']['email']:
                controller.context['user_object'] = None
                controller.context['logout_url'] = None
            else:
                controller.context['user_object'] = users.get_current_user()
                controller.context['logout_url'] = users.create_logout_url(controller.request.uri)
            controller.session['logged_in_user'] = user

            f = FirebaseRest('foo')
            firebase_setting = f.get_env_settings()

            controller.context['FIREBASE_URL'] = firebase_setting['url']

            if user.role == 'SYSTEM_ADMINISTRATOR' or user.role == 'ADMINISTRATOR' or user.role == 'SUPERVISOR' or user.role == 'SHIFT_LEADER':
                is_admin = True

        """ default user details """

        # customers and drivers
        controller.context['user_email'] = user.email if isinstance(user, BeckUser) else None
        controller.context['auth_user'] = user
        controller.context['auth_user_dict'] = user.to_dict()
        controller.context['is_admin'] = is_admin
        controller.context['from_mobile'] = from_mobile
        logging.info('auth allowed!')
        return True


def allow_access(controller, roles=None, allow_admin=True):
    if allow_admin:
        if controller.context.get('user_role') in ('SYSTEM_ADMINISTRATOR', 'ADMINISTRATOR', 'SUPERVISOR', 'SHIFT_LEADER'):
            return True

        if users.is_current_user_admin():
            return True

        if controller.context.get('is_admin'):
            return True

    context_user_role = controller.context.get('user_role', None)
    if context_user_role:
        if context_user_role in roles:
            return True
        else:
            return False

    # last check, OMDA users should not reach this point, only for authenticatd users via Auth
    if controller.context.get('auth_user'):
        return True

    return False


def csr(f):
    def wrapper(*args, **kw):
        if args[0].context.get('user_role') == 'CSR':
            return False
        else:
            return f(*args, **kw)
    return wrapper


class AuthModel(BasicModel):
    object_key = ndb.KeyProperty(required=False)
    code = ndb.StringProperty(indexed=True, required=True)
    code_last_refreshed = ndb.DateTimeProperty(required=False)
    temporary_code = ndb.StringProperty(indexed=True, required=False)
    token = ndb.StringProperty(indexed=True, required=False)
    token_last_refreshed = ndb.DateTimeProperty(required=False)

    def all(cls):
        return cls.query()

    @classmethod
    def delete(cls, key):
        logging.info(key)
        obj = AuthModel.query(AuthModel.object_key == key).get()
        obj.key.delete()


class Auth(object):

    @classmethod
    def validate(self, token):
        obj = AuthModel.find_by_properties(token=token)
        if obj:
            entity = obj.object_key.get()
            logging.info('Auth Object =====> %s' % entity)
            self.user = entity
            return entity
        else:
            return None

    @classmethod
    def validate_temp(self, code):
        obj = AuthModel.find_by_properties(temporary_code=code)
        if obj:
            entity = obj.object_key.get()
            logging.info('Auth Object =====> %s' % entity)
            self.user = entity
            return entity
        else:
            return None

    @classmethod
    def create_code(self, object_key, code=None):
        auth = AuthModel(id=object_key.urlsafe())
        auth.object_key = object_key

        auth.code = str(uuid.uuid4()) if code is None else code
        auth.temporary_code = str(uuid.uuid4())
        auth.put()
        return auth

    @classmethod
    def refresh_token(self, code, field, value):

        find_token = AuthModel.find_by_properties(code=code)
        token = None
        logging.info("ibject ==> %s" % find_token)
        if find_token:
            obj = find_token.object_key.get()
            if getattr(obj, field) == value:
                find_token.token = str(uuid.uuid4())
                find_token.put()

                token = find_token.token
        if token:
            return '{"token" : "%s"}' % token
        return 401

    @classmethod
    def generate_code(self):
        return str(uuid.uuid4())

    @classmethod
    def find(self, object_key):
        user = AuthModel.find_by_properties(object_key=object_key)
        return user
