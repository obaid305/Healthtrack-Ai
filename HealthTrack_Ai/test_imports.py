# test_imports.py
print("Testing imports...")

try:
    from flask import Flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print(f"✗ Flask import failed: {e}")

try:
    import mysql.connector
    print("✓ MySQL connector imported successfully")
except ImportError as e:
    print(f"✗ MySQL connector import failed: {e}")

try:
    import sklearn
    print(f"✓ scikit-learn {sklearn.__version__} imported successfully")
except ImportError as e:
    print(f"✗ scikit-learn import failed: {e}")

print("\nChecking project files...")

try:
    from doctor_routes import DoctorRoutes
    print("✓ doctor_routes.py found")
except ImportError as e:
    print(f"✗ doctor_routes.py not found: {e}")

try:
    from appointment_routes import AppointmentRoutes
    print("✓ appointment_routes.py found")
except ImportError as e:
    print(f"✗ appointment_routes.py not found: {e}")

try:
    from prediction_routes import PredictionRoutes
    print("✓ prediction_routes.py found")
except ImportError as e:
    print(f"✗ prediction_routes.py not found: {e}")

try:
    from auth import Auth
    print("✓ auth.py found")
except ImportError as e:
    print(f"✗ auth.py not found: {e}")

try:
    from database import Database
    print("✓ database.py found")
except ImportError as e:
    print(f"✗ database.py not found: {e}")