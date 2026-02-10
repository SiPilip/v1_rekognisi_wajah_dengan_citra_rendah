import pickle
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
import config # Pastikan config.py ada di folder yang sama

def train_models():
    print("--- Memulai Retraining Model (Spesifikasi Skripsi v6.4.3) ---")
    
    # 1. Muat data fitur dari cache galeri
    gallery_path = config.GALLERY_CACHE_PATH
    if not gallery_path.exists():
        print(f"Error: File {gallery_path} tidak ditemukan.")
        print("Jalankan server (main.py) setidaknya satu kali untuk membangun galeri.")
        return

    print(f"Memuat data galeri dari: {gallery_path}")
    with open(gallery_path, 'rb') as f:
        data = pickle.load(f)
        features = data['features']

    if not features:
        print("Data galeri kosong. Mohon isi folder 'gallery' dengan foto wajah.")
        return

    # 2. Persiapkan X (Embedding) dan y (Label)
    X = []
    y = []
    
    print(f"Ditemukan {len(features)} sampel data wajah.")
    
    for item in features:
        X.append(item['embedding'])
        y.append(item['subject_id'])

    X = np.array(X)
    
    # 3. Encode Label
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    print(f"Kelas terdeteksi: {le.classes_}")

    # --- KONFIGURASI SESUAI SKRIPSI ---
    
    # 4. Latih KNN
    # Spesifikasi: n_neighbors=1, weights='distance', metric='euclidean'
    print("Melatih KNN (n_neighbors=1, metric='euclidean')...")
    knn_model = KNeighborsClassifier(n_neighbors=1, weights='distance', metric='euclidean')
    knn_model.fit(X, y_encoded)

    # 5. Latih SVM
    # Spesifikasi: kernel='linear', probability=True, C=1000.0
    print("Melatih SVM (kernel='linear', C=1000.0)...")
    svm_model = SVC(kernel='linear', probability=True, C=1000.0)
    svm_model.fit(X, y_encoded)

    # ----------------------------------

    # 6. Simpan Model Baru
    print("Menyimpan model ke folder models/...")
    config.MODELS_DIR.mkdir(exist_ok=True)

    with open(config.MODELS_DIR / 'knn_model.pkl', 'wb') as f:
        pickle.dump(knn_model, f)
    
    with open(config.MODELS_DIR / 'svm_model.pkl', 'wb') as f:
        pickle.dump(svm_model, f)
        
    with open(config.MODELS_DIR / 'label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)

    print("--- Retraining Selesai! ---")
    print("Model sekarang menggunakan parameter sesuai Skripsi.")
    print("Silakan restart server main.py Anda.")

if __name__ == "__main__":
    train_models()