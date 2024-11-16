# Import shared modules
from .models import *  # Import your database models

# Import route modules (optional; useful for centralizing imports)
from .routes.auth import auth_routes
from .routes.admin import admin_routes
from .routes.customer import customer_routes
from .routes.professional import professional_routes

# Optional: Define a utility function for route registration
def register_routes(app):
    auth_routes(app)
    admin_routes(app)
    customer_routes(app)
    professional_routes(app)
