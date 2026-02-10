### Tabel Rencana Pengujian

| ID | Nama Pengujian | Tingkat Pengujian |
| :--- | :--- | :--- |
| **Unit Testing** |
| `UT-01` | Memverifikasi fungsi `get_iqa_scores` dapat menghitung skor BRISQUE dan NIQE secara akurat dari gambar input. | Unit Testing |
| `UT-02` | Memverifikasi fungsi `get_predictions` mengembalikan struktur data prediksi yang benar untuk metode KNN, SVM, dan Cosine. | Unit Testing |
| **Integration Testing** |
| `IT-01` | Pengujian endpoint API `/recognize` untuk memastikan data gambar dari frontend dapat diproses oleh backend dan mengembalikan `AnalysisResult`. | Integration Testing |
| `IT-02` | Pengujian endpoint API `/embedding-plot` untuk memastikan data plot t-SNE dari backend dapat diterima dan ditampilkan oleh frontend. | Integration Testing |
| **System Testing** |
| `ST-01` | Pengujian alur kerja End-to-End: mulai dari unggah gambar, proses analisis, hingga semua komponen hasil ditampilkan dengan benar di UI. | System Testing |
| `ST-02` | Pengujian fungsionalitas tampilan hasil, termasuk validasi kebenaran data pada gambar asli, gambar restorasi, skor IQA, dan semua tabel prediksi. | System Testing |
| `ST-03` | Pengujian penanganan error sistem, seperti saat koneksi ke backend gagal atau server mengembalikan respons error. | System Testing |
| `ST-04` | Pengujian performa sistem untuk mengukur total waktu respons dari saat pengguna mengunggah gambar hingga hasil ditampilkan. | System Testing |
