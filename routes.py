import os
import joblib
import numpy as np
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, logger, login_manager
from models import User, Doctor, HealthRecord, City
from utils import predict_stroke_risk, get_health_recommendations

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
    
    # Get list of cities for dropdown
    cities = City.query.all()
    return render_template('register.html', cities=cities)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Log in with Flask-Login
            login_user(user)
            
            # Set session variables
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_location'] = user.location
            session['user_type'] = 'user'
            
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Check if user has prediction history
            has_predictions = HealthRecord.query.filter_by(user_id=user.id).count() > 0
            if has_predictions:
                return redirect(url_for('user_dashboard'))
            else:
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
    
    # Get list of cities for dropdown
    cities = City.query.all()
    specialties = ["Cardiology", "Internal Medicine", "Neurology", "Endocrinology", 
                  "Family Medicine", "Vascular Surgery", "Geriatric Medicine"]
    
    return render_template('doctor_register.html', cities=cities, specialties=specialties)

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    """Doctor login route"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find doctor by email
        doctor = Doctor.query.filter_by(email=email).first()
        
        if doctor and doctor.check_password(password):
            # Log in with Flask-Login
            login_user(doctor)
            
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
@login_required
def logout():
    """Logout route for both users and doctors"""
    # Clear session data
    logout_user()
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard route"""
    # Check if user is logged in as a patient
    if session.get('user_type') != 'user':
        flash('Please login as a patient to access this page', 'warning')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    # Get user health records
    health_records = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).all()
    
    # Get latest health record if exists
    latest_record = health_records[0] if health_records else None
    
    # Find doctors in the same location as the user
    user_location = session.get('user_location')
    nearby_doctors = Doctor.query.filter_by(location=user_location).all()
    
    # Get all cities for dropdown
    cities = City.query.all()
    
    return render_template(
        'user_dashboard.html',
        health_records=health_records,
        latest_record=latest_record,
        nearby_doctors=nearby_doctors,
        cities=cities
    )

@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction_form():
    """Prediction form route"""
    # Check if user is logged in as a patient
    if session.get('user_type') != 'user':
        flash('Please login as a patient to access this page', 'warning')
        return redirect(url_for('login'))
    
    # Get all cities for location dropdown
    cities = City.query.all()
    
    if request.method == 'POST':
        try:
            # Get basic form data
            gender = request.form.get('gender')
            age = int(request.form.get('age'))
            hypertension = request.form.get('hypertension') == 'true'
            heart_disease = request.form.get('heart_disease') == 'true'
            ever_married = request.form.get('ever_married')
            residence_type = request.form.get('residence_type')
            work_type = request.form.get('work_type')
            
            # Get medical measurements
            glucose_level = float(request.form.get('glucose_level'))
            bmi = float(request.form.get('bmi') or 0)
            smoking_status = request.form.get('smoking_status')
            
            # Get cardiac-specific data
            chest_pain_type = request.form.get('chest_pain_type')
            resting_bp = int(request.form.get('resting_bp') or 0)
            cholesterol = int(request.form.get('cholesterol') or 0)
            fasting_blood_sugar = request.form.get('fasting_blood_sugar') == 'true'
            ecg_results = request.form.get('ecg_results')
            max_heart_rate = int(request.form.get('max_heart_rate') or 0)
            exercise_angina = request.form.get('exercise_angina') == 'true'
            oldpeak = float(request.form.get('oldpeak') or 0)
            
            # Basic validation
            if age < 0 or age > 120:
                flash('Please enter a valid age', 'danger')
                return render_template('prediction_form.html', cities=cities)
            
            if glucose_level < 0:
                flash('Please enter a valid glucose level', 'danger')
                return render_template('prediction_form.html', cities=cities)
            
            # Create a health record
            health_record = HealthRecord(
                user_id=session.get('user_id'),
                gender=gender,
                age=age,
                hypertension=hypertension,
                heart_disease=heart_disease,
                ever_married=ever_married,
                residence_type=residence_type,
                work_type=work_type,
                glucose_level=glucose_level,
                bmi=bmi,
                smoking_status=smoking_status,
                chest_pain_type=chest_pain_type,
                resting_bp=resting_bp,
                cholesterol=cholesterol,
                fasting_blood_sugar=fasting_blood_sugar,
                ecg_results=ecg_results,
                max_heart_rate=max_heart_rate,
                exercise_angina=exercise_angina,
                oldpeak=oldpeak
            )
            
            # Make prediction
            prediction, prediction_label = predict_stroke_risk(health_record)
            health_record.risk_prediction = prediction_label
            
            # Generate recommendations
            recommendations = get_health_recommendations(health_record)
            health_record.recommendations = "\n".join(recommendations)
            
            # Save to database
            db.session.add(health_record)
            db.session.commit()
            
            # Find doctors in the same location as the user
            user_location = session.get('user_location')
            nearby_doctors = Doctor.query.filter_by(location=user_location).all()
            
            return render_template(
                'prediction_result.html',
                prediction=prediction_label,
                recommendations=recommendations,
                nearby_doctors=nearby_doctors,
                health_record=health_record
            )
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            flash('An error occurred during prediction. Please try again.', 'danger')
            return render_template('prediction_form.html', cities=cities)
    
    return render_template('prediction_form.html', cities=cities)

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    """Doctor dashboard route"""
    # Check if doctor is logged in
    if session.get('user_type') != 'doctor':
        flash('Please login as a doctor to access this page', 'warning')
        return redirect(url_for('doctor_login'))
    
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor information not found', 'danger')
        return redirect(url_for('doctor_login'))
    
    return render_template('doctor_dashboard.html', doctor=doctor)

