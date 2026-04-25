# PostWA - WhatsApp Channel Auto Poster (Termux + VNC)

PostWA adalah alat otomatisasi untuk mengunggah media (foto/video) ke Saluran (Channel) WhatsApp menggunakan Selenium, Chromium, dan ChromeDriver di lingkungan Termux.

## ✨ Fitur Utama
- **Multi-Mode Tampilan**: Pilih antara mode **VNC** (visual) atau **Headless** (hemat RAM).
- **Auto Upload Berkelanjutan**: Mengunggah banyak file sekaligus secara otomatis.
- **Interval & Countdown**: Jeda waktu antar postingan yang dapat diatur dengan hitung mundur real-time.
- **Smart History Tracking**: Mencatat file yang sudah diunggah di `uploaded_history_wa.txt` agar tidak terjadi duplikasi.
- **Metadata Support**: Secara otomatis mengambil caption dari file `post_meta.json` jika tersedia.
- **Channel Database**: Menyimpan daftar channel Anda agar proses pemilihan lebih cepat.

## 🚀 Persiapan & Instalasi

Pastikan Anda telah menginstal dependensi yang diperlukan di Termux:
```bash
pkg update && pkg upgrade
pkg install chromium chromedriver python
pip install selenium
```

## 🛠️ Cara Penggunaan

### 1. Setup Sesi (Login)
Gunakan script ini untuk pertama kali login atau jika sesi Anda habis. Pastikan VNC Server sudah berjalan.
```bash
python setup_session_vnc.py
```
Buka VNC, scan QR Code, dan pastikan sudah masuk ke dashboard WhatsApp.

### 2. Jalankan Posting
Gunakan script utama untuk mulai mengunggah media:
```bash
python post_media_channel.py
```

### Alur Kerja Script:
1. **Pilih Mode**: VNC atau Headless.
2. **Input Folder**: Masukkan path folder tempat media Anda berada.
3. **Pilih Channel**: Pilih dari database atau lakukan RE-SCAN jika ada channel baru.
4. **Pilih Mode Upload**:
   - **Mode 1**: Pilih satu file tertentu untuk diupload.
   - **Mode 2 (Auto)**: Upload semua file di folder tersebut yang belum pernah diunggah sebelumnya.

## 📂 Struktur File
- `post_media_channel.py`: Script utama operasional.
- `setup_session_vnc.py`: Script khusus untuk setup sesi/login awal.
- `channels.txt`: Database nama-nama channel Anda.
- `uploaded_history_wa.txt`: Catatan riwayat file yang sukses terkirim.
- `chrome_profile/`: Folder data browser (berisi sesi login Anda).

## ⚠️ Catatan
- Jangan menghapus folder `chrome_profile` kecuali Anda ingin login ulang.
- Jika menggunakan mode **Headless**, pastikan Anda sudah login sukses melalui mode **VNC** terlebih dahulu.
- Pastikan display `:1` sudah aktif jika menggunakan mode VNC.
