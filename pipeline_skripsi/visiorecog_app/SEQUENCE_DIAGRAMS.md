## Sequence Diagrams - VisioRecog App

Di bawah ini adalah dua diagram sekuens yang menggambarkan alur kerja untuk masing-masing aktor: Pengguna dan Pengembang.

**Cara Melihat Visualisasi:**
1. Salin seluruh blok kode yang ada di dalam ` ```mermaid ... ``` `.
2. Buka [**Mermaid Live Editor**](https://mermaid.live).
3. Tempel kode tersebut di panel "Code" untuk melihat diagramnya.

---

### 1. Diagram Alur Pengguna Akhir

Diagram ini menunjukkan urutan kejadian dari saat pengguna mengunggah gambar hingga hasil analisis ditampilkan.

```mermaid
sequenceDiagram
    actor Pengguna
    participant Browser as Frontend UI
    participant Server as Backend API
    participant Pipeline as FaceRecognitionPipeline

    Pengguna->>+Browser: 1. Unggah gambar & klik "Mulai Analisis"
    Browser->>+Server: 2. POST /recognize (dengan file gambar)
    
    Server->>+Pipeline: 3. run_pipeline(image)
    
    par Jalur A (Gambar Asli)
        Pipeline->>Pipeline: 4a. Ekstrak fitur & hitung IQA
    and Jalur B (Gambar Restorasi)
        Pipeline->>Pipeline: 4b. Lakukan restorasi (GFPGAN)
        Pipeline->>Pipeline: 4c. Ekstrak fitur & hitung IQA hasil restorasi
    end
    
    Pipeline->>Pipeline: 5. Lakukan prediksi (KNN, SVM, Cosine) untuk kedua jalur
    
    Pipeline-->>-Server: 6. return analysisResult
    Server-->>-Browser: 7. Response 200 OK (dengan JSON hasil)
    Browser-->>-Pengguna: 8. Tampilkan halaman hasil analisis

```

---

### 2. Diagram Alur Inisialisasi Sistem (Pengembang)

Diagram ini menunjukkan urutan kejadian saat pengembang menyalakan server backend, di mana semua model dan konfigurasi dimuat ke dalam memori.

```mermaid
sequenceDiagram
    actor Pengembang
    participant Terminal
    participant Server as Backend API
    participant Pipeline as FaceRecognitionPipeline
    participant Filesystem as Model & Data Files

    Pengembang->>+Terminal: 1. Jalankan perintah (misal: uvicorn ...)
    Terminal->>+Server: 2. Inisialisasi aplikasi FastAPI
    
    Server->>+Pipeline: 3. __init__() (Membuat instance pipeline)
    
    Pipeline->>+Filesystem: 4. Muat model restorasi (GFPGAN)
    Filesystem-->>-Pipeline: (Bobot model .pth)
    
    Pipeline->>+Filesystem: 5. Muat model klasifikasi (.pkl)
    Filesystem-->>-Pipeline: (Model KNN & SVM)
    
    Pipeline->>+Filesystem: 6. Bangun fitur galeri (dari gambar di folder gallery)
    Filesystem-->>-Pipeline: (Data embedding galeri)

    Pipeline-->>-Server: 7. Inisialisasi pipeline selesai
    Server-->>-Terminal: 8. Tampilkan log "Aplikasi berhasil dimulai"
    Terminal-->>-Pengembang: (Server siap menerima permintaan)

```
