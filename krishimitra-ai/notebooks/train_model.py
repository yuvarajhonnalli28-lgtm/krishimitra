"""
Plant Disease Detection Training Script
Run this script to train the model directly without Jupyter
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import os
import json
import sys

print("="*60)
print("🌿 KrishiMitra AI - Disease Detection Training")
print("="*60)

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 5  # Reduced for quick testing
DATASET_PATH = "../dataset/plantdisease"
MODEL_SAVE_PATH = "../backend/app/ml/models/plant_disease_model"

# Create directories
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
os.makedirs(DATASET_PATH, exist_ok=True)

print(f"\n📁 Dataset path: {DATASET_PATH}")
print(f"📁 Model save path: {MODEL_SAVE_PATH}")

# Check if dataset exists
if not os.path.exists(DATASET_PATH) or len(os.listdir(DATASET_PATH)) == 0:
    print("\n❌ Dataset not found!")
    print("\nPlease download the PlantVillage dataset:")
    print("1. Go to: https://www.kaggle.com/datasets/emmarex/plantdisease")
    print("2. Download and extract to: ../dataset/plantdisease/")
    sys.exit(1)

print("\n✅ Dataset found!")

# Data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

# Load data
train_generator = train_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

validation_generator = val_datagen.flow_from_directory(
    DATASET_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Get class information
class_names = list(train_generator.class_indices.keys())
num_classes = len(class_names)

print(f"\n🎯 Number of classes: {num_classes}")
print(f"🎯 Training samples: {train_generator.samples}")
print(f"🎯 Validation samples: {validation_generator.samples}")

# Build model
print("\n🏗️ Building model...")
base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print("\n✅ Model built!")

# Train
print("\n🚀 Starting training...")
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // BATCH_SIZE,
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // BATCH_SIZE,
    verbose=1
)

# Evaluate
val_loss, val_accuracy = model.evaluate(validation_generator)
print(f"\n✅ Validation Accuracy: {val_accuracy:.4f}")

# Save model
print("\n💾 Saving model...")
model.save(os.path.join(MODEL_SAVE_PATH, 'model.h5'))
print(f"✅ Model saved")

# Save labels
with open(os.path.join(MODEL_SAVE_PATH, 'labels.json'), 'w') as f:
    json.dump(class_names, f)
print(f"✅ Labels saved")

print("\n" + "="*60)
print("🎯 MODEL TRAINING COMPLETE")
print("="*60)
