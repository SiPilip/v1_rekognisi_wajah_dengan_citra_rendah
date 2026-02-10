from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # Impor CORS Middleware
import shutil
from pathlib import Path
import uuid

# Impor dari modul lokal kita
from . import config
from .pipeline import FaceRecognitionPipeline

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="VisioRecog API",
    description="API untuk pipeline rekognisi dan restorasi wajah.",
    version="1.0.0"
)

# --- Konfigurasi CORS ---
# Ini adalah bagian penting yang mengizinkan frontend untuk berkomunikasi dengan backend.
origins = [
    "http://localhost:5173", # Alamat default server pengembangan Vite
    "http://localhost:3000", # Alamat umum server pengembangan React
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Mengizinkan semua metode (GET, POST, dll)
    allow_headers=["*"], # Mengizinkan semua header
)

# --- Mount Direktori Static ---
config.UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=config.UPLOADS_DIR), name="uploads")
app.mount("/gallery", StaticFiles(directory=config.GALLERY_DIR), name="gallery")

# --- Inisialisasi Pipeline ---
try:
    pipeline = FaceRecognitionPipeline()
except Exception as e:
    print(f"FATAL: Gagal menginisialisasi pipeline: {e}")
    pipeline = None

# --- API Endpoints ---

@app.on_event("startup")
async def startup_event():
    if pipeline is None:
        raise RuntimeError("Aplikasi tidak dapat dimulai karena pipeline gagal dimuat. Periksa error di atas.")
    print("Aplikasi FastAPI berhasil dimulai. Kunjungi /docs untuk dokumentasi.")

@app.post("/recognize")
async def recognize_face(
    image: UploadFile = File(..., description="File gambar wajah yang sudah di-crop")
):
    temp_filename = f"{uuid.uuid4()}{Path(image.filename).suffix}"
    temp_path = config.UPLOADS_DIR / temp_filename
    
    try:
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file: {e}")
    finally:
        image.file.close()

    print(f"Memproses file: {temp_path}")
    results = pipeline.run_pipeline(temp_path)

    results['original_image_url'] = f"/uploads/{temp_filename}"

    return JSONResponse(content=results)

@app.post("/evaluate")
async def evaluate_dataset(
    json_file: UploadFile = File(..., description="File JSON hasil pemrosesan dataset")
):
    """
    Menerima file JSON yang berisi embedding dan ground truth,
    kemudian menjalankan evaluasi performa model secara menyeluruh.
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline tidak tersedia.")

    try:
        content = await json_file.read()
        evaluation_results = pipeline.run_evaluation(content)
        return JSONResponse(content=evaluation_results)
    except Exception as e:
        # Memberikan error yang lebih spesifik jika terjadi masalah
        print(f"Error saat evaluasi: {e}")
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat memproses file evaluasi: {e}")
    finally:
        await json_file.close()

@app.get("/embedding-plot")
async def get_embedding_plot_data():
    """Endpoint untuk mendapatkan data plot t-SNE dari galeri."""
    if pipeline and pipeline.tsne_results:
        return JSONResponse(content=pipeline.tsne_results)
    raise HTTPException(status_code=500, detail="Data plot tidak tersedia.")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Selamat datang di VisioRecog API. Kunjungi /docs untuk dokumentasi."}
