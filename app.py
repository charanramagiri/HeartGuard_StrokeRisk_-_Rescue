import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///heartguard.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User, Doctor
    # Try to load user first
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not found, try to load doctor
    return Doctor.query.get(int(user_id))

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    from models import User, Doctor, HealthRecord, City
    
    # Check if we need to handle database migration for tables
    inspector = db.inspect(db.engine)
    
    # Doctor table columns check
    doctor_columns = [col['name'] for col in inspector.get_columns('doctor')] if inspector.has_table('doctor') else []
    
    # Health record table columns check
    health_record_columns = [col['name'] for col in inspector.get_columns('health_record')] if inspector.has_table('health_record') else []
    
    # Import text for raw SQL
    from sqlalchemy import text
    
    # If the doctor table exists but doesn't have the new columns, drop and recreate it
    if inspector.has_table('doctor') and ('about' not in doctor_columns or 
                                         'experience' not in doctor_columns or 
                                         'clinic_address' not in doctor_columns or 
                                         'contact_info' not in doctor_columns):
        logger.info("Updating Doctor table schema with new columns")
        # Use raw SQL to drop the table safely
        db.session.execute(text("DROP TABLE IF EXISTS doctor"))
        db.session.commit()
    
    # If the health_record table exists but doesn't have the new columns, drop and recreate it
    if inspector.has_table('health_record') and ('gender' not in health_record_columns or 
                                               'heart_disease' not in health_record_columns or 
                                               'recommendations' not in health_record_columns):
        logger.info("Updating HealthRecord table schema with new columns")
        # Use raw SQL to drop the table safely
        db.session.execute(text("DROP TABLE IF EXISTS health_record"))
        db.session.commit()
    
    # Now create all tables
    db.create_all()
    
    # Add cities if they don't exist
    if City.query.count() == 0:
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                 "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        for city_name in cities:
            city = City(name=city_name)
            db.session.add(city)
        db.session.commit()
        logger.info("Added cities to the database")

    # Check if there are any doctors in the database, if not, create some dummy doctors
    if Doctor.query.count() == 0:
        from utils import create_dummy_doctors
        create_dummy_doctors()
        logger.info("Created dummy doctor records")

# Import routes after app and db are initialized
from routes import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
