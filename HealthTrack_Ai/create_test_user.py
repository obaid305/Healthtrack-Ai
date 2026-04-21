# create_test_user.py
from database import Database
from auth import Auth

db = Database()
auth = Auth(db)

# Create a test user
success, message = auth.register(
    full_name="Test User",
    email="test@example.com",
    password="Test@123",
    phone="1234567890"
)

if success:
    print("✓ Test user created successfully")
    print("  Email: test@example.com")
    print("  Password: Test@123")
else:
    print(f"✗ {message}")
