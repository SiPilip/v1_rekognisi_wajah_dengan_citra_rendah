import pickle
import numpy as np
from pathlib import Path
import config
from scipy.spatial.distance import cosine

def inspect_gallery():
    print("--- INSPEKSI ISI DATABASE GALERI ---")
    
    pkl_path = config.GALLERY_CACHE_PATH
    if not pkl_path.exists():
        print("File gallery_features.pkl tidak ditemukan!")
        return

    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
        features = data['features']

    print(f"Total wajah di database: {len(features)}")

    # Kita cari sampel dari subjek 'a' dan subjek 'd'
    a_samples = [item for item in features if item['subject_id'] == 'a']
    d_samples = [item for item in features if item['subject_id'] == 'd']

    if not a_samples or not d_samples:
        print("Data subjek 'a' atau 'd' tidak ditemukan di database.")
        return

    print(f"\nDitemukan {len(a_samples)} data untuk 'a'")
    print(f"Ditemukan {len(d_samples)} data untuk 'd'")

    # AMBIL SATU SAMPEL DARI MASING-MASING
    emb_a = a_samples[0]['embedding']
    emb_d = d_samples[0]['embedding']

    # CEK 1: APAKAH VEKTORNYA SAMA PERSIS?
    # Jika hasilnya True, berarti ada bug parah di loop pembuatan galeri
    is_identical = np.allclose(emb_a, emb_d)
    
    print(f"\n--- HASIL ANALISIS ---")
    print(f"Apakah Vektor Wajah 'a' dan 'd' IDENTIK? -> {is_identical}")
    
    if is_identical:
        print("KESIMPULAN: CRITICAL BUG! Data wajah 'd' adalah duplikat copy-paste dari 'a'.")
        print("Ini sebabnya hasilnya 100%. Masalah ada di loop 'pipeline.py'.")
    else:
        # Hitung jarak manual
        dist = cosine(emb_a, emb_d)
        print(f"Jarak Cosine Manual 'a' vs 'd': {dist}")
        print("Jika jarak < 0.1, berarti data tertukar/salah foto.")
        print("Jika jarak > 0.6, berarti kode prediksi di main.py yang salah hitung.")

if __name__ == "__main__":
    inspect_gallery()