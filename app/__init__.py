from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    from . import routes
    app.register_blueprint(routes.main)
    app.register_blueprint(routes.service_bp)
    app.register_blueprint(routes.category_bp)
    app.register_blueprint(routes.service_type_bp)
    app.register_blueprint(routes.appointment_bp)
    
    return app
