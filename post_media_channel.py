import os
import time
import json
import sys
import random
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HISTORY_FILE = "uploaded_history_wa.txt"

def check_internet():
    try:
        # Ping Google DNS
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], timeout=5, stderr=subprocess.STDOUT)
        return True
    except:
        return False

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(file_path):
    with open(HISTORY_FILE, "a") as f:
        f.write(file_path + "\n")

def post_media_to_channel(channel_name, file_path, caption, headless=False):
    is_scan_mode = (channel_name == "SCAN_MODE")
    print(f"\n[PROCESS] Memulai upload: {os.path.basename(file_path)}")
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    chrome_options = Options()
    chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
    
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1280,720")
    else:
        os.environ["DISPLAY"] = ":1" 

    service = Service(executable_path="/data/data/com.termux/files/usr/bin/chromedriver")
    driver = None

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 30)
        
        driver.get("https://web.whatsapp.com/")
        print("Menunggu WhatsApp Web terbuka (Sabar, timeout 5 menit)...")

        # Tunggu sampai elemen dashboard utama muncul
        wait_long = WebDriverWait(driver, 300)
        try:
            wait_long.until(EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"] | //button[@aria-label="Saluran"] | //span[@data-icon="newsletter-outline"]')))
            print("WhatsApp Web siap.")
        except:
            print("[PERINGATAN] Loading sangat lama, mencoba tetap melanjutkan...")
        
        # 1. Klik ikon Channel di sidebar
        xpaths = [
            '//button[@aria-label="Saluran"]',
            '//button[@title="Saluran"]',
            '//span[@data-icon="newsletter-outline"]/ancestor::button'
        ]
        
        channel_tab = None
        for xp in xpaths:
            try:
                channel_tab = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xp)))
                break
            except: continue
                
        if not channel_tab:
            raise Exception("Tombol Saluran tidak ditemukan.")
            
        channel_tab.click()
        time.sleep(3)

        if is_scan_mode:
            print("Memindai daftar channel...")
            scanned_channels = driver.execute_script("""
                let results = [];
                let items = document.querySelectorAll('div[role="listitem"]');
                for (let item of items) {
                    let text = item.innerText || "";
                    if (text.includes("Saluran untuk diikuti") || text.includes("Find channels")) break;
                    let titleEl = item.querySelector('span[title]');
                    if (titleEl) { results.push(titleEl.getAttribute('title')); }
                }
                return [...new Set(results)].filter(n => n.trim() !== "");
            """)
            
            if scanned_channels:
                with open("channels.txt", "w") as f:
                    f.write("\n".join(scanned_channels))
                print(f"Database diperbarui! {len(scanned_channels)} channel disimpan.")
                print("\n=== PILIH CHANNEL TUJUAN ===")
                for i, name in enumerate(scanned_channels, 1):
                    print(f"[{i}] {name}")
                print("===========================")
                choice = input(f"Pilih nomor (1-{len(scanned_channels)}) [Default: 1]: ").strip()
                idx = int(choice) - 1 if choice.isdigit() and 0 < int(choice) <= len(scanned_channels) else 0
                channel_name = scanned_channels[idx]
            else:
                raise Exception("Tidak ada channel terdeteksi.")

        # 2. Klik Nama Channel
        print(f"Mencari Channel '{channel_name}'...")
        clean_name = channel_name.replace(".", "").strip()
        channel_xpath = f'//span[contains(text(), "{clean_name}")]'
        target_channel = wait.until(EC.element_to_be_clickable((By.XPATH, channel_xpath)))
        driver.execute_script("arguments[0].scrollIntoView();", target_channel)
        target_channel.click()
        
        wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="main"]//header//span[contains(text(), "{clean_name}")]')))
        time.sleep(2)

        # 3. Inject JS Interceptor & Buka Menu Lampirkan
        driver.execute_script("""
            window._realCreateElement = document.createElement;
            document.createElement = function(tag) {
                var el = window._realCreateElement.call(document, tag);
                if (tag.toLowerCase() === 'input') {
                    el.click = function() { console.log('OS dialog dicegah!'); };
                    el.style.display = 'block';
                    el.style.opacity = '0';
                    el.style.position = 'absolute';
                    el.style.zIndex = '-1';
                    document.body.appendChild(el);
                }
                return el;
            };
        """)
        
        attach_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Lampirkan"] | //span[@data-icon="plus-rounded"]/ancestor::button')))
        driver.execute_script("arguments[0].click();", attach_btn)
        time.sleep(1) 
        
        photo_video = wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Foto & Video")]')))
        driver.execute_script("arguments[0].click();", photo_video)
        time.sleep(2) 
            
        file_inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//input[@type="file"]')))
        uploaded = False
        is_video = file_path.lower().endswith('.mp4')

        for inp in file_inputs:
            accept_attr = (inp.get_attribute("accept") or "").lower()
            if is_video and "video/mp4" in accept_attr:
                inp.send_keys(file_path)
                uploaded = True; break
            elif not is_video and "image/" in accept_attr and "video/mp4" in accept_attr:
                inp.send_keys(file_path)
                uploaded = True; break
                    
        if not uploaded:
            for inp in file_inputs[1:]:
                inp.send_keys(file_path)
                uploaded = True; break

        if not uploaded: raise Exception("Gagal suntik file.")

        print("Menunggu preview media (10 detik)...")
        time.sleep(10) 

        print("Mengetik dan memasang caption...")
        try:
            active_element = driver.switch_to.active_element
            
            # Pisahkan kalimat pertama dan sisanya
            parts = caption.split('. ', 1)
            first_sentence = parts[0] + ('.' if len(parts) > 1 else '')
            remaining_text = parts[1] if len(parts) > 1 else ""

            # 1. Tulis kalimat pertama secara normal
            print(f"Mengetik: {first_sentence[:50]}...")
            active_element.send_keys(first_sentence)
            time.sleep(2)

            # 2. Paste sisanya menggunakan JS jika ada
            if remaining_text:
                print("Menempelkan sisa teks (Paste mode)...")
                driver.execute_script("""
                    var target = arguments[0];
                    target.focus();
                    document.execCommand('insertText', false, ' ' + arguments[1]);
                """, active_element, remaining_text)
            
            print("Menunggu 5 detik agar sistem memproses teks...")
            time.sleep(5)
            
            print("Mengirim dengan tombol ENTER...")
            active_element.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"Gagal memasang caption: {e}")
        
        wait_final = WebDriverWait(driver, 60)
        print("Mengirim... Menunggu panel preview tertutup...")
        wait_final.until(EC.invisibility_of_element_located((By.XPATH, '//span[@data-icon="send"]')))
        
        time.sleep(5) 
        print("Memastikan upload selesai...")
        try:
            wait_final.until(EC.invisibility_of_element_located((By.XPATH, '//span[@data-icon="msg-time"]')))
            print("Upload selesai!")
            save_to_history(file_path) # Simpan ke riwayat sukses
            success = True
        except:
            print("Peringatan: Status upload tidak terpantau.")
            success = False
            
        time.sleep(3) 
        print("Selesai.")
        driver.quit()
        return success

    except Exception as e:
        print(f"\n[ERROR] {e}")
        if driver: driver.quit()
        return False

