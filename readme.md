# Absensi Otomatis BSI

Skrip Python ini dirancang untuk mengotomatiskan proses absensi di situs web elearning.bsi.ac.id. Skrip ini melakukan login ke situs, memantau jadwal kelas, dan secara otomatis melakukan absensi ketika kelas dimulai.

## Fitur

* **Login Otomatis:** Melakukan login otomatis ke situs elearning.bsi.ac.id menggunakan kredensial yang tersimpan.
* **Pemantauan Jadwal:** Memantau jadwal kelas hari ini dan menentukan kelas mana yang sedang berlangsung atau akan segera dimulai.
* **Absensi Otomatis:** Melakukan absensi secara otomatis pada kelas yang sedang berlangsung atau ketika waktu absensi sudah dimulai.
* **Pengecekan Koneksi Internet:** Memeriksa koneksi internet sebelum memulai proses dan menangani masalah koneksi.
* **Pembaruan Otomatis:** Memiliki fitur untuk melakukan pembaruan otomatis dari GitHub.
* **Tampilan ASCII Art:** Menampilkan ASCII art pada awal program untuk mempercantik tampilan.
* **Penggunaan Colorama:** Menggunakan library colorama untuk pewarnaan teks di terminal.

## Cara Penggunaan

1.  **Persiapan**

    * Pastikan Anda telah menginstal Python 3.6 atau lebih tinggi.
    * Instal library yang dibutuhkan. Anda dapat menginstalnya menggunakan pip. Pastikan Anda berada di direktori yang sama dengan skrip Python dan file `requirements.txt`. Jalankan perintah:

        ```bash
        pip install -r requirements.txt
        ```

        File `requirements.txt` harus berada di direktori yang sama dengan skrip Python dan berisi:

        ```text
        aiohttp
        beautifulsoup4
        colorama
        requests
        ```

    * Buat file `memory.json` di direktori yang sama dengan skrip Python. File ini harus berisi kredensial login Anda dan URL situs. Contoh format `memory.json`:

        ```json
        {
            "username": "username_anda",
            "password": "password_anda",
            "LOGIN_URL": "URL_halaman_login",
            "DASHBOARD_URL": "URL_dashboard",
            "SCHEDULE_URL": "URL_jadwal"
        }
        ```

        **Penting:** Ganti `"username_anda"`, `"password_anda"`, `"URL_halaman_login"`, `"URL_dashboard"`, dan `"URL_jadwal"` dengan informasi yang sesuai. **Jangan pernah menyimpan file `memory.json` ke dalam repositori publik.**
2.  **Menjalankan Skrip**

    * Buka terminal dan navigasikan ke direktori tempat Anda menyimpan skrip Python dan file `memory.json`.
    * Jalankan skrip dengan perintah:

        ```bash
        python absen.py
        ```
3.  **Pembaruan Skrip**

    * Untuk memperbarui skrip ke versi terbaru dari GitHub, jalankan dengan argumen `-update`:

        ```bash
        python absen.py -update
        ```

## Penjelasan Kode

* `display_ascii_art()`: Fungsi untuk menampilkan ASCII art.
* `load_memory()`: Fungsi untuk memuat data kredensial dan URL dari file `memory.json`.
* `check_internet_connection()`: Fungsi asynchronous untuk memeriksa koneksi internet.
* `handle_connection_issues()`: Fungsi asynchronous untuk menangani masalah koneksi internet.
* `solve_captcha()`: Fungsi untuk memecahkan pertanyaan captcha sederhana (penjumlahan).
* `validate_login_page()`: Fungsi untuk memvalidasi struktur halaman login.
* `check_if_logged_in()`: Fungsi asynchronous untuk memeriksa apakah pengguna sudah login.
* `login_to_site()`: Fungsi asynchronous utama untuk melakukan proses login.
* `mark_attendance()`: Fungsi asynchronous untuk menandai kehadiran.
* `process_classes()`: Fungsi untuk memproses data kelas dari halaman jadwal.
* `display_today_schedule()`: Fungsi untuk menampilkan jadwal kelas hari ini.
* `monitor_and_attend_classes()`: Fungsi asynchronous untuk memantau kelas dan melakukan absensi otomatis.
* `join_and_attend_class()`: Fungsi asynchronous untuk masuk ke kelas dan melakukan absen.
* `navigate_to_attendance()`: Fungsi asynchronous untuk menavigasi ke halaman kehadiran.
* `schedule_attendance_check()`: Fungsi asynchronous untuk menjadwalkan pengecekan kehadiran secara berkala.
* Bagian `if __name__ == "__main__":` adalah titik masuk utama program.

## Peringatan

* **Penggunaan skrip ini sepenuhnya menjadi tanggung jawab Anda.**
* Pastikan Anda memahami risiko yang terlibat sebelum menggunakan skrip ini.
* Pengembang tidak bertanggung jawab atas konsekuensi yang mungkin timbul akibat penggunaan skrip ini.
* Modifikasi skrip mungkin diperlukan jika struktur situs web elearning.bsi.ac.id berubah.
* Gunakan skrip ini dengan bijak dan etis.