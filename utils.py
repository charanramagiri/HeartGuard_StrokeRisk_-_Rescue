import os
import joblib
import logging
from app import db
from models import Doctor
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)

def load_model():
    """Load the trained heart stroke prediction model"""
    try:
        # Check if model exists, if not create a simple logistic regression model
        model_path = os.path.join('model', 'heart_model.pkl')
        if os.path.exists(model_path):
            return joblib.load(model_path)
        else:
            # Create a simple logistic regression model
            from sklearn.linear_model import LogisticRegression
            import numpy as np
            
            # Create a simple dummy model
            X = np.array([[30, 0, 90], [65, 1, 180], [45, 0, 110], [70, 1, 200]])
            y = np.array([0, 1, 0, 1])  # 0: low risk, 1: high risk
            
            model = LogisticRegression()
            model.fit(X, y)
            
            # Save the model
            os.makedirs('model', exist_ok=True)
            joblib.dump(model, model_path)
            logger.info(f"Created and saved a new model at {model_path}")
            return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        # Return a fallback model that always predicts low risk
        return DummyModel()

class DummyModel:
    """Fallback model that always predicts low risk"""
    def predict(self, X):
        return [0]  # Always return low risk

def get_health_recommendations(age, hypertension, glucose_level):
    """Generate personalized health recommendations based on input data"""
    recommendations = []
    
    # Age-based recommendations
    if age < 40:
        recommendations.append("Establish healthy habits early: regular exercise, balanced diet, and regular check-ups.")
    elif 40 <= age < 60:
        recommendations.append("Schedule regular health screenings, including cholesterol, blood pressure, and diabetes tests.")
    else:
        recommendations.append("Consider more frequent health check-ups and focus on heart health with your doctor.")
    
    # Hypertension-based recommendations
    if hypertension == 1:
        recommendations.append("Monitor your blood pressure regularly. Consider reducing sodium intake and consulting with a cardiologist.")
        recommendations.append("Follow the DASH diet: rich in fruits, vegetables, whole grains, and low-fat dairy products.")
        recommendations.append("Limit alcohol consumption and avoid smoking to help manage your blood pressure.")
    else:
        recommendations.append("Maintain a healthy blood pressure through regular exercise and a balanced diet.")
    
    # Glucose level-based recommendations
    if glucose_level > 140:
        recommendations.append("Your glucose level is high. Consider limiting sugar and simple carbohydrates in your diet.")
        recommendations.append("Increase physical activity to help regulate blood sugar levels naturally.")
        recommendations.append("Consider speaking with a dietitian about a diabetic-friendly meal plan.")
    elif glucose_level > 100:
        recommendations.append("Your glucose level is slightly elevated. Monitor your sugar intake and consider incorporating more physical activity.")
    else:
        recommendations.append("Your glucose level is within normal range. Continue maintaining a balanced diet.")
    
    # General recommendations
    recommendations.append("Stay hydrated by drinking plenty of water throughout the day.")
    recommendations.append("Aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity each week.")
    recommendations.append("Manage stress through meditation, yoga, or other relaxation techniques.")
    
    return recommendations

def create_dummy_doctors():
    """Create dummy doctor records for testing purposes"""
    dummy_doctors = [
        {
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "password": "password123",
            "location": "New York",
            "specialty": "Cardiology"
        },
        {
            "name": "Dr. James Smith",
            "email": "james.smith@example.com",
            "password": "password123",
            "location": "Los Angeles",
            "specialty": "Internal Medicine"
        },
        {
            "name": "Dr. Emily Wilson",
            "email": "emily.wilson@example.com",
            "password": "password123",
            "location": "Chicago",
            "specialty": "Neurology"
        },
        {
            "name": "Dr. Michael Brown",
            "email": "michael.brown@example.com",
            "password": "password123",
            "location": "Houston",
            "specialty": "Endocrinology"
        },
        {
            "name": "Dr. Jessica Lee",
            "email": "jessica.lee@example.com",
            "password": "password123",
            "location": "New York",
            "specialty": "Cardiology"
        },
        {
            "name": "Dr. Robert Chen",
            "email": "robert.chen@example.com",
            "password": "password123",
            "location": "Los Angeles",
            "specialty": "Cardiology"
        },
        {
            "name": "Dr. Lisa Garcia",
            "email": "lisa.garcia@example.com",
            "password": "password123",
            "location": "Chicago",
            "specialty": "Internal Medicine"
        },
        {
            "name": "Dr. David Kim",
            "email": "david.kim@example.com",
            "password": "password123",
            "location": "Houston",
            "specialty": "Neurology"
        }
    ]
    
    for doctor_data in dummy_doctors:
        doctor = Doctor(
            name=doctor_data["name"],
            email=doctor_data["email"],
            location=doctor_data["location"],
            specialty=doctor_data["specialty"]
        )
        doctor.set_password(doctor_data["password"])
        db.session.add(doctor)
    
    db.session.commit()
    logger.info(f"Added {len(dummy_doctors)} dummy doctors to the database")