def get_files_with_captions(root_path):
    results = []
    if not os.path.exists(root_path): return results
    items = sorted(os.listdir(root_path))
    
    for item in items:
        item_path = os.path.join(root_path, item)
        if os.path.isdir(item_path):
            sub_items = os.listdir(item_path)
            media_files = [s for s in sub_items if s.lower().endswith(('.mp4', '.jpg', '.jpeg', '.png'))]
            media_files.sort(key=lambda x: 0 if x.lower().endswith('.mp4') else 1)
            
            if media_files:
                video_file = os.path.join(item_path, media_files[0])
                meta_file = os.path.join(item_path, "post_meta.json")
                caption = ""
                
                # Gunakan summary atau post_title dari json jika ada
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, 'r') as f:
                            meta_data = json.load(f)
                            caption = meta_data.get("summary", "").strip()
                            if not caption:
                                caption = meta_data.get("post_title", "").strip()
                    except:
                        pass
                
                # Fallback ke nama file jika summary kosong/tidak ada
                if not caption:
                    nama_file = os.path.basename(video_file)
                    nama_tanpa_ext = os.path.splitext(nama_file)[0]
                    caption = nama_tanpa_ext.replace('_', ' ').replace('-', ' ')
                
                results.append({"path": video_file, "caption": caption, "display": f"{item} ({os.path.basename(video_file)})"})
        else:
            if item.lower().endswith(('.mp4', '.jpg', '.jpeg', '.png')):
                caption = os.path.splitext(item)[0].replace('_', ' ').replace('-', ' ')
                results.append({"path": item_path, "caption": caption, "display": item})
    return results

def countdown_timer(minutes):
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer = f'{mins:02d}:{secs:02d}'
        print(f"\r[WAIT] Menunggu {timer} sebelum posting berikutnya...", end="")
        time.sleep(1)
        seconds -= 1
    print("\r[READY] Memulai posting berikutnya...                          ")

