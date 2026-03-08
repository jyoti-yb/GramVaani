import joblib
import numpy as np
import os

class CropPredictor:
    def __init__(self, model_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model = joblib.load(model_path or os.path.join(base_dir, "crop_model.pkl"))
        self.features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        
    def predict(self, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall):
        input_array = np.array([[nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]])
        probabilities = self.model.predict_proba(input_array)[0]
        classes = self.model.classes_
        
        top_3_idx = np.argsort(probabilities)[-3:][::-1]
        predictions = [{"crop": classes[i], "confidence": float(probabilities[i])} for i in top_3_idx]
        
        importances = self.model.feature_importances_
        feature_importance = [{"feature": f, "importance": float(importances[i])} for i, f in enumerate(["Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "pH", "Rainfall"])]
        
        return {"predictions": predictions, "feature_importance": feature_importance}
