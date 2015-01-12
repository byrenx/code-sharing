import logging


def results_to_dict(cls, items, limit=None):
    limit = 500 if limit is None else limit
    items = cls.components.pagination.paginate(query=items, cursor=cls.request.get('cursor'), limit=limit)
    build = []
    data = {}
    if items:
        for item in items:
            build.append(parse_entity(cls, item))
        data['items'] = build
        if cls.context.get('paging', None):
            data['next_cursor'] = cls.context.get('paging').get('next_cursor')
            data['previous_cursor'] = cls.context.get('paging').get('previous_cursor')
    return cls.util.stringify_json(data)


def parse_entity(cls, item, convert_to_string=False):
    from app.models.service_order import ServiceOrder
    from app.models.trip import Trip
    from app.models.beck_user import BeckUser
    from app.models.vehicle import Vehicle
    from app.models.address import Address

    i = {}
    i['key'] = item.key.urlsafe()
    for name, value in item.to_dict().items():

        """ check if value is a Key """

        if str(type(value)) == "<class 'google.appengine.ext.ndb.key.Key'>":

            """ extract data """
            val = value.get()

            try:
                """ for address objects only """
                if val.json_result:

                    """ nullifying json geo data for optimization"""
                    new = {}
                    for n in filter(lambda a: not a.startswith('__'), dir(val)):
                        new[n] = {} if n == 'json_result' else getattr(val, n)
                    i[name] = new

                else:
                    i[name] = val
            except:

                """ everything else goes here """
                i[name] = val
        else:
            i[name] = value

    if convert_to_string:
        i = cls.util.stringify_json(i)

    return i


def check_json(string):
        import json
        try:
            data = json.loads(string)
        except:
            data = False

        logging.info("JSON data ===============>")
        logging.info(data)
        return data
