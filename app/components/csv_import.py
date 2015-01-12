import csv
from google.appengine.ext import ndb
import logging

from app.models.account import Account
from app.models.vehicle import Vehicle

# def csv_to_model(csvfile, Account):
#     """
#     Loads a csv file into the database.
    
#     Assumes the first row of the csv file is a list of column names.
#     Assumes a 1-to-1 mapping between csv column names and model properties. 
#     If there is no match, the the csv column will be left out.
#     """
#     allowed_properties = Model._properties.keys()
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         filtered_row = {k: v for k, v in row.iteritems() if k in allowed_properties}
#         item = Account(**filtered_row)
#         item.put()


class CsvReader(object):
    ACCOUNTS = 'Accounts.csv'
    VEHICLE = 'Vehicle.csv'

    @classmethod
    def import_table(self, which):

        with open('sample_data/%s' % which, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            # skip the header
            next(reader,None)
            # read in data
            for row in reader:
                self.import_row(row, which)

    @classmethod
    def import_row(self, row, which):
        if which == self.ACCOUNTS:
            account = Account(
                account_id = row[1],                # Acct Id
                company_name = row[2],              # Account Name
                person_name = None,                 # only from Divisions
                phone_number = row[3],
                address = ("%s, %s, %s, %s, %s, %s" % (row[8], row[9], row[10], row[11], row[12], row[13])),
                driver_voucher = self.safe_cast(None,bool),
                special_requirements = row[0]      # Account Notes
            )
            account.put()

        elif which == self.VEHICLE:
            vehicle = Vehicle(
                vehicle_id = row[0]
            )
            vehicle.put()

    @classmethod
    def safe_cast(self, value, to_type, default=None):
        try:
            return to_type(value)
        except ValueError:
            return default