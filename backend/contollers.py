 
from .models import *   

from .routes.auth import auth_routes
from .routes.admin import admin_routes
from .routes.customer import customer_routes
from .routes.professional import professional_routes

 
def register_routes(app):
    auth_routes(app)
    admin_routes(app)
    customer_routes(app)
    professional_routes(app)
