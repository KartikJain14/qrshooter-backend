from flask import Flask, Blueprint
from config import Config
from routes import (
    admin_routes,
    credit_routes,
    user_routes,
    auth_routes,
    website_routes,
    data_routes
    )
import os

ADMIN_PATH=os.getenv("ADMIN_PORTAL") or "/admin"

## Initialize Flask app


app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
# Register website_routes without prefix since it handles main routes
app.register_blueprint(website_routes, url_prefix=ADMIN_PATH)
app.register_blueprint(admin_routes, url_prefix='/admin')
app.register_blueprint(credit_routes)
app.register_blueprint(user_routes, url_prefix="/user")
app.register_blueprint(auth_routes)
app.register_blueprint(data_routes)

if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])