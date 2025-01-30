import os
from flask import Flask, redirect, request
from config import Config
from routes.admin_routes import admin_routes
from routes.credit_routes import credit_routes
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
from routes.website_routes import website_routes
from routes.data_routes import data_routes

ADMIN_PATH=os.getenv("ADMIN_PORTAL") or "/admin"

## Initialize Flask app


app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'

# Register blueprints
# Register website_routes without prefix since it handles main routes
app.register_blueprint(website_routes, url_prefix=ADMIN_PATH)
app.register_blueprint(admin_routes, url_prefix='/admin')
app.register_blueprint(credit_routes)
app.register_blueprint(user_routes, url_prefix="/user")
app.register_blueprint(auth_routes)
app.register_blueprint(data_routes)

@app.route('/')
def home():
    return redirect("https://taqneeqfest.com/")

@app.route('/favicon.ico')
@app.route('/robots.txt')
@app.route('/sitemap.xml')
@app.route('/security.txt')
def static_from_root():
    return app.send_static_file(request.path[1:])

if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])