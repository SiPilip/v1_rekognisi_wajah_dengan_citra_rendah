## Sequence Diagrams - VisioRecog App (Based on Activity Diagrams)

Berikut adalah 4 diagram sekuens yang dibuat berdasarkan Activity Diagram yang Anda berikan. Diagram ini mencakup semua alur kerja untuk aktor Pengguna dan Pengembang.

**Cara Melihat Visualisasi:**
1. Salin seluruh blok kode yang ada di dalam ` ```mermaid ... ``` `.
2. Buka [**Mermaid Live Editor**](https://mermaid.live).
3. Tempel kode tersebut di panel "Code" untuk melihat diagramnya.

---

### Diagram 1: Memulai Analisis oleh Pengguna
*Mencakup aktivitas: "Mengunggah Gambar Wajah" & "Memulai Analisis"*

```mermaid
sequenceDiagram
    actor Pengguna
    participant Browser as Frontend UI
    participant Server as Backend API

    Pengguna->>Browser: 1. Memilih file gambar (jpg/png)
    activate Browser
    Browser->>Browser: 2. Memeriksa tipe file
    alt Tipe file valid
        Browser-->>Pengguna: 3. Mengaktifkan tombol "Mulai Analisis"
    else Tipe file tidak valid
        Browser-->>Pengguna: 3. Menampilkan pesan error & meminta pilih ulang
    end
    
    Pengguna->>Browser: 4. Menekan tombol "Mulai Analisis"
    Browser->>Browser: 5. Menampilkan indikator loading
    Browser->>Server: 6. Mengirim request POST /recognize dengan data gambar
    deactivate Browser
    activate Server
    Note right of Server: Server mulai memproses...
    deactivate Server
```

---

### Diagram 2: Proses Analisis di Backend
*Mencakup aktivitas: "Proses Restorasi dan Rekognisi", "Mengidentifikasi Subjek", "Restorasi Subjek"*

```mermaid
sequenceDiagram
    participant Server as Backend API
    participant Pipeline

    activate Server
    Note left of Server: Menerima request dari Browser
    Server->>Pipeline: 1. panggil: run_pipeline(gambar)
    activate Pipeline
    
    par Jalur A (Gambar Asli)
        Pipeline->>Pipeline: 2a. Analisis IQA (NIQE & BRISQUE)
        Pipeline->>Pipeline: 2b. Ekstrak Embedding (ArcFace)
    and Jalur B (Gambar Restorasi)
        Pipeline->>Pipeline: 2c. Lakukan Restorasi (GFPGAN)
        Pipeline->>Pipeline: 2d. Analisis IQA pada gambar hasil restorasi
        Pipeline->>Pipeline: 2e. Ekstrak Embedding dari gambar hasil restorasi
    end

    loop Untuk setiap Embedding (A & B)
        Pipeline->>Pipeline: 3. Lakukan pencocokan (KNN, SVM, Cosine Similarity)
    end

    Pipeline->>Pipeline: 4. Hitung koordinat t-SNE untuk plot
    Pipeline-->>Server: 5. Menyusun & mengembalikan semua data hasil dalam format JSON
    deactivate Pipeline
    Note right of Server: Mengirim respons kembali ke Browser...
    deactivate Server
```

---

### Diagram 3: Menampilkan Hasil kepada Pengguna
*Mencakup aktivitas: "Melihat Hasil Restorasi dan Rekognisi" & "Melihat Plot Embedding dan Face Landmarks"*

```mermaid
sequenceDiagram
    participant Browser as Frontend UI
    actor Pengguna

    activate Browser
    Note left of Browser: Menerima respons JSON dari Server
    Browser->>Browser: 1. Render gambar asli dan hasil restorasi
    Browser->>Browser: 2. Render skor IQA (Brisque & NIQE)
    Browser->>Browser: 3. Render tabel prediksi (KNN, SVM, Cosine)
    Browser->>Browser: 4. Render plot t-SNE
    Browser->>Browser: 5. Render visualisasi Face Landmarks
    
    Browser-->>Pengguna: 6. Menampilkan halaman hasil analisis yang lengkap
    deactivate Browser

    Pengguna->>Pengguna: 7. Mengamati & membandingkan semua hasil
```

---

### Diagram 4: Persiapan Aset oleh Pengembang
*Mencakup aktivitas: "Mempersiapkan Model Klasifikasi", "Mempersiapkan Model Restorasi", "Mempersiapkan Model Rekognisi"*

```mermaid
sequenceDiagram
    actor Pengembang
    participant Terminal
    participant Filesystem

    Pengembang->>Terminal: 1. Menjalankan skrip pelatihan klasifikasi
    activate Terminal
    Terminal->>Filesystem: 2. Menyimpan model KNN & SVM (.pkl)
    deactivate Terminal

    Pengembang->>Filesystem: 3. Mengunduh & menempatkan bobot model ArcFace
    Pengembang->>Filesystem: 4. Mengunduh & menempatkan bobot model GFPGAN (.pth)

    Note over Pengembang, Filesystem: Semua aset dan model siap untuk dimuat oleh aplikasi saat startup.

```
