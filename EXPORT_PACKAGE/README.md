# Crop Predictor - Portable Package

## Quick Setup

1. Copy the `crop_predictor` folder to your new project
2. Install dependencies: `pip install numpy scikit-learn joblib`

## Usage

### Basic Usage
```python
from crop_predictor import CropPredictor

predictor = CropPredictor()

result = predictor.predict(
    nitrogen=90,
    phosphorus=42,
    potassium=43,
    temperature=25.5,
    humidity=80,
    ph=6.5,
    rainfall=200
)

print(result)
# Output:
# {
#   "predictions": [
#     {"crop": "Rice", "confidence": 0.89},
#     {"crop": "Wheat", "confidence": 0.76},
#     {"crop": "Maize", "confidence": 0.68}
#   ],
#   "feature_importance": [...]
# }
```

### Django Integration
```python
# views.py
from crop_predictor import CropPredictor

predictor = CropPredictor()

def predict_view(request):
    data = json.loads(request.body)
    result = predictor.predict(
        nitrogen=data['nitrogen'],
        phosphorus=data['phosphorus'],
        potassium=data['potassium'],
        temperature=data['temperature'],
        humidity=data['humidity'],
        ph=data['ph'],
        rainfall=data['rainfall']
    )
    return JsonResponse(result)
```

### Flask Integration
```python
from flask import Flask, request, jsonify
from crop_predictor import CropPredictor

app = Flask(__name__)
predictor = CropPredictor()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    result = predictor.predict(**data)
    return jsonify(result)
```

### FastAPI Integration
```python
from fastapi import FastAPI
from crop_predictor import CropPredictor

app = FastAPI()
predictor = CropPredictor()

@app.post("/predict")
def predict(nitrogen: float, phosphorus: float, potassium: float, 
            temperature: float, humidity: float, ph: float, rainfall: float):
    return predictor.predict(nitrogen, phosphorus, potassium, 
                            temperature, humidity, ph, rainfall)
```

## Custom Model Path
```python
predictor = CropPredictor(model_path="/path/to/your/model.pkl")
```
