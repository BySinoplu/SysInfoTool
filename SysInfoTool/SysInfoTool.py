import os
import platform
import psutil
import time
import socket
import datetime
import matplotlib.pyplot as plt
from collections import deque
import curses

# Sistem bilgilerini toplama fonksiyonları
def sistem_bilgileri():
    """Sistemle ilgili temel bilgileri döndürür."""
    bilgi = {
        "İşletim Sistemi": platform.system(),
        "Bilgisayar Adı": platform.node(),
        "Sürüm": platform.release(),
        "Makine Tipi": platform.machine(),
        "İşlemci": platform.processor(),
    }
    return bilgi

def cpu_bilgileri():
    """CPU kullanım ve çekirdek bilgilerini döndürür."""
    bilgi = {
        "Fiziksel Çekirdekler": psutil.cpu_count(logical=False),
        "Toplam Çekirdekler": psutil.cpu_count(logical=True),
        "Güncel Frekans (MHz)": psutil.cpu_freq().current,
        "CPU Kullanımı (%)": psutil.cpu_percent(interval=1),
    }
    return bilgi

def bellek_bilgileri():
    """Bellek kullanım bilgilerini döndürür."""
    bellek = psutil.virtual_memory()
    bilgi = {
        "Toplam Bellek": bellek.total,
        "Kullanılabilir Bellek": bellek.available,
        "Kullanılan Bellek": bellek.used,
        "Bellek Kullanımı (%)": bellek.percent,
    }
    return bilgi

def disk_bilgileri():
    """Disk kullanım bilgilerini döndürür."""
    bölümler = psutil.disk_partitions()
    bilgi = []
    for bölüm in bölümler:
        kullanım = psutil.disk_usage(bölüm.mountpoint)
        bilgi.append({
            "Cihaz": bölüm.device,
            "Bağlama Noktası": bölüm.mountpoint,
            "Dosya Sistemi": bölüm.fstype,
            "Toplam Alan": kullanım.total,
            "Kullanılan": kullanım.used,
            "Boş": kullanım.free,
            "Kullanım Oranı (%)": kullanım.percent,
        })
    return bilgi

def ağ_bilgileri():
    """Ağ bilgilerini döndürür."""
    hostname = socket.gethostname()
    ip_adresi = socket.gethostbyname(hostname)
    ağ_io = psutil.net_io_counters()
    bilgi = {
        "Bilgisayar Adı": hostname,
        "IP Adresi": ip_adresi,
        "Gönderilen Veri (B)": ağ_io.bytes_sent,
        "Alınan Veri (B)": ağ_io.bytes_recv,
    }
    return bilgi

def sistem_baslangic_suresi():
    """Sistem başlangıç süresini döndürür."""
    boot_time = psutil.boot_time()
    boot_datetime = datetime.datetime.fromtimestamp(boot_time)
    bilgi = {
        "Başlangıç Zamanı": boot_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "Çalışma Süresi": str(datetime.datetime.now() - boot_datetime).split('.')[0]
    }
    return bilgi

def işlemleri_listele():
    """Çalışan işlemleri listeleyerek kullanıcıya gösterir."""
    işlem_listesi = []
    for işlem in psutil.process_iter(['pid', 'name', 'username']):
        işlem_listesi.append(işlem.info)
    return işlem_listesi

def işlem_sonlandır(pid):
    """Belirtilen PID'ye sahip işlemi sonlandırır."""
    try:
        işlem = psutil.Process(pid)
        işlem.terminate()
        işlem.wait()
        return True
    except Exception as e:
        return False

def disk_performansi():
    """Disk okuma ve yazma performansını döndürür."""
    disk_io = psutil.disk_io_counters()
    bilgi = {
        "Okunan Veri (B)": disk_io.read_bytes,
        "Yazılan Veri (B)": disk_io.write_bytes,
        "Okuma Sayısı": disk_io.read_count,
        "Yazma Sayısı": disk_io.write_count,
    }
    return bilgi

def cpu_kayıt(interval=1, süre=20):
    """CPU kullanımını belirtilen süre boyunca kaydeder."""
    log = []
    başlangıç_zamanı = time.time()
    while time.time() - başlangıç_zamanı < süre:
        kullanım = psutil.cpu_percent(interval=interval)
        log.append((datetime.datetime.now(), kullanım))
    return log

def cpu_grafik(log):
    """Kaydedilen CPU kullanımını çizer."""
    zamanlar = [kayıt[0] for kayıt in log]
    kullanımlar = [kayıt[1] for kayıt in log]
    plt.figure(figsize=(10, 5))
    plt.plot(zamanlar, kullanımlar, marker='o')
    plt.title("CPU Kullanımı Zamanla")
    plt.xlabel("Zaman")
    plt.ylabel("CPU Kullanımı (%)")
    plt.grid()
    plt.show()

