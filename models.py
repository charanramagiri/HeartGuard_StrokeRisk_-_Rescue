from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    about = db.Column(db.Text, nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    clinic_address = db.Column(db.String(200), nullable=True)
    contact_info = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Doctor {self.email}>'


class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Basic info
    gender = db.Column(db.String(10), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    ever_married = db.Column(db.String(3), nullable=True)
    residence_type = db.Column(db.String(10), nullable=True)
    work_type = db.Column(db.String(20), nullable=True)
    
    # Health conditions
    hypertension = db.Column(db.Boolean, nullable=False)
    heart_disease = db.Column(db.Boolean, nullable=True)
    smoking_status = db.Column(db.String(20), nullable=True)
    
    # Medical measurements
    glucose_level = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=True)
    chest_pain_type = db.Column(db.String(30), nullable=True)
    resting_bp = db.Column(db.Integer, nullable=True)
    cholesterol = db.Column(db.Integer, nullable=True)
    fasting_blood_sugar = db.Column(db.Boolean, nullable=True)
    ecg_results = db.Column(db.String(30), nullable=True)
    max_heart_rate = db.Column(db.Integer, nullable=True)
    exercise_angina = db.Column(db.Boolean, nullable=True)
    oldpeak = db.Column(db.Float, nullable=True)
    
    # Prediction and recommendations
    risk_prediction = db.Column(db.String(20), nullable=False)
    recommendations = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship
    user = db.relationship('User', backref=db.backref('health_records', lazy=True))
    
    def __repr__(self):
        return f'<HealthRecord {self.id} for User {self.user_id}>'


# List of cities for doctor location dropdown
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<City {self.name}>'
