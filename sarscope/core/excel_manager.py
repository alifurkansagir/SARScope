import pandas as pd
import json
import os
from datetime import datetime

# Dosya yollarını otomatik bul
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
JSON_PATH = os.path.join(BASE_DIR, 'data', 'products.json')
EXCEL_PATH = os.path.join(BASE_DIR, 'data', 'urun_yonetimi.xlsx')

def export_to_excel():
    """Mevcut JSON verisini Excel'e döker"""
    print(f"📂 Veriler okunuyor: {JSON_PATH}")
    if not os.path.exists(JSON_PATH):
        print("❌ Hata: Veri yok! Önce IdeaSoft çek.")
        return
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        cols = ['sku', 'name', 'brand', 'my_price', 'competitor_url', 'min_price']
        existing = df.columns.tolist()
        order = [c for c in cols if c in existing] + [c for c in existing if c not in cols]
        df[order].to_excel(EXCEL_PATH, index=False)
        print(f"\n✅ EXCEL HAZIR: {EXCEL_PATH}")
    except Exception as e:
        print(f"❌ Hata: {e}")

def import_from_excel():
    """Excel'i geri yükler"""
    print(f"📂 Excel okunuyor: {EXCEL_PATH}")
    if not os.path.exists(EXCEL_PATH):
        print("❌ Hata: Excel dosyası yok.")
        return
    try:
        df = pd.read_excel(EXCEL_PATH).fillna("")
        new_data = df.to_dict(orient='records')
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)
        print(f"\n✅ GÜNCELLENDİ: {len(new_data)} ürün yüklendi.")
    except Exception as e:
        print(f"❌ Hata: {e}")

def save_trends_to_excel(trend_data, source_url):
    """Trend Ajanı (Pazar) sonuçlarını kaydeder"""
    if not trend_data:
        return
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"trend_raporu_{timestamp}.xlsx"
        file_path = os.path.join(BASE_DIR, 'data', filename)
        
        df = pd.DataFrame(trend_data)
        df['kaynak_link'] = source_url
        df['tarih'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        cols = ['name', 'price', 'status', 'kaynak_link', 'tarih']
        existing = [c for c in cols if c in df.columns]
        df[existing].to_excel(file_path, index=False)
        
        print(f"\n✅ RAPOR KAYDEDİLDİ!")
        print(f"📄 Dosya: {file_path}")
    except Exception as e:
        print(f"❌ Excel Hatası: {e}")