if __name__ == "__main__":
    db_file = "channels.txt"
    history = load_history()
    
    print("\n=== POSTING WHATSAPP OTOMATIS ===")
    folder_path = input("Masukkan path folder konten: ").strip()
    if not os.path.exists(folder_path):
        print("Folder tidak ditemukan."); exit(1)

    print("\n[1] VNC Mode (Normal)\n[2] Headless Mode (Hemat RAM)")
    is_headless = (input("Pilih mode [Default: 1]: ").strip() == "2")

    # Pemilihan Channel
    channel_list = []
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            channel_list = [line.strip() for line in f if line.strip()]

    target_ch = "SCAN_MODE"
    if channel_list:
        print("\n=== DAFTAR CHANNEL ===")
        for i, name in enumerate(channel_list, 1):
            print(f"[{i}] {name}")
        print("[0] RE-SCAN")
        choice = input("Pilih nomor channel [Default: 1]: ").strip()
        if choice != "0":
            idx = int(choice) - 1 if choice.isdigit() and 0 < int(choice) <= len(channel_list) else 0
            target_ch = channel_list[idx]

    # Pemilihan File
    all_files = get_files_with_captions(folder_path)
    # Filter yang belum diupload
    pending_files = [f for f in all_files if f['path'] not in history]
    
    # Mengacak urutan file agar tidak berurutan abjad
    random.shuffle(pending_files)

    if not pending_files:
        print("\n[INFO] Semua file di folder ini sudah pernah diupload sebelumnya.")
        sys.exit(0)

    print(f"\nTerdeteksi {len(pending_files)} file baru yang belum diupload.")
    print("[1] Upload SATU file saja\n[2] Auto Upload SEMUA file baru")
    mode_upload = input("Pilih mode upload [1/2]: ").strip()

    if mode_upload == "2":
        try:
            interval = int(input("Masukkan jeda antar posting (menit) [Default: 5]: ") or 5)
        except: interval = 5
        
        print(f"\n[START] Memulai auto-upload {len(pending_files)} file dengan jeda {interval} menit...")
        for i, f in enumerate(pending_files):
            if i > 0:
                countdown_timer(interval)
            
            fail_count = 0
            while True:
                success = post_media_to_channel(target_ch, f['path'], f['caption'], headless=is_headless)
                if success:
                    break
                else:
                    if not check_internet():
                        print(f"\n[ERR] Internet terputus saat upload {os.path.basename(f['path'])}. Menunggu koneksi...")
                        while not check_internet():
                            time.sleep(10)
                        print("[OK] Internet kembali. Mencoba ulang upload ini...")
                        continue
                    else:
                        fail_count += 1
                        if fail_count >= 5:
                            print(f"\n[CRITICAL] Gagal 5 kali (bukan internet) pada {os.path.basename(f['path'])}. Berhenti.")
                            sys.exit(1)
                        print(f"\n[RETRY] Gagal ({fail_count}/5). Mencoba ulang dalam {interval} menit...")
                        countdown_timer(interval)
                        
        print("\n[FINISH] Semua file berhasil diproses.")
    else:
        # Mode satuan seperti biasa
        print("\n=== DAFTAR FILE PENDING ===")
        for i, data in enumerate(pending_files, 1):
            print(f"[{i}] {data['display']}")
        
        f_choice = input(f"Pilih nomor file (1-{len(pending_files)}) [Default: 1]: ").strip()
        f_idx = int(f_choice) - 1 if f_choice.isdigit() and 0 < int(f_choice) <= len(pending_files) else 0
        
        f = pending_files[f_idx]
        print(f"\nTarget: {target_ch}\nFile  : {f['path']}")
        if input("Lanjutkan? (y/n): ").lower() == 'y':
            fail_count = 0
            while True:
                success = post_media_to_channel(target_ch, f['path'], f['caption'], headless=is_headless)
                if success:
                    break
                else:
                    if not check_internet():
                        print("\n[ERR] Internet terputus. Menunggu koneksi...")
                        while not check_internet():
                            time.sleep(10)
                        print("[OK] Internet kembali. Mencoba ulang...")
                        continue
                    else:
                        fail_count += 1
                        if fail_count >= 5:
                            print("\n[CRITICAL] Gagal 5 kali. Berhenti.")
                            break
                        print(f"\n[RETRY] Gagal ({fail_count}/5). Mencoba lagi...")
                        time.sleep(10) # Jeda singkat untuk mode manual