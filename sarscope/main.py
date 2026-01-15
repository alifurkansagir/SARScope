import sys
import os
import time
from datetime import datetime

# Yol ayarı (GPS)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

# --- MODÜLLERİMİZ ---
from sarscope.core.scraper import SarScopeScraper
from sarscope.core.xml_importer import XMLImporter
from sarscope.core.excel_manager import export_to_excel, import_from_excel, save_trends_to_excel
from sarscope.core.trend_hunter import TrendHunter

# Notifier (WhatsApp) modülünü içe aktarmaya çalışıyoruz
# Eğer dosyayı oluşturmadıysan hata vermesin diye try-except koydum
try:
    from sarscope.core.notifier import NotificationManager
    HAS_NOTIFIER = True
except ImportError:
    HAS_NOTIFIER = False

class SarScopeApp:
    def __init__(self):
        self.console = Console()
        self.scraper = SarScopeScraper()
        
        # IdeaSoft XML Linkin
        self.xml_url = "https://www.ultrahirdavat.com/output/7200631009.xml"
        
        # Veri Dosyası Yolu
        self.data_file = os.path.join(current_dir, "data", "products.json")
        self.products = self.load_products()

        # Bildirim Yöneticisi (Varsa başlat)
        if HAS_NOTIFIER:
            self.notifier = NotificationManager()
        else:
            self.notifier = None

    def load_products(self):
        """Veritabanını yükler"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_products(self):
        """Veritabanını kaydeder"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, ensure_ascii=False, indent=4)

    def print_banner(self):
        self.console.clear()
        banner = """
   _____            _____                      
  / ____|          / ____|                     
 | (___   __ _ _ _| (___   ___ ___  _ __   ___ 
  \___ \ / _` | '__\___ \ / __/ _ \| '_ \ / _ \\
  ____) | (_| | |  ____) | (_| (_) | |_) |  __/
 |_____/ \__,_|_| |_____/ \___\___/| .__/ \___|
                                   | |         
                                   |_|         
        Created by SARTECH SOFTWARE
        """
        self.console.print(f"[bold cyan]{banner}[/bold cyan]")
        status = "WhatsApp Aktif ✅" if HAS_NOTIFIER else "WhatsApp Pasif ❌"
        self.console.print(f"[dim]v3.0 - Full Paket | {status}[/dim]\n")

    def sync_inventory(self):
        """IdeaSoft Entegrasyonu"""
        self.console.print(f"[bold yellow]🔄 IdeaSoft'a Bağlanılıyor...[/bold yellow]")
        importer = XMLImporter(self.xml_url)
        new_data = importer.fetch_data()
        
        if not new_data:
            self.console.print("[bold red]❌ Veri çekilemedi![/bold red]")
            input("\nDevam etmek için Enter...")
            return

        existing_map = {p.get('sku'): p for p in self.products}
        final_list = []
        updated_count = 0
        new_count = 0
        
        for item in new_data:
            sku = item['sku']
            if sku in existing_map:
                existing_product = existing_map[sku]
                existing_product.update({
                    'my_price': item['my_price'],
                    'name': item['name'],
                    'url': item['url'],
                    'brand': item.get('brand', '')
                })
                # Eski ayarları koru
                if 'competitor_url' not in existing_product:
                    existing_product['competitor_url'] = ""
                
                final_list.append(existing_product)
                updated_count += 1
            else:
                item['competitor_url'] = ""
                item['min_price'] = item['my_price'] * 0.90
                final_list.append(item)
                new_count += 1
        
        self.products = final_list
        self.save_products()
        self.console.print(f"[bold green]✅ {updated_count} güncellendi, {new_count} yeni eklendi.[/bold green]")
        input("\nDevam etmek için Enter...")

    def run_price_patrol(self):
        """Fiyat Takibi + WhatsApp Bildirimi"""
        self.products = self.load_products()
        targets = [p for p in self.products if p.get('competitor_url') and len(str(p['competitor_url'])) > 10]
        
        if not targets:
            self.console.print("[bold red]⚠️ Takip edilecek ürün yok! Excel ile link ekle.[/bold red]")
            input("\nDevam etmek için Enter...")
            return

        self.console.print(f"[bold green]🚀 Price Patrol Başlıyor ({len(targets)} hedef)...[/bold green]")
        
        for product in targets:
            self.console.print(f"\n🔎 [cyan]{product['name']}[/cyan]")
            
            competitor_price = self.scraper.fetch_price(product['competitor_url'])
            
            if competitor_price:
                self.console.print(f"💰 Rakip: [bold green]{competitor_price} TL[/bold green] | Bizim: [bold yellow]{product['my_price']} TL[/bold yellow]")
                
                if competitor_price < product['my_price']:
                    diff = product['my_price'] - competitor_price
                    self.console.print(f"[bold red]⚠️ ALARM: Rakip {diff:.2f} TL daha ucuz![/bold red]")
                    
                    # --- WHATSAPP BİLDİRİMİ ---
                    if self.notifier:
                        self.console.print("[dim]📲 WhatsApp bildirimi gönderiliyor...[/dim]")
                        self.notifier.send_alert(
                            product['name'], 
                            product['my_price'], 
                            competitor_price, 
                            product['competitor_url']
                        )
                else:
                    self.console.print("[bold green]✅ Rekabetçiyiz.[/bold green]")
            else:
                self.console.print("[bold red]❌ Fiyat alınamadı.[/bold red]")
        
        input("\nDevam etmek için Enter...")

    def run_trend_hunter(self):
        """Pazar Ajanı + Excel Raporlama"""
        url = Prompt.ask("[bold yellow]Kategori Linkini Yapıştır (Hepsiburada/Trendyol)[/bold yellow]")
        if len(url) < 10: return

        self.console.print("[dim]🕵️‍♂️ Ajan taranıyor...[/dim]")
        trends = self.scraper.fetch_best_sellers(url)
        
        if trends:
            table = Table(title="🔥 TREND ANALİZİ 🔥")
            table.add_column("Ürün", style="cyan")
            table.add_column("Fiyat", style="green")
            table.add_column("Durum", style="bold")
            
            my_names = [str(p.get('name', '')).lower() for p in self.products]
            
            for t in trends:
                status = "YOK"
                disp = "[red]YOK - FIRSAT![/red]"
                if any(t['name'].lower()[:15] in m for m in my_names):
                    status = "VAR"
                    disp = "[green]STOKTA VAR[/green]"
                
                t['status'] = status
                table.add_row(t['name'][:50] + "...", f"{t['price']} TL", disp)
            
            self.console.print(table)
            
            # EXCEL SORUSU
            if Prompt.ask("\n[bold yellow]Excel'e raporlayayım mı?[/bold yellow]", choices=["e", "h"], default="e") == "e":
                save_trends_to_excel(trends, url)
        else:
            self.console.print("[red]Sonuç yok veya site engelledi.[/red]")
        input("\nDevam etmek için Enter...")

    def send_test_mail(self):
        """Manuel Test Maili"""
        if not self.notifier:
            self.console.print("[bold red]❌ Bildirim sistemi (notifier.py) bulunamadı veya hatalı![/bold red]")
            input("\nDevam etmek için Enter...")
            return
            
        self.console.print("[bold yellow]📧 Test maili gönderiliyor...[/bold yellow]")
        try:
            self.notifier.send_alert(
                product_name="TEST ÜRÜNÜ (Panelden)",
                my_price=150.00,
                competitor_price=140.00,
                url="https://www.google.com"
            )
            self.console.print("[bold green]✅ Mail gönderildi! Gelen kutunuzu kontrol edin.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ Hata: {e}[/bold red]")
        
        input("\nDevam etmek için Enter...")

    def run_scheduler(self):
        """Otomatik Zamanlayıcı"""
        self.console.clear()
        self.console.print("[bold green]⏰ OTOMATİK MOD AKTİF[/bold green]")
        self.console.print("Her sabah 09:30'da tarama yapıp mail atacak.")
        self.console.print("[dim]Durdurmak için CTRL+C yapın.[/dim]\n")
        
        trend_hunter = TrendHunter()
        
        while True:
            now = datetime.now()
            # Saat 09:30 mu?
            if now.hour == 9 and now.minute == 30:
                self.console.print(f"\n[bold yellow]🚀 Saat {now.strftime('%H:%M')}! Görev Başlıyor...[/bold yellow]")
                trend_hunter.run_daily_scan_and_report()
                self.console.print("[bold green]✅ Görev Tamamlandı. Yarını bekliyor...[/bold green]")
                time.sleep(65) # Bir dakika bekle ki tekrar çalışmasın
            
            # Her 30 saniyede bir saati kontrol et
            time.sleep(30)
            sys.stdout.write(f"\r⏳ Bekleniyor... Şu an: {now.strftime('%H:%M:%S')}")
            sys.stdout.flush()

    def run_trend_report_test(self):
        """Manuel Trend Raporu Testi"""
        self.console.print("[bold yellow]🚀 Manuel Trend Raporu Testi Başlatılıyor...[/bold yellow]")
        try:
            trend_hunter = TrendHunter()
            trend_hunter.run_daily_scan_and_report()
            self.console.print("[bold green]✅ Test tamamlandı. Mail kutunuzu kontrol edin.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]❌ Hata: {e}[/bold red]")
        input("\nDevam etmek için Enter...")

    def run(self):
        while True:
            self.print_banner()
            self.console.print(f"[dim]Ürün Sayısı: {len(self.products)}[/dim]\n")
            
            self.console.print("1. 🛡️  Price Patrol (Fiyat Takibi)")
            self.console.print("2. 🕵️‍♂️ Trend Hunter (Pazar Ajanı)")
            self.console.print("3. 🔄 Envanter Sync (IdeaSoft)")
            self.console.print("-----------------------------")
            self.console.print("4. 📤 Excel İndir (Düzenle)")
            self.console.print("5. 📥 Excel Yükle (Kaydet)")
            self.console.print("-----------------------------")
            self.console.print("6. 📧 Test Maili Gönder")
            self.console.print("7. ⏰ Otomatik Mod (Her Sabah 09:30)")
            self.console.print("8. 🚀 Trend Raporunu Şimdi Test Et")
            self.console.print("9. ❌ Çıkış")
            
            choice = IntPrompt.ask("\nSeçim", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == 1: self.run_price_patrol()
            elif choice == 2: self.run_trend_hunter()
            elif choice == 3: self.sync_inventory()
            elif choice == 4: export_to_excel(); input("Enter...")
            elif choice == 5: import_from_excel(); self.products = self.load_products(); input("Enter...")
            elif choice == 6: self.send_test_mail()
            elif choice == 7: self.run_scheduler()
            elif choice == 8: self.run_trend_report_test()
            elif choice == 9: break

if __name__ == "__main__":
    app = SarScopeApp()
    app.run()