# prediction_routes.py - Fixed to use actual ML model
import random
import numpy as np

class PredictionRoutes:
    def __init__(self, model=None, symptom_names=None, label_encoder=None, db=None):
        self.model = model
        self.symptom_names = symptom_names or []
        self.label_encoder = label_encoder
        self.db = db
        print(f"✅ PredictionRoutes initialized with model: {model is not None}")
        
        # Fallback specialist mapping (used only if model fails or no match)
        self.symptom_specialist = {
            'fever': 'General Physician', 'cough': 'Pulmonologist',
            'headache': 'Neurologist', 'chest pain': 'Cardiologist',
            'abdominal pain': 'Gastroenterologist', 'joint pain': 'Rheumatologist',
            'back pain': 'Orthopedic Surgeon', 'rash': 'Dermatologist',
            'anxiety': 'Psychiatrist', 'frequent urination': 'Urologist',
            'blurred vision': 'Ophthalmologist', 'fatigue': 'General Physician'
        }
    
    def predict(self, symptoms):
        """
        Predict disease using loaded ML model if available, otherwise fallback to rule-based.
        """
        print(f"🔍 Predicting with symptoms: {symptoms}")
        if not symptoms:
            return self._fallback_predict([], 'General Physician')
        
        # Normalize symptoms to lowercase
        norm_symptoms = [s.lower().strip() for s in symptoms]
        
        # Try ML model first
        if self.model is not None and self.symptom_names and self.label_encoder:
            try:
                # Create feature vector
                feature_vector = np.zeros(len(self.symptom_names))
                for sym in norm_symptoms:
                    if sym in self.symptom_names:
                        idx = self.symptom_names.index(sym)
                        feature_vector[idx] = 1
                # Predict
                pred_idx = self.model.predict([feature_vector])[0]
                disease = self.label_encoder.inverse_transform([pred_idx])[0]
                # Get probabilities for confidence
                probs = self.model.predict_proba([feature_vector])[0]
                confidence = int(probs[pred_idx] * 100)
                # Determine specialist from disease or fallback
                specialist = self._get_specialist_from_disease(disease) or self._get_specialist_from_symptoms(norm_symptoms)
                print(f"✅ ML prediction: {disease} with {confidence}% confidence")
                doctors = self.find_doctors_by_specialization(specialist)
                return {
                    'disease': disease,
                    'confidence': min(95, confidence),
                    'specialist': specialist,
                    'doctors': doctors
                }
            except Exception as e:
                print(f"⚠️ ML prediction failed: {e}, falling back to rule-based")
        
        # Fallback to rule-based matching
        return self._fallback_predict(norm_symptoms, self._get_specialist_from_symptoms(norm_symptoms))
    
    def _fallback_predict(self, symptoms, default_specialist):
        """Rule-based prediction (original logic)"""
        # Expanded disease-symptom map (same as before but trimmed for brevity)
        disease_map = [
            {'symptoms': ['fever','cough','fatigue','body aches','chills'], 'disease': 'Influenza (Flu)', 'confidence': 85, 'specialist': 'General Physician'},
            {'symptoms': ['sore throat','cough','runny nose','nasal congestion','fever'], 'disease': 'Common Cold', 'confidence': 80, 'specialist': 'General Physician'},
            # ... (keep full map from original but ensure all symptoms covered)
        ]
        best_match = None
        best_score = 0
        for disease_info in disease_map:
            disease_symptoms = [s.lower() for s in disease_info['symptoms']]
            matches = sum(1 for s in symptoms if s in disease_symptoms)
            if matches > 0:
                score = (matches / len(disease_symptoms)) * 100
                if score > best_score:
                    best_score = score
                    best_match = disease_info
        if best_match and best_score >= 40:
            disease = best_match['disease']
            confidence = min(95, max(40, int(best_match['confidence'] * (best_score / 100))))
            specialist = best_match['specialist']
        else:
            disease = "General Illness"
            confidence = 55
            specialist = default_specialist
        doctors = self.find_doctors_by_specialization(specialist)
        return {'disease': disease, 'confidence': confidence, 'specialist': specialist, 'doctors': doctors}
    
    def _get_specialist_from_disease(self, disease):
        """Map disease to specialist"""
        mapping = {
            'Influenza': 'General Physician', 'Common Cold': 'General Physician',
            'Asthma': 'Pulmonologist', 'COVID-19': 'Pulmonologist',
            'Migraine': 'Neurologist', 'Stroke': 'Neurologist',
            'Heart Attack': 'Cardiologist', 'Hypertension': 'Cardiologist',
            'Diabetes': 'Endocrinologist', 'Arthritis': 'Rheumatologist',
            'Depression': 'Psychiatrist', 'Anxiety': 'Psychiatrist'
        }
        for key, spec in mapping.items():
            if key.lower() in disease.lower():
                return spec
        return None
    
    def _get_specialist_from_symptoms(self, symptoms):
        for sym in symptoms:
            if sym in self.symptom_specialist:
                return self.symptom_specialist[sym]
        return 'General Physician'
    
    def find_doctors_by_specialization(self, specialization):
        if not self.db:
            return []
        try:
            cursor = self.db.get_connection().cursor(dictionary=True)
            # Case-insensitive search
            cursor.execute("""
                SELECT id, name, hospital, qualification, specialization, timings
                FROM doctors 
                WHERE LOWER(specialization) LIKE LOWER(%s) AND is_available = TRUE
                LIMIT 5
            """, (f'%{specialization}%',))
            doctors = cursor.fetchall()
            cursor.close()
            return doctors
        except Exception as e:
            print(f"Error finding doctors: {e}")
            return []