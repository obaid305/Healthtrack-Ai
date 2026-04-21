# test_prediction.py
from prediction_routes import PredictionRoutes
from database import Database

print("Testing Prediction Routes...")

# Create instance
db = Database()
pred = PredictionRoutes(db=db)

# Test with some symptoms
test_symptoms = ['fever', 'cough', 'fatigue']
print(f"\nTesting with symptoms: {test_symptoms}")

result = pred.predict(test_symptoms)
print("Result:", result)

print("\nTest complete!")