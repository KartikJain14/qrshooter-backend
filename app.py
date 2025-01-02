from flask import Flask
from config import Config
from routes.admin_routes import admin_routes
from routes.credit_routes import credit_routes
from routes.user_routes import user_routes
from routes.auth_routes import auth_routes
# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)



app.register_blueprint(admin_routes)
app.register_blueprint(credit_routes)
app.register_blueprint(user_routes)
app.register_blueprint(auth_routes)

if __name__ == '__main__':
    app.run(debug=True, port=app.config['PORT'])