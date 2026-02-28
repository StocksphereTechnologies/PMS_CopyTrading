import requests
import time
import os

url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
file_path = "5paisa_scrip_master.csv"

print(f"Starting standalone download from {url}...")
try:
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        print("Connected. Downloading...")
        total_size = 0
        with open(file_path + ".tmp", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                total_size += len(chunk)
                if total_size % (5*1024*1024) == 0:
                     print(f"Downloaded {total_size / (1024*1024):.2f} MB")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(file_path + ".tmp", file_path)
        print(f"Download complete. Saved to {file_path}. Size: {total_size} bytes")
except Exception as e:
    print(f"Download failed: {e}")
