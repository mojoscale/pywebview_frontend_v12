import requests

# URL you want to POST to
url = "http://10.0.0.118/upload_model"  # replace with your target URL

# File in the same folder
file_path = "pedestrian_detector.espdl"  # replace with your actual filename

with open(file_path, "rb") as f:
    files = {"file": (file_path, f)}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response:", response.text)
