from pathlib import Path

# Path dasar untuk direktori backend, semua path lain akan mengacu ke sini
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Path Konfigurasi Aplikasi ---

# Path ke direktori yang berisi model-model terlatih (.pkl)
MODELS_DIR = BASE_DIR / "models"

# [BARU] Path ke direktori model khusus EVALUASI
MODELS_EVAL_DIR = BASE_DIR / "models_evaluation"

# Path ke direktori galeri wajah
GALLERY_DIR = BASE_DIR / "gallery"

# Path untuk menyimpan file yang diunggah pengguna sementara
UPLOADS_DIR = BASE_DIR / "uploads"

# Path ke file bobot model GFPGAN v1.4
# PENTING: Ini adalah path absolut dari sistem Anda.
# Pastikan file 'GFPGANv1.4.pth' ada di lokasi ini.
GFPGAN_WEIGHTS_PATH = BASE_DIR / 'gfpgan' / 'weights' / 'GFPGANv1.4.pth'
GALLERY_CACHE_PATH = MODELS_DIR / 'gallery_features.pkl'

# --- Model Machine Learning ---
DEEPFACE_MODEL_NAME = "ArcFace"
