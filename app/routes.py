from ferris.core import routing

# Routes all App handlers
routing.auto_route()

# Default root route
routing.redirect("/",  to="/code_share/index")
