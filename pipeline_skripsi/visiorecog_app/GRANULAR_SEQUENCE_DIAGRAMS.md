## 10 Sequence Diagrams (Granular)

Berikut adalah 10 diagram sekuens yang dibuat satu per satu berdasarkan 10 Activity Diagram yang Anda berikan.

**Cara Melihat Visualisasi:**
1. Salin seluruh blok kode yang ada di dalam ` ```mermaid ... ``` ` untuk satu diagram.
2. Buka [**Mermaid Live Editor**](https://mermaid.live).
3. Tempel kode tersebut di panel "Code" untuk melihat diagramnya.

---

### 1. Mengunggah Gambar Wajah

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    actor Pengguna
    participant Browser as Frontend UI

    Pengguna->>Browser: Memilih file gambar (jpg/png)
    activate Browser
    Browser->>Browser: Memeriksa tipe file
    alt Tipe file valid
        Browser-->>Pengguna: Mengaktifkan tombol 'Mulai Analisis'
    else Tipe file tidak valid
        Browser-->>Pengguna: Menampilkan pesan error
    end
    deactivate Browser
```

---

### 2. Memulai Analisis

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    actor Pengguna
    participant Browser as Frontend UI
    participant Server as Backend API

    Pengguna->>Browser: Menekan tombol "Mulai Analisis"
    activate Browser
    Browser->>Browser: Menampilkan indikator loading
    Browser->>Server: Kirim request POST /recognize dengan gambar
    deactivate Browser
```

---

### 3. Proses Restorasi dan Rekognisi

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    participant Server as Backend API
    participant Pipeline

    activate Server
    Server->>Pipeline: panggil: run_pipeline(gambar)
    activate Pipeline
    par 
        Pipeline->>Pipeline: Ekstrak Embedding (Gambar Asli)
    and
        Pipeline->>Pipeline: Analisis IQA (Gambar Asli)
    and
        Pipeline->>Pipeline: Lakukan Restorasi (GFPGAN)
    end
    Pipeline->>Pipeline: Proses IQA & Embedding (Gambar Restorasi)
    Pipeline->>Pipeline: Lakukan semua prediksi (KNN, SVM, Cosine)
    Pipeline->>Pipeline: Hitung koordinat t-SNE
    Pipeline-->>Server: Mengembalikan data hasil lengkap (JSON)
    deactivate Pipeline
    deactivate Server
```

---

### 4. Melihat Hasil Restorasi dan Rekognisi

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    participant Browser as Frontend UI
    actor Pengguna

    activate Browser
    Note over Browser: Menerima data hasil dari Server
    Browser->>Browser: Render gambar asli & restorasi
    Browser->>Browser: Render skor IQA
    Browser->>Browser: Render tabel prediksi
    Browser-->>Pengguna: Menampilkan semua hasil
    deactivate Browser
    Pengguna->>Pengguna: Mengamati dan membandingkan hasil
```

---

### 5. Melihat Plot Embedding dan Face Landmarks

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    participant Browser as Frontend UI
    actor Pengguna

    activate Browser
    Note over Browser: Halaman hasil sudah ditampilkan
    Browser->>Browser: Render plot t-SNE
    Browser->>Browser: Render visualisasi Face Landmarks
    Browser-->>Pengguna: Menampilkan plot dan landmarks
    deactivate Browser
    Pengguna->>Pengguna: Mengamati posisi titik pada plot & wajah
```

---

### 6. Mempersiapkan Model Klasifikasi

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    actor Pengembang
    participant Terminal
    participant Filesystem

    Pengembang->>Terminal: Menjalankan skrip pelatihan (misal: train.py)
    activate Terminal
    Terminal->>Filesystem: Menyimpan model SVM (.pkl)
    Terminal->>Filesystem: Menyimpan model KNN (.pkl)
    deactivate Terminal
```

---

### 7. Mempersiapkan Model Restorasi

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    actor Pengembang
    participant Filesystem

    Pengembang->>Filesystem: Mengunduh & menempatkan file bobot GFPGAN (.pth)
```

---

### 8. Mempersiapkan Model Rekognisi

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    actor Pengembang
    participant Filesystem

    Pengembang->>Filesystem: Mengunduh & menempatkan file bobot ArcFace
```

---

### 9. Mengidentifikasi Subjek

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    participant Pipeline

    Note over Pipeline: Menerima embedding probe
    activate Pipeline
    par 
        Pipeline->>Pipeline: Perhitungan Cosine Similarity
    and
        Pipeline->>Pipeline: Perhitungan KNN
    and
        Pipeline->>Pipeline: Perhitungan SVM
    end
    Pipeline->>Pipeline: Membungkus hasil prediksi ke dalam JSON
    deactivate Pipeline
```

---

### 10. Restorasi Subjek

*Catatan: Activity diagram untuk ini tampak identik dengan "Mengidentifikasi Subjek". Diagram sekuens berikut dibuat berdasarkan **nama** aktivitasnya, yaitu restorasi.*

```mermaid
%%{init: { "theme": "default", "fontFamily": "Times New Roman, Times, serif" } }%%
sequenceDiagram
    participant Pipeline

    Note over Pipeline: Menerima gambar input untuk direstorasi
    activate Pipeline
    Pipeline->>Pipeline: Memanggil model restorasi (GFPGAN)
    Pipeline->>Pipeline: Mengembalikan gambar yang telah direstorasi
    deactivate Pipeline
```
