import os
import shutil

def save_uploaded_file(uploaded_file, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    return file_path

def detect_file_type(file_path):
    ext = file_path.split(".")[-1].lower()
    if ext in ["pdf", "xml", "csv", "xls", "xlsx"]:
        return ext
    return None

