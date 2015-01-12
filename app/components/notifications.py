from app.services.gcm_api import GCM_API
from app.controllers.apns_api import ApnsApi
from binascii import a2b_base64, hexlify
import logging


class Notifications(object):

    def __init__(self):
        self.gcm = GCM_API()
        self.g_tokens = []
        self.a_tokens = []

    def get_token(self, entity):
        # check google tokens
        try:
            g = entity.google_push_notification_token
            if g is not None or g != '' or g != 'None' or g != 'none':
                if g not in self.g_tokens:
                    self.g_tokens.append(g)
        except:
            pass

        # check apple tokens
        # due to the fact that someone does not know how to follow the specs,
        # we need to do this additional convertion of token for IOS
        # base 64 to hexa
        try:
            a = entity.apple_push_notification_token
            if a is not None or a != '' or a != 'None' or a != 'none':
                if a not in self.a_tokens:
                    self.a_tokens.append(a)

            # if not error:
            #     a = str(hexlify(a2b_base64(a))).upper()
            #     error = False
            # else:
            #     a = None
        except:
            # a = None
            # logging.info("TypeError: Non-hexadecimal digit found in APN token : %s" % (a))
            # error = True
            pass

        # if not error and a:
        #    self.a_tokens.append(a)

    def notify(self, data, entity, message=None, is_multiple=False):

        self.g_tokens = []
        self.a_tokens = []

        if is_multiple:
            for item in entity:
                self.get_token(item)
            marker = None
        else:
            self.get_token(entity)
            marker = entity.key.urlsafe()

        action = data.get('ACTION', '')

        logging.info("g token => %s" % self.g_tokens)
        logging.info("a token => %s" % self.a_tokens)
        logging.info("action => %s" % action)
        logging.info("data => %s" % data)
        logging.info("push message => %s" % message)

        self.push(data, self.g_tokens, self.a_tokens, message, action, marker)

    def push(self, data, g_tokens, a_tokens, message, action=None, marker=None):
        # google push
        if len(self.g_tokens) > 0:
            self.gcm.notify(data, g_tokens, action + "_" + str(marker), message=message)

        # apple push
        try:
            if len(self.a_tokens) > 0:
                ApnsApi.notify(data, a_tokens, ios_message=message)
        except:
            logging.info("apple push failed : %s" % (a_tokens))

    def customer_registered(self, customer):
        data = {
            "ACTION": "CUSTOMER_REGISTERED",
        }
        self.notify(data, customer, message="You are now registered.")

    def customer_paid(self, customer):
        data = {
            "ACTION": "PAYMENT_SUCCESS",
        }
        self.notify(data, customer, message="Payment Received.")

    def inform_vehicle_of_payment(self, vehicle, trip_key):
        data = {
            "ACTION": "CUSTOMER_PAID",
            "TRIP_KEY": trip_key
        }
        self.notify(data, vehicle, message="Customer Paid.")

    def trip_assigned_to_vehicle(self, vehicle, trip_id, service_order_key):
        data = {
            "ACTION": "TRIP_ASSIGNED",
            "TRIP_ID": trip_id,
            "SERVICE_ORDER_KEY": service_order_key
        }
        self.notify(data, vehicle, message="A new trip has been assigned to you.")

    def trip_forced_dispatched(self, vehicle, trip_id, service_order_key):
        data = {
            "ACTION": "TRIP_FORCED",
            "TRIP_ID": trip_id,
            "SERVICE_ORDER_KEY": service_order_key
        }
        self.notify(data, vehicle, message="Force dispatch.")

    def trip_undispatched_to_vehicle(self, vehicle, trip_id, service_order_key):
        data = {
            "ACTION": "TRIP_UNDISPATCHED",
            "TRIP_ID": trip_id,
            "SERVICE_ORDER_KEY": service_order_key
        }
        self.notify(data, vehicle, message="Your trip has been undispatched.")

    def vehicle_verified(self, vehicle):
        data = {
            "ACTION": "VEHICLE_VERIFIED",
        }
        self.notify(data, vehicle, message="Your app is now verified.")

    def trip_edited(self, vehicle, trip_id):
        data = {
            "ACTION": "TRIP_CHANGED",
            "TRIP_ID": trip_id
        }
        self.notify(data, vehicle, message="Your current trip has been modified.")

    def trip_cancelled(self, vehicle, trip_id, service_order_key):
        data = {
            "ACTION": "TRIP_CANCELLED",
            "TRIP_ID": trip_id,
            "SERVICE_ORDER_KEY": service_order_key
        }
        self.notify(data, vehicle, message="The current trip has been cancelled.")

    def service_order_cancelled(self, customer, service_order_key):
        data = {
            "ACTION": "SOC",
            "SO": service_order_key
        }
        self.notify(data, customer, message="Your Beck Taxi has been cancelled.")

    def vehicle_accepts_trip(self, customer, vehicle_id, vehicle_key, estimate, service_order_key):
        data = {
            "ACTION": "TA",
            "ID": vehicle_id,
            "VK": vehicle_key,
            "EST": estimate,
            "SO": service_order_key
        }
        message = vehicle_id
        logging.info("vehicle_accepts_trip  data ==> %s" % data)
        self.notify(data, customer, message=message)

    def vehicle_booked_out_of_zone(self, vehicle):
        data = {
            "ACTION": "VEHICLE_BOOKED_OUT",
        }
        self.notify(data, vehicle, message="You've been booked out of the zone.")

    def vehicle_booked_in_of_zone(self, vehicle, zone):
        data = {
            "ACTION": "VEHICLE_BOOKED_IN",
            "ZONE": zone
        }
        self.notify(data, vehicle, message="You've been booked in zone %s" % zone)

    def vehicle_manual_booked_in_zone(self, vehicle, zone):
        data = {
            "ACTION": "MANUAL_BOOKED_IN",
            "ZONE": zone
        }
        self.notify(data, vehicle, message="You've been manually booked in zone %s" % zone)

    def vehicle_arrived(self, customer, vehicle_id, trip_id, service_order_key):
        data = {
            "ACTION": "VA",
            "ID": vehicle_id,
            "TID": trip_id,
            "SO": service_order_key
        }
        self.notify(data, customer, message="Arrived")

    def vehicle_completed_the_trip(self, customer, vehicle_id, trip_id, service_order_key):
        data = {
            "ACTION": "TC",
            "TID": trip_id,
            "SO": service_order_key
        }
        self.notify(data, customer, message="Complete.")

    def customer_no_show(self, customer, service_order_key):
        data = {
            "ACTION": "NO_SHOW",
            "SO": service_order_key
        }
        self.notify(data, customer, message="Your Beck Taxi has left.")

    """ This method is intended for Vehicle and Customer Models to use """
    def message_send_alert(self, entity, message_id):
        data = {
            "ACTION": "MESSAGE_ALERT",
            "MESSAGE_ID": message_id
        }
        self.notify(data, entity, message="You have received a messsage.", is_multiple=True)

    def vehicle_logout_alert(self, entity, vehicle_id):
        data = {
            "ACTION": "VEHICLE_LOGGED_OUT",
            "VEHICLE_ID": vehicle_id
        }
        self.notify(data, entity, message="Your vehicle has been logged out.")

    def vehicle_suspended_alert(self, entity, vehicle_id):
        data = {
            "ACTION": "VEHICLE_SUSPENDED",
            "VEHICLE_ID": vehicle_id
        }
        self.notify(data, entity, message="Your vehicle has been suspended.")

    def send_out_cloud_data_url(self, entity, url, multi=False):
        data = {
            "ACTION": "ZONE_INFO_DATA",
            "URL": url
        }
        message = "Cloud Data URL has been changed."
        if multi is False:
            self.notify(data, entity, message=message)
        else:
            self.notify(data, entity, message=message, is_multiple=True)
