from ferris import Behavior
from ferris.core.json_util import stringify as json_stringify
from google.appengine.ext import deferred
from app.components.utilities import parse_entity
from plugins.firebase_rest import FirebaseRest
from ferris import ndb
import logging


class FirebaseActions:

    @classmethod
    def remove(self, kind, key):

        logging.info("--- FIREBASE DELETE ---")
        logging.info(kind)
        logging.info(str(key))

        try:
            f = FirebaseRest(kind + '/' + key)
            r = f.delete()
        except:
            raise Exception("Unable to connect to Firebase!")

    @classmethod
    def put(self, key, priority=None):

        from app.models.trip import Trip
        from app.models.service_order import ServiceOrder
        from app.models.vehicle import Vehicle

        instance = ndb.Key(urlsafe=key).get()
        kind = instance.key.kind().upper()

        data = parse_entity(None, instance)

        # set priority
        if priority is not None:
            dt = data.get(priority, None)
            if dt:
                ts = int(dt.strftime("%s"))
                data.update({'.priority': ts})

        logging.info("--- FIREBASE PUT ---")
        logging.info(kind)
        logging.info(str(instance.status))

        try:
            f = FirebaseRest(kind + '/' + key)
            r = f.set(json_stringify(data))
        except:
            raise Exception("Unable to connect to Firebase!")

    @classmethod
    def custom(self, kind, url, data):
        logging.info("--- CUSTOM PUT ---")

        f = FirebaseRest(kind + '/' + url)
        r = f.set(json_stringify(data))


class FirebaseBehavior(Behavior):

    def tripHandle(self, kind, instance):

        # deal with parent service order first
        # on trips with the following status, its parent Service Order will be removed from CSR dashboard
        if str(instance.status) in ['DISPATCHED', 'ARRIVED', 'STARTED', 'NO_SHOW', 'COMPLETED']:
            d = parse_entity(None, instance)
            FirebaseActions.remove('SERVICEORDER', d.get('service_order_id').key.urlsafe())

        # deal with the actual trip object
        if str(instance.status) in ['COMPLETED'] or instance.is_archived:

            if instance.is_archived or str(instance.payment_method) != 'IN_APP':
                # remove trip in firebase if completed, archived or in-app payment method
                FirebaseActions.remove(kind, instance.key.urlsafe())

        else:
            # add data to firebase
            # do not send trip_pending status
            if str(instance.status) not in ['TRIP_PENDING']:
                # send to firebase
                FirebaseActions.put(instance.key.urlsafe())

    def ServiceOrderHandle(self, kind, instance):
        # REMOVE service order and trip if the statuses are:
        statuses = ['COMPLETED', 'CANCELLED']
        if str(instance.status) in statuses:
            # remove data in firebase
            # FirebaseActions.remove(kind, instance.key.urlsafe())
            FirebaseActions.remove(kind, instance.key.urlsafe())

        else:
            FirebaseActions.put(instance.key.urlsafe(), priority='adjusted_pickup_time')

    def after_put(self, instance):
        logging.info("sending to firebase ... ")

        kind = instance.key.kind().upper()

        if kind == 'TRIP':
            self.tripHandle(kind, instance)

        # check service order and trip for update
        if kind == 'SERVICEORDER':
            self.ServiceOrderHandle(kind, instance)

        # check vehicle for update
        if kind == 'VEHICLE':
            if instance.status == 'PENDING' or instance.status == 'SUSPENDED' or (instance.current_booked_zone == None or instance.current_booked_zone == ''):
                # remove data in firebase
                # FirebaseActions.remove(kind, instance.key.urlsafe())
                FirebaseActions.remove(kind, instance.key.urlsafe())

            else:
                # send to firebase
                # FirebaseActions.put(kind, instance, data)
                FirebaseActions.put(instance.key.urlsafe(), priority='date_booked_on_zone')

    def before_delete(self, instance):
        FirebaseActions.remove(instance.kind().upper(), instance.urlsafe())
        if str(instance.kind().upper()) == 'VEHICLE':
            FirebaseActions.remove('vehicles-current-location', instance.urlsafe())
