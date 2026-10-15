# Dashboard Analitik Penjualan

Aplikasi dashboard interaktif untuk memahami transaksi penjualan dengan Python, Pandas, dan Streamlit. Dashboard menyediakan ringkasan metrik, grafik tren, perbandingan kategori dan wilayah, filter data, serta ekspor CSV.

## Fitur

- Memakai dataset contoh atau mengunggah data transaksi berformat CSV/Excel.
- Filter transaksi berdasarkan tanggal, jenis produk, dan wilayah.
- Ringkasan total penjualan, unit terjual, dan rata-rata nilai transaksi.
- Grafik tren bulanan dengan perkiraan sederhana, penjualan per jenis produk, dan pembagian menurut wilayah.
- Tabel transaksi dan unduhan data hasil filter maupun ringkasan.

## Persyaratan

- Python 3.9 atau lebih baru.
- Pustaka yang tercantum di `requirements.txt`.

## Instalasi dan menjalankan aplikasi

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Setelah berjalan, Streamlit menampilkan alamat lokal aplikasi di terminal (umumnya `http://localhost:8501`).

## Mengunggah data

Di panel kiri, unggah berkas `.csv` atau `.xlsx`. Baris dengan tanggal atau nilai angka yang tidak valid akan dibuang; nilai kategori yang kosong diisi sebagai `Unknown`. Berkas harus memiliki kolom berikut:

| Kolom | Isi |
| --- | --- |
| `date` | Tanggal transaksi yang dapat dibaca sebagai tanggal |
| `product_category` | Jenis/kategori produk |
| `revenue` | Pendapatan transaksi, angka nol atau lebih |
| `units_sold` | Jumlah unit terjual, angka nol atau lebih |
| `region` | Wilayah penjualan |
| `customer_type` | Jenis pelanggan |

Contoh berkas tersedia di `data/sample_data.csv`. Untuk membuat ulang data contoh (300 transaksi):

```powershell
python src/data_generator.py
```

## Struktur proyek

```text
.
├── app.py                  # Antarmuka Streamlit dan visualisasi
├── requirements.txt        # Dependensi Python
├── data/
│   ├── sample_data.csv     # Dataset contoh
│   ├── raw/                # Lokasi data mentah
│   └── processed/          # Lokasi data hasil pemrosesan
└── src/
    ├── analytics.py        # KPI, agregasi bulanan, dan perkiraan
    ├── data_generator.py   # Generator dataset contoh
    └── data_loader.py      # Validasi, pembersihan, dan pembacaan data
```

## Catatan

- Rata-rata nilai transaksi dihitung sebagai total pendapatan dibagi jumlah baris transaksi yang lolos filter.
- Forecast merupakan tren linear sederhana dari data bulanan yang tersedia, bukan jaminan hasil penjualan.
- Simpan data sensitif di luar repositori dan pastikan izin aksesnya sesuai.