@app.route('/doctor/profile/edit', methods=['GET', 'POST'])
@login_required
def doctor_profile_edit():
    """Doctor profile edit route"""
    # Check if doctor is logged in
    if session.get('user_type') != 'doctor':
        flash('Please login as a doctor to access this page', 'warning')
        return redirect(url_for('doctor_login'))
    
    doctor_id = session.get('user_id')
    doctor = Doctor.query.get(doctor_id)
    
    if not doctor:
        flash('Doctor information not found', 'danger')
        return redirect(url_for('doctor_login'))
    
    if request.method == 'POST':
        # Get form data
        about = request.form.get('about')
        specialty = request.form.get('specialty')
        experience = request.form.get('experience')
        clinic_address = request.form.get('clinic_address')
        contact_info = request.form.get('contact_info')
        location = request.form.get('location')
        
        # Update doctor profile
        doctor.about = about
        doctor.specialty = specialty
        doctor.experience = experience
        doctor.clinic_address = clinic_address
        doctor.contact_info = contact_info
        doctor.location = location
        
        try:
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('doctor_dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating doctor profile: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')
    
    cities = City.query.all()
    specialties = ["Cardiology", "Internal Medicine", "Neurology", "Endocrinology", 
                  "Family Medicine", "Vascular Surgery", "Geriatric Medicine"]
    
    return render_template('doctor_profile_edit.html', doctor=doctor, cities=cities, specialties=specialties)

@app.route('/user/history')
@login_required
def user_history():
    """User health records history route"""
    # Check if user is logged in
    if session.get('user_type') != 'user':
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    health_records = HealthRecord.query.filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).all()
    
    return render_template('user_history.html', health_records=health_records)

@app.route('/doctors/location/<location>')
def doctors_by_location(location):
    """Show doctors by location"""
    specialty = request.args.get('specialty')
    
    # Base query
    query = Doctor.query.filter_by(location=location)
    
    # Add specialty filter if provided
    if specialty:
        query = query.filter_by(specialty=specialty)
    
    # Get doctors
    doctors = query.all()
    
    # Get all cities for dropdown
    cities = City.query.all()
    
    return render_template(
        'doctors_by_location.html', 
        location=location, 
        doctors=doctors, 
        cities=cities, 
        specialty=specialty
    )

@app.route('/doctor/profile/<int:doctor_id>')
def doctor_profile(doctor_id):
    """Doctor public profile page"""
    doctor = Doctor.query.get_or_404(doctor_id)
    # Get all cities for location dropdown navigation
    cities = City.query.all()
    return render_template('doctor_profile.html', doctor=doctor, cities=cities)
