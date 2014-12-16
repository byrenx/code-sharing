from ferris.core import routing, plugins

# Routes all App handlers
routing.auto_route()

# Default root route
routing.redirect("/",  to="/code_share/index")



# Plugins
#plugins.enable('settings')
#plugins.enable('oauth_manager')
