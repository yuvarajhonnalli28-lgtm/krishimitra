import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os

print("="*50)
print("🌿 Testing Plant Disease Detection Model")
print("="*50)

# Load model
model_path = '../backend/app/ml/models/plant_disease_model/model.h5'
labels_path = '../backend/app/ml/models/plant_disease_model/labels.json'

print(f"\n📂 Loading model from: {model_path}")
model = tf.keras.models.load_model(model_path)

print(f"📂 Loading labels from: {labels_path}")
with open(labels_path, 'r') as f:
    labels = json.load(f)

print(f"✅ Model loaded successfully!")
print(f"📊 Number of classes: {len(labels)}")

def predict_image(image_path):
    """Predict disease from an image file"""
    print(f"\n🔍 Analyzing: {image_path}")
    
    # Load and preprocess image
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    class_idx = np.argmax(predictions[0])
    confidence = predictions[0][class_idx]
    
    print(f"✅ Predicted: {labels[class_idx]}")
    print(f"📊 Confidence: {confidence:.2%}")
    
    # Show top 3 predictions
    print("\n📋 Top 3 predictions:")
    top3 = np.argsort(predictions[0])[-3:][::-1]
    for i, idx in enumerate(top3):
        print(f"   {i+1}. {labels[idx]}: {predictions[0][idx]:.2%}")
    
    return labels[class_idx], confidence

# If you have a test image, uncomment and modify this:
# test_image = "../dataset/plantdisease/Tomato_Bacterial_spot/sample.jpg"
# if os.path.exists(test_image):
#     predict_image(test_image)
# else:
#     print("\n⚠️  No test image found. Add a test image path to test.")

print("\n" + "="*50)
print("✅ Test script ready!")
print("="*50)
print("\nTo test with an image, add this line at the end:")
print('predict_image("path/to/your/test/image.jpg")')
