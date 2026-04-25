import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def setup_whatsapp_session():
    print("Menyiapkan konfigurasi Chrome untuk VNC...")
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    
    chrome_options = Options()
    chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
    
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # User agent Windows agar WA Web tidak mendeteksi browser mobile/lama
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(executable_path="/data/data/com.termux/files/usr/bin/chromedriver")

    try:
        print("Mencoba membuka browser di display :1...")
        # Kita paksa gunakan display :1 dari dalam script
        os.environ["DISPLAY"] = ":1"
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Membuka WhatsApp Web...")
        driver.get("https://web.whatsapp.com")
        
        print("\n[INFO] Menunggu WhatsApp Web termuat sempurna (Timeout 5 menit)...")
        try:
            wait = WebDriverWait(driver, 300)
            wait.until(EC.presence_of_element_located((By.XPATH, '//canvas | //div[@id="pane-side"]')))
        except:
            pass

        print("\n=============================================")
        print("Browser SEHARUSNYA sudah muncul di VNC.")
        print("Silakan SCAN QR Code.")
        print("Jika sudah login, tekan ENTER di terminal ini.")
        print("=============================================\n")
        
        input("Tekan ENTER jika sudah login...")
        
        driver.quit()
        print("Sesi disimpan.")
        
    except Exception as e:
        print(f"\n[ERROR] Gagal: {e}")

if __name__ == "__main__":
    setup_whatsapp_session()
