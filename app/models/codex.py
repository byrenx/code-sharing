from ferris import BasicModel, ndb
from ferris.behaviors import searchable
from app.behaviors.mail_mehavior import MailBehavior

class Codex(BasicModel):
    class Meta:
        behaviors = (searchable.Searchable, MailBehavior)
        search_index = ('global',)

    codex_id = ndb.StringProperty()
    date_modified = ndb.DateProperty()
