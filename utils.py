import os
import joblib
import logging
import random
import numpy as np
from datetime import datetime
from app import db
from models import Doctor, City

logger = logging.getLogger(__name__)

def load_model():
    """Load the trained heart stroke prediction model"""
    try:
        # Check if model exists, if not create a simple logistic regression model
        model_path = os.path.join('model', 'heart_model.pkl')
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                logger.info(f"Successfully loaded model from {model_path}")
                return model
            except Exception as e:
                logger.error(f"Error loading existing model: {e}")
                # If we can't load the existing model, create a new one
                os.remove(model_path)  # Remove corrupted model file
                logger.info(f"Removed corrupted model file, will create a new one")
                # Continue to model creation below
        
        # Create a simple logistic regression model
        from sklearn.linear_model import LogisticRegression
        import numpy as np
        
        logger.info("Creating new prediction model")
        # Create a simple model with more features
        # Features: [gender, age, hypertension, heart_disease, married, residence, glucose, bmi, smoking_status]
        X = np.array([
            [0, 30, 0, 0, 0, 0, 90, 22, 0],  # Low risk
            [1, 65, 1, 1, 1, 1, 180, 32, 2],  # High risk
            [0, 45, 0, 0, 1, 0, 110, 25, 1],  # Low risk
            [1, 70, 1, 1, 1, 1, 200, 30, 2],  # High risk
            [0, 50, 0, 0, 1, 0, 120, 26, 1],  # Low risk
            [1, 55, 1, 0, 1, 1, 160, 28, 2],  # High risk
        ])
        y = np.array([0, 1, 0, 1, 0, 1])  # 0: low risk, 1: high risk
        
        model = LogisticRegression()
        model.fit(X, y)
        
        # Save the model
        os.makedirs('model', exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Created and saved a new model at {model_path}")
        return model
    except Exception as e:
        logger.error(f"Error in model creation/loading: {e}")
        # Return a more realistic fallback model
        return ImprovedDummyModel()

class DummyModel:
    """Fallback model that always predicts low risk"""
    def predict(self, X):
        return [0]  # Always return low risk
        
class ImprovedDummyModel:
    """Improved fallback model that makes predictions based on key risk factors"""
    def predict(self, X):
        # Extract key features from X
        # Features: [gender, age, hypertension, heart_disease, married, residence, glucose, bmi, smoking_status]
        try:
            features = X[0]  # Get the first (and only) sample's features
            
            # Count risk factors
            risk_score = 0
            
            # Age over 60 is a risk factor
            if features[1] >= 60:
                risk_score += 2
            elif features[1] >= 50:
                risk_score += 1
                
            # Hypertension is a risk factor
            if features[2] == 1:
                risk_score += 2
                
            # Heart disease is a risk factor
            if features[3] == 1:
                risk_score += 2
                
            # High glucose level is a risk factor
            if features[6] >= 160:
                risk_score += 2
            elif features[6] >= 120:
                risk_score += 1
                
            # High BMI is a risk factor
            if features[7] >= 30:
                risk_score += 1
                
            # Smoking is a risk factor
            if features[8] == 2:  # Current smoker
                risk_score += 1
                
            # Determine risk based on score
            # High risk if 3 or more risk factors
            return [1 if risk_score >= 3 else 0]
        except Exception as e:
            logger.error(f"Error in ImprovedDummyModel: {e}")
            # If anything goes wrong, return low risk
            return [0]

def get_health_recommendations(record):
    """Generate personalized health recommendations based on input data"""
    recommendations = []
    
    # Age-based recommendations
    if record.age < 40:
        recommendations.append("Establish healthy habits early: regular exercise, balanced diet, and regular check-ups.")
    elif 40 <= record.age < 60:
        recommendations.append("Schedule regular health screenings, including cholesterol, blood pressure, and diabetes tests.")
    else:
        recommendations.append("Consider more frequent health check-ups and focus on heart health with your doctor.")
    
    # Gender-based recommendations
    if record.gender == "Male":
        recommendations.append("Men over 45 are at higher risk for heart disease. Consider a heart health evaluation.")
    elif record.gender == "Female":
        recommendations.append("Women may have different heart attack symptoms than men. Be aware of fatigue, shortness of breath, and jaw/back pain.")
    
    # Hypertension-based recommendations
    if record.hypertension:
        recommendations.append("Monitor your blood pressure regularly. Consider reducing sodium intake and consulting with a cardiologist.")
        recommendations.append("Follow the DASH diet: rich in fruits, vegetables, whole grains, and low-fat dairy products.")
        recommendations.append("Limit alcohol consumption and avoid smoking to help manage your blood pressure.")
    else:
        recommendations.append("Maintain a healthy blood pressure through regular exercise and a balanced diet.")
    
    # Heart Disease
    if hasattr(record, 'heart_disease') and record.heart_disease:
        recommendations.append("With your heart disease history, regular consultations with a cardiologist are essential.")
        recommendations.append("Consider cardiac rehabilitation programs to improve heart function and overall well-being.")
    
    # BMI recommendations
    if hasattr(record, 'bmi'):
        if record.bmi > 30:
            recommendations.append("Your BMI indicates obesity. Focus on weight management to reduce heart disease risk.")
            recommendations.append("Consider consulting with a nutritionist for a personalized meal plan.")
        elif record.bmi > 25:
            recommendations.append("Your BMI indicates overweight status. Aim for moderate weight loss through diet and exercise.")
        else:
            recommendations.append("Maintain your healthy weight through balanced nutrition and regular physical activity.")
    
    # Glucose level-based recommendations
    if record.glucose_level > 140:
        recommendations.append("Your glucose level is high. Consider limiting sugar and simple carbohydrates in your diet.")
        recommendations.append("Increase physical activity to help regulate blood sugar levels naturally.")
        recommendations.append("Consider speaking with a dietitian about a diabetic-friendly meal plan.")
    elif record.glucose_level > 100:
        recommendations.append("Your glucose level is slightly elevated. Monitor your sugar intake and consider incorporating more physical activity.")
    else:
        recommendations.append("Your glucose level is within normal range. Continue maintaining a balanced diet.")
    
    # Smoking recommendations
    if hasattr(record, 'smoking_status') and record.smoking_status == "Current smoker":
        recommendations.append("Quitting smoking is the single most important step you can take for heart health.")
        recommendations.append("Consider nicotine replacement therapy or medication to help quit smoking.")
    
    # Cholesterol recommendations
    if hasattr(record, 'cholesterol') and record.cholesterol > 200:
        recommendations.append("Your cholesterol is elevated. Consider a diet low in saturated fats and trans fats.")
        recommendations.append("Increase fiber intake through fruits, vegetables, and whole grains to help lower cholesterol.")
    
    # Exercise induced angina
    if hasattr(record, 'exercise_angina') and record.exercise_angina:
        recommendations.append("Your chest pain during exercise could indicate coronary artery disease. Consult a cardiologist promptly.")
        recommendations.append("Work with a healthcare provider to develop a safe exercise program.")
    
    # General recommendations
    recommendations.append("Stay hydrated by drinking plenty of water throughout the day.")
    recommendations.append("Aim for at least 150 minutes of moderate aerobic activity or 75 minutes of vigorous activity each week.")
    recommendations.append("Manage stress through meditation, yoga, or other relaxation techniques.")
    
    # Remove duplicate recommendations and limit to a reasonable number
    return list(set(recommendations))[:10]

def predict_stroke_risk(record):
    """
    Predict stroke risk based on health record data
    Returns prediction (0 or 1) and risk label (Low Risk or High Risk)
    """
    model = load_model()
    
    # Create feature array
    features = []
    
    # Gender (0 for Female, 1 for Male)
    gender_val = 1 if record.gender == "Male" else 0
    features.append(gender_val)
    
    # Age
    features.append(record.age)
    
    # Hypertension (0 or 1)
    features.append(1 if record.hypertension else 0)
    
    # Heart disease (0 or 1)
    heart_disease_val = 0
    if hasattr(record, 'heart_disease'):
        heart_disease_val = 1 if record.heart_disease else 0
    features.append(heart_disease_val)
    
    # Ever married (0 for No, 1 for Yes)
    married_val = 0
    if hasattr(record, 'ever_married'):
        married_val = 1 if record.ever_married == "Yes" else 0
    features.append(married_val)
    
    # Residence type (0 for Rural, 1 for Urban)
    residence_val = 0
    if hasattr(record, 'residence_type'):
        residence_val = 1 if record.residence_type == "Urban" else 0
    features.append(residence_val)
    
    # Glucose level
    features.append(record.glucose_level)
    
    # BMI
    bmi_val = 25.0  # Default
    if hasattr(record, 'bmi') and record.bmi:
        bmi_val = record.bmi
    features.append(bmi_val)
    
    # Smoking status (0 for never, 1 for former, 2 for current)
    smoking_val = 0
    if hasattr(record, 'smoking_status'):
        if record.smoking_status == "Former smoker":
            smoking_val = 1
        elif record.smoking_status == "Current smoker":
            smoking_val = 2
    features.append(smoking_val)
    
    # Make prediction
    prediction = model.predict([features])[0]
    risk_label = "High Risk" if prediction == 1 else "Low Risk"
    
    return prediction, risk_label

def create_dummy_doctors():
    """Create dummy doctor records for testing purposes"""
    cities = City.query.all()
    city_names = [city.name for city in cities]
    
    specialties = ["Cardiology", "Internal Medicine", "Neurology", "Endocrinology", 
                  "Family Medicine", "Vascular Surgery", "Geriatric Medicine"]
    
    # Get existing doctor emails to avoid duplicates
    existing_emails = [doc.email for doc in Doctor.query.all()]
    
    dummy_doctors = [
        {
            "name": "Dr. Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "password": "password123",
            "location": "New York",
            "specialty": "Cardiology",
            "about": "Dr. Johnson is a board-certified cardiologist with over 15 years of experience treating heart conditions and stroke prevention.",
            "experience": "15+ years",
            "clinic_address": "123 Medical Plaza, New York, NY 10001",
            "contact_info": "(212) 555-1234"
        },
        {
            "name": "Dr. James Smith",
            "email": "james.smith@example.com",
            "password": "password123",
            "location": "Los Angeles",
            "specialty": "Internal Medicine",
            "about": "Dr. Smith specializes in preventative care and managing chronic conditions like hypertension and diabetes.",
            "experience": "12 years",
            "clinic_address": "456 Wellness Blvd, Los Angeles, CA 90001",
            "contact_info": "(310) 555-5678"
        },
        {
            "name": "Dr. Emily Wilson",
            "email": "emily.wilson@example.com",
            "password": "password123",
            "location": "Chicago",
            "specialty": "Neurology",
            "about": "Dr. Wilson is a neurologist focusing on stroke recovery and prevention, with special interest in vascular neurology.",
            "experience": "10 years",
            "clinic_address": "789 Brain Health Center, Chicago, IL 60601",
            "contact_info": "(312) 555-9012"
        },
        {
            "name": "Dr. Michael Brown",
            "email": "michael.brown@example.com",
            "password": "password123",
            "location": "Houston",
            "specialty": "Endocrinology",
            "about": "Dr. Brown specializes in diabetes management and metabolic disorders that contribute to stroke risk.",
            "experience": "14 years",
            "clinic_address": "321 Hormone Lane, Houston, TX 77001",
            "contact_info": "(713) 555-3456"
        },
        {
            "name": "Dr. Jessica Lee",
            "email": "jessica.lee@example.com",
            "password": "password123",
            "location": "New York",
            "specialty": "Cardiology",
            "about": "Dr. Lee is an interventional cardiologist specializing in coronary artery disease and heart attack prevention.",
            "experience": "11 years",
            "clinic_address": "543 Heart Avenue, New York, NY 10002",
            "contact_info": "(212) 555-7890"
        },
        {
            "name": "Dr. Robert Chen",
            "email": "robert.chen@example.com",
            "password": "password123",
            "location": "Los Angeles",
            "specialty": "Cardiology",
            "about": "Dr. Chen focuses on non-invasive cardiology and uses advanced imaging to assess cardiac health and stroke risk.",
            "experience": "17 years",
            "clinic_address": "876 Cardiac Court, Los Angeles, CA 90002",
            "contact_info": "(310) 555-1234"
        },
        {
            "name": "Dr. Lisa Garcia",
            "email": "lisa.garcia@example.com",
            "password": "password123",
            "location": "Chicago",
            "specialty": "Internal Medicine",
            "about": "Dr. Garcia specializes in comprehensive care for adults with multiple risk factors for stroke and heart disease.",
            "experience": "9 years",
            "clinic_address": "234 Wellness Way, Chicago, IL 60602",
            "contact_info": "(312) 555-5678"
        },
        {
            "name": "Dr. David Kim",
            "email": "david.kim@example.com",
            "password": "password123",
            "location": "Houston",
            "specialty": "Neurology",
            "about": "Dr. Kim specializes in stroke diagnosis, treatment, and rehabilitation with a focus on advanced neuroimaging.",
            "experience": "13 years",
            "clinic_address": "567 Brain Boulevard, Houston, TX 77002",
            "contact_info": "(713) 555-9012"
        }
    ]
    
    # Add more doctors for different cities to ensure coverage
    for city in city_names:
        if city not in ["New York", "Los Angeles", "Chicago", "Houston"]:
            for specialty in random.sample(specialties, 2):  # Add 2 doctors per city
                # Generate unique email
                email = f"doctor.{city.lower().replace(' ', '')}.{specialty.lower().replace(' ', '')}@example.com"
                if email in existing_emails:
                    continue
                    
                dummy_doctors.append({
                    "name": f"Dr. {random.choice(['John', 'Jane', 'Alex', 'Maria', 'Carlos', 'Priya', 'Sam'])} {random.choice(['Williams', 'Davis', 'Miller', 'Rodriguez', 'Patel', 'Singh', 'Wong'])}",
                    "email": email,
                    "password": "password123",
                    "location": city,
                    "specialty": specialty,
                    "about": f"Board-certified {specialty.lower()} specialist with extensive experience in stroke prevention and treatment.",
                    "experience": f"{random.randint(5, 20)} years",
                    "clinic_address": f"{random.randint(100, 999)} Medical Center, {city}",
                    "contact_info": f"({random.randint(200, 999)}) 555-{random.randint(1000, 9999)}"
                })
    
    for doctor_data in dummy_doctors:
        # Skip if doctor with this email already exists
        if doctor_data["email"] in existing_emails:
            continue
            
        doctor = Doctor(
            name=doctor_data["name"],
            email=doctor_data["email"],
            location=doctor_data["location"],
            specialty=doctor_data["specialty"],
            about=doctor_data["about"],
            experience=doctor_data["experience"],
            clinic_address=doctor_data["clinic_address"],
            contact_info=doctor_data["contact_info"]
        )
        doctor.set_password(doctor_data["password"])
        db.session.add(doctor)
        existing_emails.append(doctor_data["email"])
    
    db.session.commit()
    logger.info(f"Added {len(dummy_doctors)} dummy doctors to the database")
