# ♻ Nirsampah
### Kelola, Pilah, dan Jemput Sampahmu dengan Mudah


## Tentang Aplikasi

Aplikasi ini terinspirasi dari keresahan sehari-hari yang sering kita temui di lingkungan sekitar, tumpukan sampah yang tidak terpilah, masyarakat yang bingung membedakan jenis sampah yang mereka miliki, hingga sulitnya menemukan lokasi Tempat Pembuangan Sampah terdekat. Kami melihat bahwa masalah pengelolaan sampah bukan semata-mata karena kurangnya kepedulian, melainkan karena minimnya akses informasi yang mudah dan cepat.

Dari situ lahirlah **Nirsampah** sebuah platform digital pengelolaan sampah berbasis web yang kami bangun menggunakan Python Flask. Nama *Nirsampah* berasal dari kata *nir* (tanpa) yang mencerminkan visi kami: dunia yang bebas dari sampah yang tidak terkelola dengan baik. Nirsampah hadir untuk membantu masyarakat mengidentifikasi jenis sampah secara instan, menemukan TPS terdekat melalui peta interaktif, melihat jadwal pengangkutan sampah per wilayah, hingga mengajukan layanan penjemputan sampah langsung dari rumah, semua dalam satu platform yang sederhana dan mudah digunakan.


## Fitur Utama

1. Klasifikasi Sampah - Ketik nama sampah, sistem langsung menentukan kategori (Organik, Anorganik, atau B3) beserta panduan penanganannya
2. Cari TPS - Temukan lokasi Tempat Pembuangan Sampah terdekat via API OpenStreetMap dengan peta interaktif Leaflet
3. Jadwal Pengangkutan - Lihat jadwal pengangkutan sampah per wilayah (tersedia 8 kecamatan di Sukabumi)
4. Layanan Penjemputan - Ajukan permintaan penjemputan sampah dari rumah dan pantau statusnya secara real-time
5. Login & Registrasi - Sistem autentikasi aman dengan password yang di-hash menggunakan Werkzeug


## Teknologi yang Digunakan

| Komponen Teknologi |
| Backend | Python Flask |
| Database | SQLite |
| API Lokasi | Nominatim OpenStreetMap |
| Peta Interaktif | Leaflet.js |
| Frontend | HTML5, CSS3 |

## Struktur Folder

nirsampah/
├── backend/
│   ├── app.py          > Routing, login, semua endpoint Flask
│   └── models.py       > Class OOP: Waste, User, PickupRequest, Database
├── frontend/
│   ├── templates/      > Halaman HTML (Jinja2)
│   └── static/
│       ├── css/        > style.css
│       ├── js/         > map.js (peta interaktif)
│       └── img/        > Foto tim & aset gambar
├── database.db         > Dibuat otomatis saat pertama kali dijalankan
└── requirements.txt


## Cara Menjalankan

### 1. Pastikan Python sudah terinstall
```bash
python --version
```
Minimal Python 3.8 ke atas.

### 2. Masuk ke folder project
```bash
cd smart_waste
```

### 3. (Opsional) Buat virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 4. Install dependensi
```bash
pip install -r requirements.txt
```

### 5. Jalankan aplikasi
```bash
cd backend
python app.py
```

### 6. Buka di browser
```
http://127.0.0.1:5000
```

Catatan: Database (`database.db`) akan dibuat otomatis di folder `smart_waste/` saat pertama kali aplikasi dijalankan. Tidak perlu setup database secara manual.


## Implementasi OOP

Seluruh konsep OOP ada di file `backend/models.py`:

| Konsep Penerapan |
| Inheritance | `OrganicWaste`, `InorganicWaste`, `HazardousWaste` mewarisi class `Waste` |
| Encapsulation | Atribut `__name` (Waste) dan `__username`, `__email`, `__password_hash` (User) dibuat private |
| Polymorphism | Method `get_category()`, `get_description()`, `get_handling()` di-override di tiap subclass |


> *Mulai dari hal kecil. Pilah sampahmu hari ini, jaga bumi untuk esok.*
