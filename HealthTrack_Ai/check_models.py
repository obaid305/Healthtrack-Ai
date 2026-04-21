import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
import os
import warnings
warnings.filterwarnings('ignore')

print("="*50)
print("Recreating Model Files")
print("="*50)

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

# Expanded symptom list
symptom_names = [
    'fever', 'cough', 'headache', 'fatigue', 'rash', 
    'nausea', 'chest_pain', 'shortness_of_breath', 'joint_pain', 
    'back_pain', 'abdominal_pain', 'dizziness', 'sore_throat',
    'runny_nose', 'muscle_ache', 'chills', 'vomiting', 'diarrhea',
    'constipation', 'bloating', 'itching', 'skin_redness', 'swelling',
    'numbness', 'anxiety', 'depression', 'insomnia', 'palpitations',
    'wheezing', 'loss_of_appetite', 'weight_loss', 'hair_loss'
]

# Save symptom names
with open('models/symptom_names.pkl', 'wb') as f:
    pickle.dump(symptom_names, f)
print(f"✓ Created symptom_names.pkl with {len(symptom_names)} symptoms")

# Disease list
diseases = [
    'Common Cold', 'Influenza', 'Migraine', 'Dermatitis',
    'Gastroenteritis', 'Hypertension', 'Diabetes', 'Arthritis',
    'Asthma', 'Pneumonia', 'COVID-19', 'Allergies',
    'Anxiety Disorder', 'Depression', 'GERD', 'Urinary Tract Infection',
    'Strep Throat', 'Bronchitis', 'Sinusitis', 'Eczema',
    'Psoriasis', 'Rheumatoid Arthritis', 'Osteoarthritis',
    'Sciatica', 'Conjunctivitis', 'Tonsillitis'
]

# Create and save label encoder
label_encoder = LabelEncoder()
label_encoder.fit(diseases)
with open('models/disease_label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
print(f"✓ Created disease_label_encoder.pkl with {len(diseases)} diseases")

# Create synthetic training data
np.random.seed(42)
n_samples = 2000
n_features = len(symptom_names)

# Generate random symptom patterns
X = np.random.rand(n_samples, n_features)
# Binarize features (0 or 1) - more realistic for symptoms
X = (X > 0.7).astype(int)

# Generate random disease labels
y = np.random.randint(0, len(diseases), n_samples)

# Train a simple model
print("Training model...")
model = LogisticRegression(max_iter=2000, random_state=42, multi_class='ovr')
model.fit(X, y)
print("✓ Model training complete")

# Save the model
with open('models/disease_prediction_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("✓ Created disease_prediction_model.pkl")

print("\n" + "="*50)
print("✅ All model files recreated successfully!")
print(f"📊 Model accuracy score: {model.score(X, y):.2f}")
print("="*50)

# Test the model
print("\nTesting model with sample symptoms...")
test_symptoms = ['fever', 'cough', 'fatigue']
test_vector = np.zeros(len(symptom_names))
for symptom in test_symptoms:
    if symptom in symptom_names:
        idx = symptom_names.index(symptom)
        test_vector[idx] = 1

prediction = model.predict([test_vector])[0]
disease_name = label_encoder.inverse_transform([prediction])[0]
print(f"✓ Test prediction for {test_symptoms}: {disease_name}")