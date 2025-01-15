from flask import Flask, Blueprint
from config import Config
from routes.admin_routes import admin_routes
from routes.credit_routes import credit_routes
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
from routes.website_routes import website_routes
from dotenv import load_dotenv
import os

ADMIN_PATH=os.getenv("ADMIN_PORTAL") or "/admin"

load_dotenv()
# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
# Register website_routes without prefix since it handles main routes
app.register_blueprint(website_routes, url_prefix=ADMIN_PATH)
app.register_blueprint(admin_routes, url_prefix='/admin')
app.register_blueprint(credit_routes)
app.register_blueprint(user_routes, url_prefix="/user")
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])