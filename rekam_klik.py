import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def jalankan_perekam():
    print("Menyiapkan Perekam Klik WhatsApp Web...")
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    
    chrome_options = Options()
    chrome_options.binary_location = "/data/data/com.termux/files/usr/bin/chromium-browser"
    
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(executable_path="/data/data/com.termux/files/usr/bin/chromedriver")

    try:
        os.environ["DISPLAY"] = ":1" 
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Membuka WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        input("Tekan ENTER di sini JIKA WHATSAPP WEB SUDAH TERBUKA SEMPURNA di VNC...")

        # Kode JavaScript untuk merekam setiap klik
        js_injector = """
        window.recordedXPaths = [];
        document.addEventListener('click', function(e) {
            var getXPath = function(node) {
                if (node.id !== '') {
                    return '//*[@id="' + node.id + '"]';
                }
                if (node === document.body) {
                    return node.tagName.toLowerCase();
                }
                var nodeCount = 0;
                var childNodes = node.parentNode.childNodes;
                for (var i = 0; i < childNodes.length; i++) {
                    var currentNode = childNodes[i];
                    if (currentNode === node) {
                        return getXPath(node.parentNode) + '/' + node.tagName.toLowerCase() + '[' + (nodeCount + 1) + ']';
                    }
                    if (currentNode.nodeType === 1 && currentNode.tagName.toLowerCase() === node.tagName.toLowerCase()) {
                        nodeCount++;
                    }
                }
            };
            
            // Tangkap elemen yang diklik dan elemen di atasnya (parent) untuk jaga-jaga
            var path = getXPath(e.target);
            var parentPath = e.target.parentElement ? getXPath(e.target.parentElement) : 'Tidak ada parent';
            
            var result = {
                tag: e.target.tagName,
                text: e.target.innerText ? e.target.innerText.substring(0, 30) : '', // Ambil sedikit teksnya
                xpath: path,
                parent_xpath: parentPath
            };
            window.recordedXPaths.push(result);
        }, true);
        """
        
        print("Menyuntikkan alat perekam ke browser...")
        driver.execute_script(js_injector)
        
        print("\n" + "="*50)
        print("PEREKAM AKTIF! Silakan kembali ke VNC.")
        print("Lakukan simulasi pengiriman ke Channel (Klik pencarian, klik nama channel, klik kotak pesan).")
        print("Tekan CTRL+C di terminal ini untuk berhenti.")
        print("="*50 + "\n")
        
        jumlah_terekam_sebelumnya = 0
        
        # Looping terus menerus untuk mengambil data klik dari browser
        while True:
            # Ambil data dari variabel JavaScript
            recorded_data = driver.execute_script("return window.recordedXPaths;")
            
            if len(recorded_data) > jumlah_terekam_sebelumnya:
                for i in range(jumlah_terekam_sebelumnya, len(recorded_data)):
                    data = recorded_data[i]
                    print(f"\n[KLIK TERDETEKSI]")
                    print(f"Elemen : {data['tag']}")
                    teks_elemen = data['text'].replace('\n', ' ')
                    if teks_elemen.strip():
                        print(f"Teks   : {teks_elemen}...")
                    print(f"XPath  : {data['xpath']}")
                    print(f"Parent : {data['parent_xpath']}")
                    print("-" * 30)
                
                jumlah_terekam_sebelumnya = len(recorded_data)
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nPerekaman dihentikan oleh pengguna.")
        driver.quit()
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    jalankan_perekam()
