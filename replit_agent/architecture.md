# Architecture Overview

## Overview

HeartGuard is a web application designed to help users assess their risk of heart stroke and connect with specialized doctors. The application provides personalized health recommendations based on user-provided health information and machine learning predictions. It follows a traditional web application architecture with separate user and doctor interfaces.

## System Architecture

HeartGuard follows a Model-View-Controller (MVC) architectural pattern implemented using Flask, a lightweight Python web framework. The application is structured as follows:

- **Frontend**: HTML templates with Bootstrap for styling, minimal JavaScript for client-side interactions
- **Backend**: Python Flask application handling request routing, business logic, and database interactions
- **Database**: SQLAlchemy ORM with SQLite database (configurable to use other databases)
- **Machine Learning**: Scikit-learn based prediction model for heart stroke risk assessment

### Architecture Diagram

```
┌─────────────┐     ┌───────────────────────────────────────┐     ┌─────────────┐
│             │     │               Backend                 │     │             │
│   Browser   │────▶│    (Flask + SQLAlchemy + ML Model)    │────▶│   Database  │
│             │     │                                       │     │             │
└─────────────┘     └───────────────────────────────────────┘     └─────────────┘
       ▲                                 │                               │
       │                                 ▼                               │
       │                        ┌─────────────────┐                      │
       └────────────────────────│  HTML Templates │◀─────────────────────┘
                                └─────────────────┘
```

## Key Components

### Backend Components

1. **Flask Application (`app.py`, `main.py`)**: 
   - Initializes the Flask application
   - Configures database connection
   - Sets up login management
   - Configures application middleware

2. **Models (`models.py`)**: 
   - Defines SQLAlchemy ORM models representing database tables
   - Core entities: User, Doctor, HealthRecord
   - Includes password hashing and authentication methods

3. **Routes (`routes.py`)**:
   - Implements HTTP request handlers
   - Manages page rendering and form processing
   - Handles authentication flows
   - Orchestrates the risk prediction functionality

4. **Utilities (`utils.py`)**:
   - Contains helper functions for the application
   - Loads and manages the machine learning model
   - Implements the risk prediction algorithm
   - Provides health recommendation generation

### Database Schema

The application uses SQLAlchemy ORM with the following main tables:

1. **User**:
   - Basic user attributes (id, email, password_hash, name, location)
   - Authentication methods

2. **Doctor**:
   - Extended user attributes for medical professionals (specialty, about, experience, clinic_address)
   - Authentication methods

3. **HealthRecord**:
   - Stores user health assessment data
   - Links to User model

4. **City** (referenced but not fully visible in the code):
   - Likely stores location information for users and doctors

### Frontend Components

1. **Base Template (`templates/base.html`)**:
   - Defines the common layout and navigation
   - Includes Bootstrap CSS and JavaScript

2. **User Templates**:
   - `index.html`: Landing page
   - `register.html`, `login.html`: Authentication forms
   - `user_dashboard.html`: User's main interface
   - `prediction_form.html`, `prediction_result.html`: Risk assessment workflow
   - `user_history.html`: Health record tracking

3. **Doctor Templates**:
   - `doctor_register.html`, `doctor_login.html`: Authentication for doctors
   - `doctor_dashboard.html`: Doctor's main interface
   - `doctor_profile.html`, `doctor_profile_edit.html`: Profile management
   - `doctors_by_location.html`: Location-based doctor search

4. **Static Assets**:
   - CSS (`static/css/styles.css`): Custom styling beyond Bootstrap
   - JavaScript (`static/js/main.js`): Client-side functionality

### Machine Learning Component

The application incorporates a machine learning model for heart stroke risk prediction:

- Built with scikit-learn (LogisticRegression)
- Uses features like age, gender, hypertension, heart disease, etc.
- Stored as a serialized model file (`model/heart_model.pkl`)
- Fallback mechanism if model file doesn't exist

## Data Flow

### User Registration and Authentication Flow

1. User registers with email, password and basic information
2. Password is hashed and stored in the database
3. On login, password is verified against stored hash
4. Flask-Login manages user sessions
5. Common user loader handles both User and Doctor models

### Risk Assessment Flow

1. User submits health information via assessment form
2. Backend processes and normalizes the input data
3. Machine learning model predicts stroke risk
4. Result is stored in the database as a HealthRecord
5. User is shown results with personalized recommendations

### Doctor Integration Flow

1. Doctors register with professional details
2. Users can search for doctors by location and specialty
3. Doctor profiles are displayed to users based on their risk assessment
4. Location-based matching connects users with nearby specialists

## External Dependencies

### Core Dependencies

1. **Flask**: Web framework for the application
2. **SQLAlchemy**: ORM for database interactions
3. **Flask-Login**: User session management
4. **Flask-WTF**: Form handling and validation
5. **Scikit-learn**: Machine learning for risk prediction
6. **Werkzeug**: Utilities including password hashing and WSGI middleware
7. **Gunicorn**: WSGI HTTP server for production deployment

### Frontend Dependencies

1. **Bootstrap**: CSS framework for responsive design
2. **Font Awesome**: Icon library for the UI

## Deployment Strategy

The application is configured for deployment in a container-based environment:

1. **Application Server**: Gunicorn serves the Flask application
2. **Database**: Configurable via environment variables to use SQLite locally or an external database in production
3. **Environment Configuration**: Uses environment variables for sensitive settings
4. **Connection Pooling**: Configured for database connection recycling and health checks
5. **Scalability**: Deployment configuration supports auto-scaling

### Deployment Configuration

- The application is designed to be deployed on Replit using the `.replit` configuration
- Gunicorn is configured to bind to port 5000
- ProxyFix middleware is used to handle HTTPS reverse proxy
- Database connection pool is configured with recycling and health checks

## Security Considerations

1. **Authentication**: Password hashing using Werkzeug's generate_password_hash
2. **Session Management**: Secret key for session encryption
3. **Database**: Connection pooling with health checks
4. **Configuration**: Environment variables for sensitive settings

## Development Considerations

1. **Local Development**: Development server with debug mode
2. **Database Configuration**: Defaults to SQLite for development
3. **Model Development**: Support for fallback model when trained model is not available