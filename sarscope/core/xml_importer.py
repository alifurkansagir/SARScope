import requests
import xml.etree.ElementTree as ET

class XMLImporter:
    def __init__(self, xml_url):
        self.xml_url = xml_url
        # IdeaSoft'un Cimri için kullandığı Özel Namespace Kilidi
        self.ns = {'c': 'http://www.cimri.com/schema/merchant/upload'}

    def fetch_data(self):
        print(f"📥 XML indiriliyor: {self.xml_url}")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.xml_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Hata: Linke ulaşılamadı! Kod: {response.status_code}")
                return []

            print("✅ XML indirildi, ürünler ayrıştırılıyor...")
            
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError:
                print("❌ Hata: XML bozuk veya okunamadı.")
                return []
            
            products = []
            count = 0
            
            # Namespace kullanarak "MerchantItem"ları bul (Derinlemesine arama)
            items = root.findall('.//c:MerchantItem', self.ns)
            
            print(f"📦 Toplam {len(items)} adet ham veri bulundu. İşleniyor...")

            for item in items:
                try:
                    # 1. İsim (itemTitle)
                    name_el = item.find('c:itemTitle', self.ns)
                    name = name_el.text if name_el is not None else "İsimsiz Ürün"
                    
                    # 2. Stok Kodu (merchantItemId)
                    sku_el = item.find('c:merchantItemId', self.ns)
                    sku = sku_el.text if sku_el is not None else "NO-SKU"

                    # 3. Fiyat (pricePlusTax - En önemli kısım!)
                    price_el = item.find('c:pricePlusTax', self.ns)
                    # Eğer satış fiyatı yoksa EFT fiyatına bak
                    if price_el is None:
                        price_el = item.find('c:priceEft', self.ns)

                    if price_el is None or not price_el.text:
                        continue # Fiyatı olmayan ürünü atla

                    price = float(price_el.text.replace(',', '.'))
                    
                    # 4. Link (itemUrl)
                    link_el = item.find('c:itemUrl', self.ns)
                    link = link_el.text if link_el is not None else ""

                    # 5. Marka (brand)
                    brand_el = item.find('c:brand', self.ns)
                    brand = brand_el.text if brand_el is not None else ""
                    
                    # Listeye ekle
                    products.append({
                        'sku': sku,
                        'name': name,
                        'my_price': price,
                        'url': link,
                        'brand': brand
                    })
                    count += 1
                    
                except Exception as e:
                    # print(f"Ürün atlandı: {e}")
                    continue

            print(f"🎉 BÜYÜK BAŞARI! {count} adet ürün SarScope'a uygun hale getirildi.")
            return products

        except Exception as e:
            print(f"❌ Kritik Hata: {e}")
            return []

if __name__ == "__main__":
    # SENİN LİNKİN (Otomatik ekledim)
    test_link = "https://www.ultrahirdavat.com/output/7200631009.xml"
    
    importer = XMLImporter(test_link)
    data = importer.fetch_data()
    
    # Test için ilk 5 ürünü gösterelim
    if data:
        print("\n--- ÖRNEK ÜRÜNLER (İlk 5) ---")
        for p in data[:5]:
            print(f"Ürün:  {p['name']}")
            print(f"Marka: {p['brand']}")
            print(f"Fiyat: {p['my_price']} TL")
            print("-" * 30)