import cv2
import numpy as np

def convert_to_native_python_types(obj):
    """Rekursif mengubah tipe data NumPy menjadi tipe data asli Python."""
    if isinstance(obj, dict):
        return {k: convert_to_native_python_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_to_native_python_types(i) for i in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

import torch
import pickle
from pathlib import Path
import os
import glob
import uuid
from scipy.spatial.distance import cosine
from typing import Union
from sklearn.manifold import TSNE

# Impor dari modul lokal kita
from . import config

# Coba impor pustaka pihak ketiga dan berikan pesan error jika gagal
try:
    from gfpgan import GFPGANer
    import pyiqa
    from deepface import DeepFace
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.svm import SVC
    from sklearn.preprocessing import LabelEncoder
except ImportError as e:
    print(f"Error: Salah satu pustaka yang dibutuhkan tidak terinstal. {e}")
    print("Silakan jalankan 'pip install -r requirements.txt' di terminal Anda.")
    raise

import json
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

import hashlib

class FaceRecognitionPipeline:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Pipeline diinisialisasi pada device: {self.device}")

        self.gfpgan_restorer = self._load_gfpgan()
        self.brisque_assessor = pyiqa.create_metric('brisque', device=self.device)
        self.niqe_assessor = pyiqa.create_metric('niqe', device=self.device)
        self.knn_model, self.svm_model, self.label_encoder = self._load_classifiers(source_dir=config.MODELS_DIR)
        
        self.gallery_features = self._load_or_build_gallery_features()
        self.tsne_results = self._calculate_tsne() # Hitung t-SNE saat startup

        print("Melakukan pemanasan model DeepFace...")
        # Pastikan model di-load dengan benar saat startup
        DeepFace.represent(np.zeros((112, 112, 3), dtype=np.uint8), model_name=config.DEEPFACE_MODEL_NAME, enforce_detection=False)
        print("Pipeline siap digunakan.")

    def _generate_gallery_hash(self) -> str:
        """Menghasilkan hash unik berdasarkan file dan waktu modifikasi di galeri."""
        gallery_files = sorted(glob.glob(os.path.join(config.GALLERY_DIR, '*.jpg')) + glob.glob(os.path.join(config.GALLERY_DIR, '*.png')))
        manifest = []
        for file_path in gallery_files:
            mod_time = os.path.getmtime(file_path)
            manifest.append(f"{file_path}|{mod_time}")
        
        return hashlib.sha256("".join(manifest).encode()).hexdigest()

    def _get_embedding_from_cropped(self, image_array: np.ndarray) -> Union[list, None]:
        """Mendapatkan embedding langsung dari gambar yang diasumsikan sudah di-crop."""
        try:
            embedding_objs = DeepFace.represent(
                img_path=image_array,
                model_name=config.DEEPFACE_MODEL_NAME,
                enforce_detection=False
            )
            return embedding_objs[0]['embedding']
        except Exception as e:
            # Ini bisa terjadi jika gambar galeri bukan wajah, jadi ini bukan error fatal
            # print(f"Gagal mendapatkan embedding dari gambar yang di-crop: {e}")
            return None

    def _load_or_build_gallery_features(self) -> list:
        """Memuat fitur galeri dari cache jika valid, atau membangunnya kembali."""
        current_hash = self._generate_gallery_hash()
        
        try:
            with open(config.GALLERY_CACHE_PATH, 'rb') as f:
                cached_data = pickle.load(f)
            
            if cached_data.get('hash') == current_hash:
                print("Memuat fitur galeri dari cache...")
                return cached_data['features']
            else:
                print("Cache galeri tidak valid.")
        except (FileNotFoundError, EOFError, KeyError):
            print("Cache galeri tidak ditemukan atau rusak.")

        # Jika cache tidak ada, tidak valid, atau rusak, bangun kembali
        print("Membangun ulang fitur galeri...")
        features = self._generate_gallery_features()
        
        # Simpan fitur baru beserta hash-nya ke cache
        with open(config.GALLERY_CACHE_PATH, 'wb') as f:
            pickle.dump({'hash': current_hash, 'features': features}, f)
            print(f"Cache galeri berhasil disimpan di {config.GALLERY_CACHE_PATH}")
            
        return features

    def _generate_gallery_features(self) -> list:
        print("Membangun ulang fitur galeri (Versi Anti-Leak)...")
        features = []
        # Ambil semua file gambar
        gallery_files = glob.glob(os.path.join(config.GALLERY_DIR, '*.jpg')) + \
                        glob.glob(os.path.join(config.GALLERY_DIR, '*.png'))
        
        # PENTING: Sortir agar urutan proses konsisten
        gallery_files.sort() 

        for file_path in gallery_files:
            subject_id = Path(file_path).stem.split('_')[0]
            
            # --- [FIX CRITICAL] RESET VARIABEL ---
            # Kita kosongkan variabel ini sebelum memproses file baru.
            # Jadi kalau deteksi gagal, dia tidak akan pakai data sisa file sebelumnya.
            embedding = None 
            img = None
            # -------------------------------------

            try:
                img = cv2.imdecode(np.fromfile(file_path, np.uint8), cv2.IMREAD_COLOR)
                
                if img is None:
                    print(f"SKIP (Corrupt): Gagal membaca file gambar {file_path}")
                    continue

                # Coba ekstrak wajah
                # Pastikan fungsi ini mengembalikan None jika wajah tidak ketemu, bukan error.
                embedding, _ = self.get_embedding_and_landmarks(img)
                
                # LOGIKA PENYIMPANAN YANG KETAT
                # Hanya simpan jika embedding berhasil diisi BARU (bukan None, bukan kosong)
                if embedding is not None and len(embedding) > 0:
                    features.append({
                        'subject_id': subject_id, 
                        'embedding': embedding, 
                        'image_path': file_path
                    })
                    # Optional: Print progress biar kelihatan nyangkut di mana
                    # print(f"OK: {file_path} -> {subject_id}")
                else:
                    print(f"WARNING: Wajah tidak terdeteksi di {file_path}. File ini di-SKIP.")

            except Exception as e:
                print(f"ERROR pada file {file_path}: {e}")
                # Lanjut ke file berikutnya, variable embedding sudah None jadi aman.
                continue 

        print(f"Selesai. Total {len(features)} wajah valid berhasil disimpan.")
        return features
        
    def _get_cosine_prediction(self, embedding: list) -> str:
        """Mencari satu prediksi terbaik berdasarkan Cosine Similarity."""
        if not self.gallery_features:
            return "N/A"
        
        distances = [{'subject_id': item['subject_id'], 'distance': cosine(embedding, item['embedding'])} for item in self.gallery_features]
        # Cari item dengan distance terkecil
        best_match = min(distances, key=lambda x: x['distance'])
        return best_match['subject_id']

    def _calculate_metrics(self, y_true, y_pred, labels):
        """Menghitung metrik evaluasi dari list ground truth dan prediksi."""
        if not y_true or not y_pred:
            return {
                "accuracy": 0, "precision": 0, "recall": 0, "f1_score": 0,
                "confusion_matrix": [], "report": {}
            }

        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', labels=labels, zero_division=0)
        
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        }

    def run_evaluation(self, json_content: bytes) -> dict:
        """Menjalankan pipeline evaluasi menggunakan model dari folder models_evaluation."""
        
        # 1. MUAT MODEL KHUSUS EVALUASI
        print("--- Memulai Evaluasi dengan Model Terpisah ---")
        eval_knn, eval_svm, eval_le = self._load_classifiers(source_dir=config.MODELS_EVAL_DIR)

        if eval_knn is None or eval_svm is None:
            return {"error": "Model evaluasi tidak ditemukan di folder models_evaluation. Haraplatih model evaluasi terlebih dahulu."}

        try:
            data = json.loads(json_content)
        except json.JSONDecodeError:
            return {"error": "Gagal mem-parsing file JSON."}

        # Inisialisasi penyimpanan untuk hasil
        ground_truths = {'original': [], 'restored': []}
        predictions = {
            'original_knn': [], 'original_svm': [], 'original_cosine': [],
            'restored_knn': [], 'restored_svm': [], 'restored_cosine': []
        }
        iqa_scores = {'brisque_original': [], 'niqe_original': [], 'brisque_restored': [], 'niqe_restored': []}
        restoration_count = 0

        # Iterasi melalui setiap item data
        for item in data:
            gt = item.get("ground_truth")
            if not gt: continue

            # --- Proses Data Original ---
            emb_orig = item.get("embedding_original")
            if emb_orig:
                ground_truths['original'].append(gt)
                
                # PENTING: Gunakan eval_knn, eval_svm, dan eval_le (Bukan self.knn_model)
                predictions['original_knn'].append(eval_le.inverse_transform(eval_knn.predict([emb_orig]))[0])
                predictions['original_svm'].append(eval_le.inverse_transform(eval_svm.predict([emb_orig]))[0])
                
                # Cosine tetap menggunakan galeri utama (atau logic lain jika galeri juga dipisah)
                # Asumsi saat ini: Evaluasi tetap membandingkan dengan Galeri Utama
                predictions['original_cosine'].append(self._get_cosine_prediction(emb_orig))
                
                if item.get("brisque_original") is not None: iqa_scores['brisque_original'].append(item["brisque_original"])
                if item.get("niqe_original") is not None: iqa_scores['niqe_original'].append(item["niqe_original"])

            # --- Proses Data Restored ---
            if item.get("restoration_succeeded") and item.get("embedding_restored"):
                restoration_count += 1
                emb_rest = item["embedding_restored"]
                
                ground_truths['restored'].append(gt)
                
                # PENTING: Gunakan eval_knn, eval_svm, dan eval_le
                predictions['restored_knn'].append(eval_le.inverse_transform(eval_knn.predict([emb_rest]))[0])
                predictions['restored_svm'].append(eval_le.inverse_transform(eval_svm.predict([emb_rest]))[0])
                predictions['restored_cosine'].append(self._get_cosine_prediction(emb_rest))

                if item.get("brisque_restored") is not None: iqa_scores['brisque_restored'].append(item["brisque_restored"])
                if item.get("niqe_restored") is not None: iqa_scores['niqe_restored'].append(item["niqe_restored"])

        # Dapatkan semua label unik untuk confusion matrix dari Label Encoder Evaluasi
        all_labels = list(eval_le.classes_)

        # Hitung semua metrik
        results = {
            "without_restoration": {
                "knn": self._calculate_metrics(ground_truths['original'], predictions['original_knn'], all_labels),
                "svm": self._calculate_metrics(ground_truths['original'], predictions['original_svm'], all_labels),
                "cosine": self._calculate_metrics(ground_truths['original'], predictions['original_cosine'], all_labels),
            },
            "with_restoration": {
                "knn": self._calculate_metrics(ground_truths['restored'], predictions['restored_knn'], all_labels),
                "svm": self._calculate_metrics(ground_truths['restored'], predictions['restored_svm'], all_labels),
                "cosine": self._calculate_metrics(ground_truths['restored'], predictions['restored_cosine'], all_labels),
            }
        }

        # Siapkan laporan akhir
        total_items = len(data)
        final_report = {
            "summary": {
                "total_items": total_items,
                "restoration_success_count": restoration_count,
                "restoration_success_rate": (restoration_count / total_items) if total_items > 0 else 0,
                "model_source": str(config.MODELS_EVAL_DIR) # Info tambahan
            },
            "iqa_comparison": {
                "original": {
                    "avg_brisque": np.mean(iqa_scores['brisque_original']) if iqa_scores['brisque_original'] else 0,
                    "avg_niqe": np.mean(iqa_scores['niqe_original']) if iqa_scores['niqe_original'] else 0,
                },
                "restored": {
                    "avg_brisque": np.mean(iqa_scores['brisque_restored']) if iqa_scores['brisque_restored'] else 0,
                    "avg_niqe": np.mean(iqa_scores['niqe_restored']) if iqa_scores['niqe_restored'] else 0,
                }
            },
            "evaluation_results": results,
            "class_labels": all_labels
        }

        return convert_to_native_python_types(final_report)
        
    def _calculate_tsne(self):
        print("Menghitung proyeksi t-SNE untuk galeri...")
        if not self.gallery_features:
            return {"labels": [], "x": [], "y": []}

        embeddings = np.array([item['embedding'] for item in self.gallery_features])
        labels = [item['subject_id'] for item in self.gallery_features]

        # Pastikan perplexity lebih kecil dari jumlah sampel
        perplexity_value = min(30, len(embeddings) - 1)
        if perplexity_value <= 0:
            print("Tidak cukup data untuk menghitung t-SNE.")
            return {"labels": [], "x": [], "y": []}

        tsne = TSNE(n_components=2, perplexity=perplexity_value, random_state=42, n_iter=300)
        tsne_projections = tsne.fit_transform(embeddings)

        return {
            "labels": labels,
            "x": tsne_projections[:, 0].tolist(),
            "y": tsne_projections[:, 1].tolist()
        }

    def _transform_probe_embedding(self, probe_embedding):
        if not self.gallery_features:
            return None, None

        # Gabungkan embedding galeri dan probe
        gallery_embeddings = np.array([item['embedding'] for item in self.gallery_features])
        all_embeddings = np.vstack([gallery_embeddings, probe_embedding])
        
        perplexity_value = min(30, len(all_embeddings) - 1)
        if perplexity_value <= 0: return None, None

        tsne = TSNE(n_components=2, perplexity=perplexity_value, random_state=42, n_iter=300)
        projections = tsne.fit_transform(all_embeddings)
        # Koordinat probe adalah yang terakhir
        probe_coords = projections[-1]
        return probe_coords[0].tolist(), probe_coords[1].tolist()

    def _load_gfpgan(self) -> GFPGANer:
        print("Memuat model GFPGAN...")
        if not config.GFPGAN_WEIGHTS_PATH.is_file():
            raise FileNotFoundError(f"File bobot GFPGAN tidak ditemukan di: {config.GFPGAN_WEIGHTS_PATH}")
        # Konversi Path object ke string, karena GFPGANer mengharapkan string
        return GFPGANer(model_path=str(config.GFPGAN_WEIGHTS_PATH), upscale=2, arch='clean', channel_multiplier=2, bg_upsampler=None, device=self.device)

    def _load_classifiers(self, source_dir=config.MODELS_DIR) -> tuple:
        """
        Memuat model KNN, SVM, dan LabelEncoder.
        Parameter source_dir menentukan folder asal (models atau models_evaluation).
        """
        print(f"Memuat classifiers dari: {source_dir}...")
        try:
            # Perhatikan: Kita menggunakan source_dir, bukan config.MODELS_DIR langsung
            with open(source_dir / 'knn_model.pkl', 'rb') as f: knn = pickle.load(f)
            with open(source_dir / 'svm_model.pkl', 'rb') as f: svm = pickle.load(f)
            with open(source_dir / 'label_encoder.pkl', 'rb') as f: le = pickle.load(f)
            print("Classifiers berhasil dimuat.")
            return knn, svm, le
        except (FileNotFoundError, OSError):
            print(f"PERINGATAN: File model belum ditemukan di {source_dir}.")
            return None, None, None

    def _build_gallery_features(self) -> list:
        print("Membangun fitur galeri untuk pencarian Cosine Similarity...")
        features = []
        gallery_files = glob.glob(os.path.join(config.GALLERY_DIR, '*.jpg')) + glob.glob(os.path.join(config.GALLERY_DIR, '*.png'))
        for file_path in gallery_files:
            subject_id = Path(file_path).stem.split('_')[0]
            img = cv2.imdecode(np.fromfile(file_path, np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                embedding, _ = self.get_embedding_and_landmarks(img)
                if embedding:
                    features.append({'subject_id': subject_id, 'embedding': embedding, 'image_path': file_path})
        print(f"Fitur galeri berhasil dibuat. Ditemukan {len(features)} gambar.")
        return features

    def get_embedding_and_landmarks(self, image_array: np.ndarray) -> (Union[list, None], Union[dict, None]):
        try:
            # Simpan ukuran gambar original untuk referensi landmarks
            original_height, original_width = image_array.shape[:2]
            
            # Step 1: Ekstrak wajah dan landmarks menggunakan retinaface
            # Fungsi ini TIDAK menerima model_name, tugasnya hanya deteksi.
            face_objs = DeepFace.extract_faces(
                img_path=image_array,
                detector_backend='retinaface',
                enforce_detection=False,
                align=True # Align penting untuk embedding yang konsisten
            )
            
            if not face_objs:
                return None, None

            face_obj = face_objs[0]
            
            # Ambil data facial area (termasuk landmarks)
            facial_area = face_obj['facial_area']
            
            # PENTING: Tambahkan ukuran gambar yang digunakan untuk koordinat landmarks
            # Koordinat landmarks dari retinaface mengacu pada ukuran gambar input (image_array)
            facial_area['image_width'] = original_width
            facial_area['image_height'] = original_height
            
            print(f"Landmarks reference size: {original_width}x{original_height}")
            print(f"Sample landmark (left_eye): {facial_area.get('left_eye', 'N/A')}")
            
            # Step 2: Dapatkan embedding dari wajah yang sudah di-crop dan di-align
            # Wajah yang sudah diproses ada di key 'face'
            embedding_obj = DeepFace.represent(
                img_path=face_obj['face'],
                model_name=config.DEEPFACE_MODEL_NAME,
                enforce_detection=False
            )
            
            embedding = embedding_obj[0]['embedding']

            return embedding, facial_area

        except Exception as e:
            print(f"Error saat ekstraksi embedding/landmarks: {e}")
            return None, None

    def get_iqa_scores(self, image_array: np.ndarray) -> Union[dict, None]:
        if image_array is None or image_array.size == 0: return None
        try:
            img_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).unsqueeze(0) / 255.0
            brisque_score = self.brisque_assessor(img_tensor.to(self.device)).item()
            niqe_score = self.niqe_assessor(img_tensor.to(self.device)).item()
            return {'brisque': round(brisque_score, 2), 'niqe': round(niqe_score, 2)}
        except Exception: return None

    def get_predictions(self, embedding: list) -> dict:
        def get_top5_classifier(model, embedding):
            probabilities = model.predict_proba([embedding])[0]
            top5_indices = np.argsort(probabilities)[-5:][::-1]
            return [{'label': self.label_encoder.inverse_transform([idx])[0], 'confidence': float(probabilities[idx])} for idx in top5_indices]

        knn_top5 = get_top5_classifier(self.knn_model, embedding)
        svm_top5 = get_top5_classifier(self.svm_model, embedding)

        # --- PERBAIKAN LOGIKA COSINE SIMILARITY ---
        distances = []
        for item in self.gallery_features:
            # Hitung jarak cosine (0 = identik, 2 = berlawanan)
            dist = cosine(embedding, item['embedding'])
            
            # --- RUMUS KEPERCAYAAN BARU ---
            # ArcFace biasanya menggunakan threshold 0.68 untuk verifikasi.
            # Jarak > 0.68 artinya "Beda Orang". Jarak < 0.68 artinya "Orang Sama".
            # Kita ubah jarak menjadi persentase sederhana:
            # Jika dist 0.0 -> 100%
            # Jika dist 1.0 -> 0%
            # Kami gunakan max(0, ...) agar tidak negatif.
            conf_score = max(0, 1.0 - dist)
            
            distances.append({
                'subject_id': item['subject_id'], 
                'image_path': item['image_path'], 
                'distance': dist,     # Simpan jarak asli
                'confidence': conf_score 
            })

        # Urutkan dari jarak terpendek (paling mirip)
        sorted_distances = sorted(distances, key=lambda x: x['distance'])
        
        # Ambil 5 teratas
        top5 = sorted_distances[:5]

        # --- DEBUG PRINT (Cek Terminal Anda saat upload!) ---
        print("\n--- DEBUG HASIL COSINE ---")
        for res in top5:
            print(f"Subjek: {res['subject_id']} | Jarak Asli: {res['distance']:.4f} | Conf: {res['confidence']:.2%}")
        print("--------------------------\n")

        # Format untuk JSON response
        cosine_top5 = [{
            'label': c['subject_id'], 
            'confidence': c['confidence'], 
            'image_url': f"/gallery/{Path(c['image_path']).name}"
        } for c in top5]

        return {'knn': knn_top5, 'svm': svm_top5, 'cosine': cosine_top5}

    def run_pipeline(self, image_path: Path) -> dict:
        img_probe = cv2.imdecode(np.fromfile(str(image_path), np.uint8), cv2.IMREAD_COLOR)
        if img_probe is None: return {"error": "Gagal membaca file gambar."}

        # --- Tambahan: Pastikan gambar tidak terlalu kecil ---
        MIN_WIDTH = 512
        h, w, _ = img_probe.shape
        if w < MIN_WIDTH:
            scale = MIN_WIDTH / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            img_probe = cv2.resize(img_probe, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        # --- Akhir Tambahan ---

        results = {'pipeline_a': None, 'pipeline_b': None, 'probe_coords': None}

        embedding_a, landmarks_a = self.get_embedding_and_landmarks(img_probe)
        if embedding_a:
            probe_x, probe_y = self._transform_probe_embedding(embedding_a)
            results['probe_coords'] = {'x': probe_x, 'y': probe_y}
            results['pipeline_a'] = {
                'iqa': self.get_iqa_scores(img_probe),
                'predictions': self.get_predictions(embedding_a),
                'landmarks': landmarks_a
            }

        _, restored_faces, _ = self.gfpgan_restorer.enhance(img_probe, has_aligned=True, only_center_face=False)
        if restored_faces and restored_faces[0] is not None:
            # Ambil dimensi gambar asli
            original_height, original_width, _ = img_probe.shape
            dsize = (original_width, original_height)

            # Resize gambar restorasi agar sama dengan ukuran asli
            restored_face = cv2.resize(restored_faces[0], dsize)

            embedding_b, landmarks_b = self.get_embedding_and_landmarks(restored_face)
            restored_filename = f"restored_{uuid.uuid4()}.png"
            cv2.imwrite(str(config.UPLOADS_DIR / restored_filename), restored_face)

            if embedding_b:
                results['pipeline_b'] = {
                    'iqa': self.get_iqa_scores(restored_face),
                    'predictions': self.get_predictions(embedding_b),
                    'restored_image_url': f"/uploads/{restored_filename}",
                    'landmarks': landmarks_b
                }
        
        return convert_to_native_python_types(results)
