from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import shutil
import zipfile
from ocr_ner import process_invoice  # Elindeki OCR ve NER kodunu import edeceğiz
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik originler kullanın
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dosyaları kaydetmek için klasör oluşturuyoruz
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Kullanıcıdan birden fazla dosya alacak endpoint
@app.post("/uploadfiles/")
async def upload_files(files: list[UploadFile] = File(...)):
    file_paths = []
    output_file_paths = []

    # Dosyaları kaydet
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_path)

    # OCR ve NER işlemi
    for file_path in file_paths:
        processed_text, entities = process_invoice(file_path)

        output_file_path = os.path.join(OUTPUT_FOLDER, os.path.basename(file_path) + "_output.txt")
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write("=== Extracted Text ===\n")
            f.write(processed_text + "\n\n")
            f.write("--- spaCy Entities ---\n")
            for entity, label in entities:
                f.write(f"{entity} - {label}\n")

        output_file_paths.append(output_file_path)

    # Zip dosyasını oluştur
    zip_filename = "output_files.zip"
    zip_filepath = os.path.join(OUTPUT_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for file_path in output_file_paths:
            zipf.write(file_path, os.path.basename(file_path))
    
    # Yanıtı logla
    print(f"Zip dosyası oluşturuldu: {zip_filepath}")

    for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)

    

    # Dosyayı kullanıcıya döndür
    return FileResponse(zip_filepath, media_type='application/zip', filename=zip_filename)








