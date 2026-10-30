import tensorflow as tf
import numpy as np
from PIL import Image
import json

# Load model
model = tf.keras.models.load_model('../backend/app/ml/models/plant_disease_model/model.h5')

with open('../backend/app/ml/models/plant_disease_model/labels.json', 'r') as f:
    labels = json.load(f)

def predict_image(image_path):
    print(f"Analyzing: {image_path}")
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    predictions = model.predict(img_array, verbose=0)
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    
    print(f"Predicted: {labels[class_idx]}")
    print(f"Confidence: {confidence:.2%}")

# Test with first image
predict_image(r"D:\krishimitra-ai\dataset\plantdisease\Pepper__bell___Bacterial_spot\0022d6b7-d47c-4ee2-ae9a-392a53f48647___JR_B.Spot 8964.JPG")
