# Proyek Restorasi dan Verifikasi Wajah

Proyek ini adalah implementasi alur kerja _end-to-end_ untuk merestorasi gambar wajah berkualitas rendah menggunakan **GFPGAN** dan kemudian memverifikasi identitas wajah yang telah direstorasi terhadap gambar referensi berkualitas tinggi menggunakan model **ArcFace**.

## Alur Kerja Proyek

Alur kerja utama proyek ini adalah sebagai berikut:

1.  **Input**: Sebuah gambar wajah dengan resolusi rendah atau kualitas yang terdegradasi.
2.  **Restorasi Wajah**: Gambar input diproses oleh **GFPGAN (Generative Facial Prior - Generative Adversarial Network)** untuk meningkatkan kualitas, ketajaman, dan detail wajah secara signifikan.
3.  **Verifikasi Wajah**: Wajah yang telah direstorasi kemudian dibandingkan dengan gambar wajah referensi (berkualitas tinggi) menggunakan _library_ `deepface` dengan model **ArcFace** untuk menghitung kesamaan dan memverifikasi apakah keduanya adalah orang yang sama.
4.  **Output**: Hasil restorasi disimpan sebagai gambar baru, dan hasil verifikasi (termasuk skor jarak dan status "terverifikasi" atau "tidak") ditampilkan.

## Komponen Utama

- **GFPGAN (`model_gfpgan`)**: Digunakan untuk tugas restorasi wajah buta (_blind face restoration_). Model ini mampu menghasilkan wajah yang realistis dan berkualitas tinggi bahkan dari input yang sangat rusak, dengan memanfaatkan _prior_ dari model StyleGAN2 yang sudah dilatih sebelumnya.
- **ArcFace (`model_arcface`)**: Digunakan untuk tugas verifikasi wajah. ArcFace adalah model pengenalan wajah _state-of-the-art_ yang sangat akurat dalam mengukur kesamaan antara dua wajah dengan menghitung jarak (_distance_) antara _embedding_ wajah mereka.

## Struktur Direktori

```
.
├── model_arcface/
│   └── model.ipynb         # Notebook untuk verifikasi wajah menggunakan ArcFace.
├── model_gfpgan/
│   ├── inference_gfpgan.py # Skrip utama untuk menjalankan restorasi dengan GFPGAN.
│   └── README.md           # README asli dari repositori GFPGAN.
├── raw_hq_data/              # Tempat untuk menyimpan gambar referensi berkualitas tinggi.
├── raw_lq_data/              # Tempat untuk menyimpan gambar input berkualitas rendah.
├── results/                  # Folder output untuk hasil restorasi dari GFPGAN.
├── osd_face.ipynb            # Notebook untuk eksperimen pemuatan data.
└── README.md                 # File ini.
```

## Instalasi

1.  **Clone repositori ini (jika belum):**

    ```bash
    git clone <URL_REPOSITORI_ANDA>
    cd <NAMA_DIREKTORI>
    ```

2.  **Buat dan aktifkan lingkungan virtual (disarankan):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # atau
    .venv\Scripts\activate    # Windows
    ```

3.  **Install dependensi yang dibutuhkan:**
    Proyek ini memerlukan beberapa _library_ Python. Anda dapat menginstalnya menggunakan pip dengan file `requirements.txt` yang ada di dalam folder `model_gfpgan`.

    ```bash
    pip install -r model_gfpgan/requirements.txt
    pip install deepface # Dependensi tambahan untuk verifikasi
    ```

    _Catatan: Skrip GFPGAN akan secara otomatis mengunduh model-model yang diperlukan saat pertama kali dijalankan._

## Cara Penggunaan

### 1. Restorasi Wajah dengan GFPGAN

- Tempatkan gambar berkualitas rendah yang ingin Anda restorasi di dalam folder `raw_lq_data/`.
- Jalankan skrip `inference_gfpgan.py` dari dalam direktori `model_gfpgan/`.

  ```bash
  cd model_gfpgan
  python inference_gfpgan.py -i ../raw_lq_data -o ../results -v 1.4 -s 2 --bg_upsampler realesrgan
  cd ..
  ```

  - `-i ../raw_lq_data`: Menentukan folder input.
  - `-o ../results`: Menentukan folder output.
  - `-v 1.4`: Menggunakan model GFPGAN versi 1.4 (menghasilkan detail lebih baik).
  - `-s 2`: Skala upsampling.
  - `--bg_upsampler realesrgan`: Secara opsional juga meningkatkan kualitas latar belakang.

  Hasil restorasi akan disimpan di dalam folder `results/`.

### 2. Verifikasi Wajah dengan ArcFace

- Pastikan Anda memiliki gambar referensi berkualitas tinggi di `raw_hq_data/`.
- Pastikan gambar hasil restorasi sudah ada di `results/restored_faces/`.
- Buka dan jalankan sel-sel kode di dalam _notebook_ `model_arcface/model.ipynb`.

  _Notebook_ ini akan:

  - Memuat gambar HQ dan gambar hasil restorasi.
  - Menjalankan `DeepFace.verify()` untuk membandingkan keduanya.
  - Menghasilkan visualisasi perbandingan berdampingan yang menunjukkan gambar HQ, gambar LQ (input awal), dan gambar yang telah direstorasi, lengkap dengan status verifikasi.

---

Dibuat dengan bantuan AI.
