import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificationManager:
    def __init__(self):
        # Gmail SMTP ayarları (Varsayılan)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        # Ortam değişkenlerinden al, yoksa buradaki değerleri kullan
        # Güvenlik için bu bilgileri environment variable olarak tutmak en iyisidir.
        # Gmail kullanıyorsan "Uygulama Şifresi" (App Password) almalısın.
        # ÖRNEK: "abcd efgh ijkl mnop" (Boşluksuz: abcdefghijklmnop)
        
        self.sender_email = os.getenv("EMAIL_USER", "alifurkansagir69@gmail.com") # <- Kendi Gmail adresin
        self.sender_password = os.getenv("EMAIL_PASS", "xzldrzkigkaxshhx") # <- Aldığın 16 haneli kod
        self.recipient_email = os.getenv("EMAIL_TO", "alifurkan@sartechsoftware.com.tr") # <- Bildirimin gideceği adres

    def send_alert(self, product_name, my_price, competitor_price, url):
        """Fiyat alarmı için e-posta gönderir"""
        subject = f"🚨 Fiyat Alarmı: {product_name}"
        
        body = f"""
        Merhaba,
        
        SarScope bir fiyat fırsatı veya tehdidi tespit etti!
        
        📦 Ürün: {product_name}
        💰 Sizin Fiyatınız: {my_price} TL
        📉 Rakip Fiyatı: {competitor_price} TL
        ⚠️ Fark: {my_price - competitor_price:.2f} TL
        
        🔗 Rakip Linki: {url}
        
        Bu mesaj SarScope Otomasyonu tarafından gönderilmiştir.
        """
        
        self._send_email(subject, body)

    def send_trend_report(self, report_data):
        """Günlük trend raporunu HTML formatında gönderir"""
        date_str = datetime.now().strftime("%d.%m.%Y")
        subject = f"🔥 Günlük Trend Raporu - {date_str}"
        
        # HTML Başlangıcı
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">📅 SarScope Günlük Pazar Analizi ({date_str})</h2>
            <p>Aşağıdaki kategorilerde en çok satan ve yorum alan ürünler listelenmiştir:</p>
        """
        
        for category, products in report_data.items():
            if not products: continue
            
            html_content += f"<h3 style='background-color: #f39c12; color: white; padding: 10px;'>📂 {category}</h3>"
            html_content += """
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #ecf0f1;">
                    <th>Ürün Adı</th>
                    <th>Fiyat</th>
                    <th>Yorum/Değ.</th>
                    <th>Link</th>
                </tr>
            """
            
            for p in products[:10]: # Her kategoriden ilk 10 ürün
                html_content += f"""
                <tr>
                    <td>{p['name']}</td>
                    <td style="color: green; font-weight: bold;">{p['price']} TL</td>
                    <td>{p.get('reviews', '0')}</td>
                    <td><a href="{p.get('link', '#')}">Ürüne Git</a></td>
                </tr>
                """
            html_content += "</table><br>"
            
        html_content += """
            <p style="font-size: 12px; color: #7f8c8d;">Bu rapor SarScope Otomasyonu tarafından otomatik oluşturulmuştur.</p>
        </body>
        </html>
        """
        
        self._send_html_email(subject, html_content)

    def _send_html_email(self, subject, html_body):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
            server.quit()
            print(f"📧 Rapor başarıyla gönderildi: {self.recipient_email}")
        except Exception as e:
            print(f"❌ Rapor gönderme hatası: {e}")

    def _send_email(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            print(f"📧 E-posta başarıyla gönderildi: {self.recipient_email}")
        except Exception as e:
            print(f"❌ E-posta gönderme hatası: {e}")
            print("💡 İpucu: Gmail kullanıyorsanız 'Uygulama Şifresi' (App Password) almanız gerekebilir.")