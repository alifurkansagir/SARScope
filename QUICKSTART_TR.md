# SarScope Hızlı Başlangıç Rehberi

## Kurulum (macOS/Linux)

### 1. Proje dizinine gidin
```bash
cd /Users/alifurkansagir/Desktop/sartech/sarscope
```

### 2. Kurulum betiğini çalıştırın
```bash
chmod +x install.sh
./install.sh
```

Veya manuel olarak:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## SarScope'u Çalıştırma

```bash
# Sanal ortamın aktif olduğundan emin olun
source venv/bin/activate

# Uygulamayı başlatın
python sarscope/main.py
```

## İlk Adımlar

### Ürün Ekleyin
1. Menüden **3** seçeneğini seçin
2. Ürün detaylarını doldurun:
   - Ad: örneğin "Kablosuz Kulaklık"
   - SKU: örneğin "KK-001"
   - Satış Fiyatı: örneğin 79.99
   - Minimum Fiyat: örneğin 50.00
   - Maliyet: örneğin 30.00
   - Hedef Kar Marjı: örneğin 50

3. Rakip URL'lerini ekleyin:
   - Benzer ürünleri satan rakip sitelerinin linklerini girin
   - Örnek: "https://amazon.com/dp/B0XXXXXX"

### Fiyatları İzleyin
1. Menüden **1** seçeneğini seçin (Fiyat Devriyesi)
2. Sistem şunları yapacak:
   - Rakip fiyatlarını getir
   - Senin fiyatınla karşılaştır
   - Fiyat önerilerini sun
   - Fırsatları göster

### Trendleri Keşfedin
1. Menüden **2** seçeneğini seçin (Trend Avcısı)
2. Tarayacak bir kategori URL'si girin
3. Yeni fırsatları görüntüleyin:
   - Envanterinde olmayan ürünler
   - Satış hızı tahmini
   - Bulanık eşleştirme skorları

### Raporu Görüntüleyin
1. Menüden **4** seçeneğini seçin
2. Şunları göreceksiniz:
   - Kontrol paneli istatistikleri
   - Ürün izleme listesi
   - Fiyat önerileri

## Yaygın Görevler

### Rakip Fiyatlarını Kontrol Edin
```
Menü → Seçenek 1 → Fiyat Devriyesi
```

### Pazar Fırsatlarını Bulun
```
Menü → Seçenek 2 → Trend Avcısı
```

### Yeni Ürün İzlemeye Ekleyin
```
Menü → Seçenek 3 → Ürün Ekle
```

### Verileri Dışa Aktarın

Ürünler SQLite veritabanında saklanır: `sarscope.db`

Yedek almak için:
```bash
cp sarscope/sarscope.db sarscope/sarscope_yedek_$(date +%Y%m%d).db
```

## Programlı Kullanım

```python
from sarscope.database import DatabaseManager
from sarscope.core.scraper import SarScopeScraper

# Başlat
db = DatabaseManager()
scraper = SarScopeScraper()

# Tüm ürünleri al
urunler = db.get_all_products()
for urun in urunler:
    print(f"{urun.name}: ${urun.my_price:.2f}")

# Fiyat getir
fiyat = scraper.fetch_price("https://rakip.com/urun")
print(f"Rakip fiyatı: ${fiyat:.2f}")

# İstatistikleri al
istatistikler = db.get_dashboard_stats()
print(f"Toplam ürün: {istatistikler['total_products']}")
```

## Özelleştirme

### Fiyatlandırma Stratejisini Değiştirin
`sarscope/config.py` dosyasını düzenleyin:
```python
UNDERCUTTING_MARGIN = 2.0  # 1 dolar yerine 2 dolar az sat
```

### Algılanmayı Önle Ayarlarını Değiştirin
```python
MIN_DELAY = 5  # Daha uzun gecikmeler
MAX_DELAY = 10
```

### Bulanık Eşleştirme Hassasiyetini Değiştirin
```python
FUZZY_MATCH_THRESHOLD = 75  # Daha düşük = daha esnek eşleştirme
```

## Günlük Dosya

Günlük dosyasını şuradan kontrol edin: `sarscope/sarscope.log`

Canlı günlükleri görüntüleyin:
```bash
tail -f sarscope/sarscope.log
```

## Sorun Giderme

### İçe Aktarma Hatası
```
ModuleNotFoundError: No module named 'requests'
```
Çözüm:
```bash
pip install -r requirements.txt
```

### Veritabanı Hatası
```
sqlite3.OperationalError: database is locked
```
Çözüm:
```bash
rm sarscope/sarscope.db  # Veritabanını sıfırla
python sarscope/main.py  # Yeniden başlat
```

### Site Engelleme
- `config.py` dosyasındaki gecikmeleri artırın
- Farklı kullanıcı ajanı eklemeyi deneyin
- Sitenin `robots.txt` dosyasında kazıma izni olup olmadığını kontrol edin

## İpuçları ve En İyi Uygulamalar

✅ **Yapılacaklar**
- Her ürüne birden fazla rakip URL'si ekleyin
- Fiyat Devriyesini düzenli olarak çalıştırın (günde bir defa önerilir)
- Marjları yakından izleyin
- Trendleri haftalık gözden geçirin

❌ **Yapılmayacaklar**
- Minimum fiyatı maliyetin altına ayarlamayın
- Kazımayı engelleyen siteleri kazımayın
- Aynı anda birden fazla örnek çalıştırmayın
- 3 saniyeden az gecikmeler kullanmayın

## Performans

- **Tipik Fiyat Kontrolü**: Rakip başına 2-5 saniye
- **Trend Taraması**: Kategori başına 10-30 saniye
- **Bulanık Eşleştirme**: Yüzlerce ürün için <1 saniye

## Sonraki Adımlar

1. Ürün envanterinizi ekleyin
2. Rakip URL'lerini ekleyin
3. Taban fiyatını belirlemek için Fiyat Devriyesini çalıştırın
4. Pazarları trendler için tarayın
5. Fırsatlar raporunu gözden geçirin
6. Fiyatı otomatik olarak ayarlayın

---

Daha ayrıntılı dokümantasyon için [README_TR.md](README_TR.md) dosyasına bakın
