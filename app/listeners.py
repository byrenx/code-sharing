"""
Central place to store event listeners for your application,
automatically imported at run time.
"""
from ferris.core.events import on


# example
@on('controller_before_authorization')
def inject_authorization_chains(controller, authorizations):
    pass