def bilgi_göster(stdscr, başlık, veri):
    """Bilgileri terminalde curses kullanarak gösterir."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    try:
        stdscr.addstr(0, 0, başlık, curses.A_BOLD)
        for idx, (anahtar, değer) in enumerate(veri.items(), start=2):
            if idx >= max_y - 2:
                stdscr.addstr(max_y - 1, 0, "Çıkmak için bir tuşa basın...")
                break
            if isinstance(değer, int) and "Bellek" in anahtar:
                değer = f"{değer / (1024 ** 3):.2f} GB"
            elif isinstance(değer, int) and "Veri" in anahtar:
                değer = f"{değer / (1024 ** 2):.2f} MB"
            stdscr.addstr(idx, 0, f"{anahtar}: {değer}")
        stdscr.addstr(idx + 2, 0, "Menüye dönmek için bir tuşa basın...")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()

def disk_bilgisi_göster(stdscr, başlık, diskler):
    """Disk bilgilerini curses kullanarak ayrı ayrı gösterir."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    satır = 2
    try:
        stdscr.addstr(0, 0, başlık, curses.A_BOLD)
        for disk in diskler:
            for anahtar, değer in disk.items():
                if satır >= max_y - 2:
                    stdscr.addstr(max_y - 1, 0, "Çıkmak için bir tuşa basın...")
                    break
                if isinstance(değer, int):
                    değer = f"{değer / (1024 ** 3):.2f} GB"
                stdscr.addstr(satır, 0, f"{anahtar}: {değer}")
                satır += 1
            stdscr.addstr(satır, 0, "-" * 40)
            satır += 1
        stdscr.addstr(satır + 1, 0, "Menüye dönmek için bir tuşa basın...")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()

def işlem_göster(stdscr, başlık, işlemler):
    """Çalışan işlemleri curses ile gösterir."""
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    satır = 2
    try:
        stdscr.addstr(0, 0, başlık, curses.A_BOLD)
        for işlem in işlemler:
            if satır >= max_y - 2:
                stdscr.addstr(max_y - 1, 0, "Çıkmak için bir tuşa basın...")
                break
            işlem_bilgi = f"PID: {işlem['pid']} - Ad: {işlem['name']} - Kullanıcı: {işlem['username']}"
            stdscr.addstr(satır, 0, işlem_bilgi)
            satır += 1
        stdscr.addstr(satır + 1, 0, "Menüye dönmek için bir tuşa basın...")
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()

def ana_menü(stdscr):
    """Ana menü döngüsü curses kullanılarak."""
    k = 0
    while k != ord('0'):
        stdscr.clear()
        stdscr.addstr(0, 0, "Sistem Bilgi Menüsü", curses.A_BOLD)
        stdscr.addstr(2, 0, "1. Sistem Bilgilerini Göster")
        stdscr.addstr(3, 0, "2. CPU Bilgilerini Göster")
        stdscr.addstr(4, 0, "3. Bellek Bilgilerini Göster")
        stdscr.addstr(5, 0, "4. Disk Bilgilerini Göster")
        stdscr.addstr(6, 0, "5. Ağ Bilgilerini Göster")
        stdscr.addstr(7, 0, "6. CPU Kullanım Grafiği(10 15 saniye bekleyiniz)")
        stdscr.addstr(8, 0, "7. Çalışan İşlemleri Göster")
        stdscr.addstr(9, 0, "8. Sistem Başlangıç Süresi")
        stdscr.addstr(10, 0, "9. Disk Performansı")
        stdscr.addstr(11, 0, "0. Çıkış")
        stdscr.addstr(13, 0, "Bir seçim yapın (0-9):")
        stdscr.refresh()

        k = stdscr.getch()

        if k == ord('1'):
            sistem = sistem_bilgileri()
            bilgi_göster(stdscr, "Sistem Bilgileri", sistem)
        elif k == ord('2'):
            cpu = cpu_bilgileri()
            bilgi_göster(stdscr, "CPU Bilgileri", cpu)
        elif k == ord('3'):
            bellek = bellek_bilgileri()
            bilgi_göster(stdscr, "Bellek Bilgileri", bellek)
        elif k == ord('4'):
            diskler = disk_bilgileri()
            disk_bilgisi_göster(stdscr, "Disk Bilgileri", diskler)
        elif k == ord('5'):
            ağ = ağ_bilgileri()
            bilgi_göster(stdscr, "Ağ Bilgileri", ağ)
        elif k == ord('6'):
            log = cpu_kayıt()
            cpu_grafik(log)
        elif k == ord('7'):
            işlemler = işlemleri_listele()
            işlem_göster(stdscr, "Çalışan İşlemler", işlemler)
        elif k == ord('8'):
            başlangıç = sistem_baslangic_suresi()
            bilgi_göster(stdscr, "Sistem Başlangıç Süresi", başlangıç)
        elif k == ord('9'):
            performans = disk_performansi()
            bilgi_göster(stdscr, "Disk Performansı", performans)

def main():
    curses.wrapper(ana_menü)

if __name__ == "__main__":
    main()
