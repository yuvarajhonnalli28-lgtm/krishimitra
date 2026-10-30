# download_dataset_mendeley.py
import requests
import zipfile
import os
from tqdm import tqdm

print("="*60)
print("🌿 Downloading Complete PlantVillage Dataset from Mendeley")
print("="*60)

# Mendeley URL for the complete PlantVillage dataset (official source)
url = "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/33f8f6c9-4dc9-4378-a964-ea5a2d074a42/file_downloaded"

print("\n📥 Downloading dataset (815 MB)...")
print("This may take 5-15 minutes depending on your internet speed.\n")

# Download with progress bar
response = requests.get(url, stream=True)
total_size = int(response.headers.get('content-length', 0))

with open('plantvillage.zip', 'wb') as file:
    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            pbar.update(len(data))

print("\n📦 Extracting files...")

# Create target directory
os.makedirs('dataset/plantdisease', exist_ok=True)

# Extract the zip file
with zipfile.ZipFile('plantvillage.zip', 'r') as zip_ref:
    zip_ref.extractall('dataset/plantdisease/')

# Count the folders
num_folders = len([f for f in os.listdir('dataset/plantdisease') 
                   if os.path.isdir(os.path.join('dataset/plantdisease', f))])

print(f"\n✅ Extraction complete! Found {num_folders} class folders.")

# Clean up
os.remove('plantvillage.zip')
print("🧹 Cleaned up temporary zip file.")

print("\n" + "="*60)
print("🎯 DATASET READY FOR TRAINING!")
print("="*60)
print(f"\n📍 Location: D:\\krishimitra-ai\\dataset\\plantdisease\\")
print(f"📊 Total classes: {num_folders} (should be 38)")
print("\n🚀 Next step: Run your training script")
print("cd notebooks")
print("python train_model.py")