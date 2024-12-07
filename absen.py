import aiohttp
import asyncio
import os
from datetime import datetime
from bs4 import BeautifulSoup
import locale
from datetime import timedelta
import colorama
from colorama import Fore, Back, Style
import time
import requests
import sys

# Inisialisasi colorama
colorama.init(autoreset=True)

# Atur bahasa lokal ke bahasa Indonesia
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# URL untuk masuk dan dasbor
LOGIN_URL = "https://elearning.bsi.ac.id/login"
DASHBOARD_URL = "https://elearning.bsi.ac.id/user/dashboard"
SCHEDULE_URL = "https://elearning.bsi.ac.id/sch"

# Kredensial pengguna
username = "19215324"  # Ganti dengan NIP/NIM Anda
password = "Polrescikarang!1"  # Ganti dengan kata sandi Anda

def update_program():
    # URL file dari Google Drive
    file_url = "https://drive.google.com/uc?id=1sQ6-4-m2QdRiAsaAj7LqJM-2fVXKQjBq&export=download"
    local_file = "absen.py"  # Nama file lokal yang akan diperbarui

    try:
        print("Mengunduh versi terbaru program...")
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Periksa apakah ada kesalahan HTTP

        with open(local_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print("Program berhasil diperbarui. Jalankan ulang script.")
        sys.exit(0)  # Keluar setelah update
    except requests.RequestException as e:
        print(f"Gagal memperbarui program: {e}")
        sys.exit(1)

# Fungsi untuk memeriksa koneksi internet
async def check_internet_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.google.com", ssl=False, timeout=5) as response:
                if response.status == 200:
                    print(" Koneksi internet berhasil.")
                    return True
    except aiohttp.ClientError as e:
        print(f" Koneksi internet gagal. Error: {e}")
    except asyncio.TimeoutError:
        print(" Timeout saat memeriksa koneksi internet.")
    return False

# Fungsi untuk menangani reset saat koneksi bermasalah
async def handle_connection_issues():
    while True:
        is_connected = await check_internet_connection()
        if is_connected:
            return  # Keluar dari loop jika koneksi berhasil
        else:
            print("Koneksi internet bermasalah. Program akan mencoba lagi dalam 30 detik...")
            await asyncio.sleep(30)  # Tunggu 30 detik sebelum mencoba lagi

# Fungsi untuk memecahkan captcha
def solve_captcha(question):
    question = question.replace("?", "").strip()
    parts = question.split()
    try:
        num1 = int(parts[3])  # Nomor pertama
        num2 = int(parts[5])   # Nomor kedua
        return num1 + num2     # tambahkan jumlahnya
    except (ValueError, IndexError):
        return None

# Fungsi untuk memvalidasi halaman login
def validate_login_page(soup):
    return all(soup.find("input", {"name": name}) for name in ["_token", "username", "password"])

# Fungsi untuk memeriksa apakah pengguna sudah masuk
async def check_if_logged_in(session):
    try:
        async with session.get(DASHBOARD_URL, ssl=False) as dashboard_response:
            dashboard_text = await dashboard_response.text()
            if "Dashboard" in dashboard_text:
                print(" Pengguna sudah login.\n")
                return True
            else:
                print(" Pengguna belum login. \n")
                return False
    except aiohttp.ClientError as e:
        print(f" Error saat memeriksa login: {e}\n")
        return False

# Fungsi untuk menambahkan efek pemuatan seperti hacker (dihapus)
def hacker_animation(text, delay=0.08):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # Pindah ke baris berikutnya setelah animasi selesai

# Fungsi utama untuk login ke situs
async def login_to_site(session):
    try:
        print(" Memulai proses login...\n")
        if await check_if_logged_in(session):
            print(" Sudah login sebelumnya, melanjutkan ke jadwal.")
            return await navigate_to_attendance(session)

        async with session.get(LOGIN_URL, ssl=False) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            print(" Berhasil mengakses halaman login.\n")

            if not validate_login_page(soup):
                print(" Halaman login tidak valid.")
                return "Validasi halaman login gagal."

            token = soup.find("input", {"name": "_token"}).get("value")
            captcha_question = soup.find("p", {"id": "captcha_question"})
            if not captcha_question:
                print(" Tidak dapat menemukan pertanyaan captcha.")
                return "Tidak dapat menemukan pertanyaan captcha."

            captcha_answer = solve_captcha(captcha_question.text)
            if captcha_answer is None:
                print(" Gagal memecahkan captcha.")
                return "Gagal memecahkan captcha."

            payload = {
                "_token": token,
                "username": username,
                "password": password,
                "captcha_answer": captcha_answer,
            }

            print(" Payload login siap. Mengirimkan request login...\n")
            async with session.post(LOGIN_URL, data=payload, ssl=False) as login_response:
                if "Dashboard" in await login_response.text():
                    print(" Login berhasil!\n")
                    return await navigate_to_attendance(session)
                else:
                    print(" Login gagal. Cek kredensial.")
                    return "Login gagal. Periksa kredensial Anda."
    except aiohttp.ClientError as e:
        print(f" Error saat login: {e}")
        return f"Error during request: {str(e)}"

# Fungsi untuk menandai kehadiran setelah kelas ditemukan
async def mark_attendance(session, token, pertemuan, id):
    attendance_url = "https://elearning.bsi.ac.id/mhs-absen"
    data = {
        "_token": token,
        "pertemuan": pertemuan,
        "id": id
    }

    while True:  # Lakukan pengecekan berkala
        async with session.post(attendance_url, data=data, ssl=False) as response:
            if response.status == 200:
                print("Absen berhasil dilakukan!\n")
                return "Absen berhasil dilakukan. \n"
            elif response.status == 400:  # Status 400 biasanya untuk kondisi belum tersedia
                print("Absen belum dibuka oleh dosen. Menunggu 5 menit...")
                await asyncio.sleep(300)  # Tunggu 5 menit sebelum mencoba lagi
            else:
                return f"Gagal melakukan absen. Status code: {response.status}"
# Fungsi untuk memproses kelas dan menentukan jadwal hari ini
def process_classes(classes, current_time):
    print(" Mulai memproses kelas.\n")
    today_classes = []
    day_mapping = {
        "Jumat": 4,  # Jumat = 4 (0 = Monday, 6 = Sunday)
        "Sabtu": 5   # Sabtu = 5
    }

    for class_info in classes:
        try:
            course_name = class_info.find('h6').text.strip()
            time_info = class_info.find("div", class_="pricing-save").text.strip()
            day, time_range = time_info.split(" - ")
            start_time_str, end_time_str = time_range.split("-")

            print(f" Data kelas ditemukan: {course_name}, {day}, {time_range}")
            if day not in day_mapping:
                print(f" Hari {day} tidak sesuai.")
                continue

            start_time = datetime.strptime(start_time_str.strip(), "%H:%M")
            end_time = datetime.strptime(end_time_str.strip(), "%H:%M")
            start_time = current_time.replace(hour=start_time.hour, minute=start_time.minute, second=0)
            end_time = current_time.replace(hour=end_time.hour, minute=end_time.minute, second=0)
            while start_time.weekday() != day_mapping[day]:
                start_time += timedelta(days=1)
                end_time += timedelta(days=1)

            if start_time.date() == current_time.date():
                today_classes.append((course_name, start_time, end_time))
        except Exception as e:
            print(f" Error processing class: {e}")
    return today_classes

# Fungsi untuk menampilkan jadwal hari ini
def display_today_schedule(today_classes):
    if today_classes:
        print("Jadwal Kelas Hari Ini:")
        for course_name, start_time, end_time in today_classes:
            print(f"Kelas: {course_name}")
            print(f"Waktu: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
            print("-" * 30)
    else:
        print("Tidak ada jadwal untuk hari ini.")  # Cetak hanya sekali di sini

# Fungsi untuk memantau kelas dan langsung absen jika sudah waktunya
async def monitor_and_attend_classes(session, classes, today_classes):
    print(" Mulai memantau kelas.\n")
    current_time = datetime.now()
    for course_name, start_time, end_time in today_classes:
        print(f" Memantau kelas: {course_name} {start_time} - {end_time}")
        
        if current_time > end_time:
            print(f"Kelas {course_name} telah berakhir. Tidak ada tindakan lebih lanjut.\n")
            continue  # Lanjutkan ke kelas berikutnya

        if current_time >= start_time:
            print(f" Waktunya absen untuk kelas {course_name}. Memulai proses absen...\n")

            # Proses bergabung ke kelas
            for class_info in classes:
                course_name_check = class_info.find('h6').text.strip()
                if course_name_check == course_name:
                    join_class_button = class_info.find("a", class_="btn btn-primary btn-lg")
                    if join_class_button:
                        join_class_url = join_class_button['href']

                        while True:  # Loop untuk mencoba absen ulang setiap 5 menit
                            response = await join_and_attend_class(session, join_class_url, course_name)
                            if response == "Absen berhasil dilakukan!" or response == "Absen sudah selesai":
                                print("Absen berhasil atau sudah selesai! Keluar dari loop.")
                                return  # Keluar setelah berhasil absen atau jika absen sudah selesai
                            elif response == "Absen belum dimulai":
                                print(f"Tombol absen belum tersedia untuk kelas {course_name}. Menunggu 5 menit untuk mencoba lagi...\n")
                                await asyncio.sleep(300)  # Tunggu 5 menit sebelum mencoba lagi
                            else:
                                print(f" Tidak ada tindakan untuk absen pada kelas {course_name}.")
                                break  # Hentikan loop jika tidak ada tindakan
        else:
            print(f"Kelas {course_name} belum dimulai. Menunggu waktu yang sesuai...\n")

# Fungsi untuk masuk ke kelas dan melakukan absen
async def join_and_attend_class(session, join_class_url, course_name):
    async with session.get(join_class_url, ssl=False) as join_response:
        if join_response.status == 200:
            join_text = await join_response.text()
            join_soup = BeautifulSoup(join_text, "html.parser")

            # Cek apakah absen belum dimulai
            not_started_button = join_soup.find("button", class_="btn btn-danger btn-rounded left mt-4")
            if not_started_button and "Belum Mulai" in not_started_button.text:
                print(f"Absen belum dimulai untuk kelas {course_name}. Menunggu 5 menit...\n")
                await asyncio.sleep(300)  # Tunggu 5 menit dan ulangi
                return "Absen belum dimulai"

            # Cek apakah absen sudah selesai
            attendance_form = join_soup.find("form", action="/komentar-mhs")
            if attendance_form:
                print(f"Absen sudah selesai untuk kelas {course_name}. Pengecekan akan dilakukan setiap 1 jam.\n")
                return "Absen sudah selesai"

            # Lakukan proses kehadiran setelah pengecekan form
            token_input = join_soup.find("input", {"name": "_token"})
            pertemuan_input = join_soup.find("input", {"name": "pertemuan"})
            id_input = join_soup.find("input", {"name": "id"})

            if token_input and pertemuan_input and id_input:
                token = token_input.get("value")
                pertemuan = pertemuan_input.get("value")
                id = id_input.get("value")

                # Tandai kehadiran
                attendance_result = await mark_attendance(session, token, pertemuan, id)
                print(attendance_result)
                return attendance_result

    # Jika tidak ada kondisi yang terpenuhi, kembalikan nilai default
    return "Tidak ada tindakan untuk absen"

# Fungsi utama untuk menavigasi ke kehadiran
async def navigate_to_attendance(session):
    try:
        print("--- Jadwal Hari Ini ---")
        async with session.get(SCHEDULE_URL, ssl=False) as schedule_response:
            if schedule_response.status != 200:
                print(f" Gagal mengakses jadwal. Status: {schedule_response.status}")
                return "Gagal mengakses jadwal."

            schedule_text = await schedule_response.text()
            schedule_soup = BeautifulSoup(schedule_text, "html.parser")

            classes = schedule_soup.find_all("div", class_="pricing-plan")
            print(f" {len(classes)} kelas ditemukan.")
            current_time = datetime.now()

            today_classes = process_classes(classes, current_time)
            display_today_schedule(today_classes)

            if today_classes:
                await monitor_and_attend_classes(session, classes, today_classes)
                return "Absen selesai untuk kelas hari ini."
            else:
                return "Tidak ada jadwal untuk hari ini."
    except aiohttp.ClientError as e:
        print(f" Error accessing attendance: {e}")
        return f"Error accessing attendance: {str(e)}"

# Fungsi untuk menjadwalkan pemeriksaan kehadiran setiap 5 menit jika kelas sudah dekat, jika tidak setiap 1 jam
async def schedule_attendance_check():
    async with aiohttp.ClientSession() as session:
        last_status = None  # Menyimpan status terakhir untuk menghindari duplikasi output

        while True:
            print(" Memulai pengecekan jadwal. ")
            ongoing_classes = await login_to_site(session)  # Pastikan login dilakukan di sini

            # Tangani jika ongoing_classes adalah string (status atau error)
            if isinstance(ongoing_classes, str):
                if ongoing_classes != last_status:
                    print(f" Status: {ongoing_classes}")
                    last_status = ongoing_classes
                print(" Pengecekan berikutnya akan dilakukan dalam 1 jam.")
                await asyncio.sleep(3600)  # Tunggu 1 jam sebelum pengecekan berikutnya
                continue

            # Tangani jika ongoing_classes adalah daftar kelas
            current_time = datetime.now()
            soon_classes = [
                course_name for course_name, start_time, end_time in ongoing_classes
                if current_time <= start_time <= current_time + timedelta(minutes=30)
            ]

            if soon_classes:
                print(f" Berikut kelas yang akan dimulai dalam 30 menit: {', '.join(soon_classes)}")
                await asyncio.sleep(1800)  # Tunggu 30 menit untuk pengecekan berikutnya
            else:
                print(" Tidak ada kelas yang akan dimulai dalam 30 menit. Menunggu 1 jam.")
                await asyncio.sleep(3600)  # Tunggu 1 jam sebelum pengecekan berikutnya

# Menjalankan aplikasi
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-update":
        update_program()
    else:
        asyncio.run(schedule_attendance_check())
    asyncio.run(schedule_attendance_check())
