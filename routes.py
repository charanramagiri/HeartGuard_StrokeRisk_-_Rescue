import os
import joblib
import numpy as np
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, logger
from models import User, Doctor, HealthRecord
from utils import get_health_recommendations, load_model

# Load the model at startup
model = load_model()

@app.route('/')
def index():
    """Homepage route"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location')
        
        # Validation
        if not all([name, email, password, confirm_password, location]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            location=location
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during user registration: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Set session variables
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_location'] = user.location
            session['user_type'] = 'user'
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('prediction_form'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    """Doctor registration route"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        location = request.form.get('location')
        specialty = request.form.get('specialty')
        
        # Validation
        if not all([name, email, password, confirm_password, location, specialty]):
            flash('All fields are required', 'danger')
            return render_template('doctor_register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('doctor_register.html')
        
        # Check if doctor already exists
        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('doctor_login'))
        
        # Create new doctor
        new_doctor = Doctor(
            name=name,
            email=email,
            location=location,
            specialty=specialty
        )
        new_doctor.set_password(password)
        
        try:
            db.session.add(new_doctor)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('doctor_login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during doctor registration: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('doctor_register.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find doctor by email
        doctor = Doctor.query.filter_by(email=email).first()
        
        if doctor and doctor.check_password(password):
            # Set session variables
            session['user_id'] = doctor.id
            session['user_name'] = doctor.name
            session['user_location'] = doctor.location
            session['user_specialty'] = doctor.specialty
            session['user_type'] = 'doctor'
            flash(f'Welcome back, Dr. {doctor.name}!', 'success')
            return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('doctor_login.html')

@app.route('/logout')
def logout():
    """Logout route for both users and doctors"""
    # Clear session data
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/prediction', methods=['GET', 'POST'])
def prediction_form():
    """Prediction form route"""
    # Check if user is logged in
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            age = int(request.form.get('age'))
            hypertension = int(request.form.get('hypertension'))
            glucose_level = float(request.form.get('glucose_level'))
            
            # Validate input data
            if age < 0 or age > 120:
                flash('Please enter a valid age', 'danger')
                return render_template('prediction_form.html')
                
            if hypertension not in [0, 1]:
                flash('Hypertension must be 0 or 1', 'danger')
                return render_template('prediction_form.html')
                
            if glucose_level < 0:
                flash('Please enter a valid glucose level', 'danger')
                return render_template('prediction_form.html')
            
            # Prepare data for prediction
            data = np.array([[age, hypertension, glucose_level]])
            
            # Make prediction
            prediction = model.predict(data)[0]
            prediction_label = "High Risk" if prediction == 1 else "Low Risk"
            
            # Get recommendations based on input data
            recommendations = get_health_recommendations(age, hypertension, glucose_level)
            
            # Find doctors in the same location as the user
            user_location = session.get('user_location')
            nearby_doctors = Doctor.query.filter_by(location=user_location).all()
            
            # Save the health record to the database
            health_record = HealthRecord(
                user_id=session.get('user_id'),
                age=age,
                hypertension=bool(hypertension),
                glucose_level=glucose_level,
                risk_prediction=prediction_label
            )
            
            db.session.add(health_record)
            db.session.commit()
            
            return render_template(
                'prediction_result.html',
                prediction=prediction_label,
                recommendations=recommendations,
                nearby_doctors=nearby_doctors,
                age=age,
                hypertension=hypertension,
                glucose_level=glucose_level
            )
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            flash('An error occurred during prediction. Please try again.', 'danger')
            return render_template('prediction_form.html')
    
    return render_template('prediction_form.html')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    """Doctor dashboard route"""
    # Check if doctor is logged in
    if 'user_id' not in session or session.get('user_type') != 'doctor':
        flash('Please login as a doctor to access this page', 'warning')
        return redirect(url_for('doctor_login'))
    
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor information not found', 'danger')
        return redirect(url_for('doctor_login'))
    
    return render_template('doctor_dashboard.html', doctor=doctor)

@app.route('/user/history')
def user_history():
    """User health records history route"""
    # Check if user is logged in
    if 'user_id' not in session or session.get('user_type') != 'user':
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    health_records = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).all()
    
    return render_template('user_history.html', health_records=health_records)
