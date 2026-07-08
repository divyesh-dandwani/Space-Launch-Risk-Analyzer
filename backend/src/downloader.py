import os
import sys
import shutil
import kagglehub

# Ensure sibling src/ modules are in the Python search path regardless of startup cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import RAW_DATA_PATH, DATA_DIR

def download_dataset():
    print("Downloading space missions dataset using kagglehub...")
    try:
        # Download latest version of the dataset
        downloaded_path = kagglehub.dataset_download("agirlcoding/all-space-missions-from-1957")
        print("Path to dataset files:", downloaded_path)
        
        # Find the Space_Corrected.csv in the downloaded directory
        src_file = os.path.join(downloaded_path, "Space_Corrected.csv")
        if not os.path.exists(src_file):
            files = os.listdir(downloaded_path)
            print(f"Downloaded files list: {files}")
            csv_files = [f for f in files if f.endswith(".csv")]
            if csv_files:
                src_file = os.path.join(downloaded_path, csv_files[0])
            else:
                raise FileNotFoundError("Could not find any CSV file in the downloaded kagglehub folder.")
        
        # Copy to local backend data directory
        os.makedirs(DATA_DIR, exist_ok=True)
        shutil.copy(src_file, RAW_DATA_PATH)
        print(f"Successfully copied dataset to: {RAW_DATA_PATH}")
        print(f"File size: {os.path.getsize(RAW_DATA_PATH)} bytes")
    except Exception as e:
        print(f"Error downloading dataset via kagglehub: {e}")
        raise e

if __name__ == "__main__":
    download_dataset()
