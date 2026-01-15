import os
import sys

# Proje ana dizinini path'e ekle ki modülleri bulabilsin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sarscope.core.notifier import NotificationManager

def test_mail_gonder():
    print("🚀 Test maili gönderimi başlatılıyor...")
    
    try:
        # NotificationManager'ı başlat
        notifier = NotificationManager()
        
        # Test verileri
        urun_adi = "TEST ÜRÜNÜ (Manuel Kontrol)"
        bizim_fiyat = 100.0
        rakip_fiyat = 95.0
        link = "https://www.google.com"
        
        print(f"📨 Alıcı adresi: {notifier.recipient_email}")
        
        # Gönder
        notifier.send_alert(urun_adi, bizim_fiyat, rakip_fiyat, link)
        
        print("\n✅ Test maili başarıyla gönderildi! Lütfen gelen kutunuzu (ve spam klasörünü) kontrol edin.")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        print("Lütfen 'sarscope/core/notifier.py' dosyasındaki e-posta ayarlarını ve uygulama şifresini kontrol edin.")

if __name__ == "__main__":
    test_mail_gonder()