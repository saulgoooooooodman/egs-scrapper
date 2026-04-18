EGS Scrapper
1. Proje Tanımı
EGS Scrapper, EGS sisteminden alınan haber verilerini analiz ederek Cinegy uyumlu hale getiren otomasyon aracıdır.
2. Özellikler
• EGS (.egs) dosyalarını otomatik tarama
• Başlık ve KJ parsing sistemi
• Türkçe karakter düzeltme (sözlük + spellcheck altyapısı)
• Çift tıklama ile kopyalama
• Kanal bazlı kurallar (A NEWS, A HABER, A SPOR, A PARA)
• Cache sistemi ve hızlı yükleme
• Worker thread (UI donmaz)
• Canlı izleme (Live Watch)
• Arşiv arama
• Health Check ve Smoke Test
3. Kanal Kuralları
A NEWS
Uluslararası haber yapısı. Bölge kodları korunur (WME, WEU vb).
A HABER
Türkçe karakter düzeltme zorunludur. ERDOGAN → ERDOĞAN gibi dönüşümler yapılır.
A SPOR
Program isimleri korunur. (90+1, SPOR GÜNDEMİ vb)
A PARA
Tüm başlıkların sonuna -APR eklenir.
4. Parser Kuralları
FRANCE MEDIA(PKG)31 → FRANCE MEDIA (PKG) 31
(OD) → ÖZEL HABER -
COPLUK klasörü yok sayılır
+ ile başlayan başlıklar filtrelenir
5. KJ Parsing
DOUBLE, NAME ve LOCATION etiketlerine göre ayrıştırılır.
Sıralama: Başlık → Açıklama → Kişi → Lokasyon
6. Kopyalama Davranışı
Çift tıklama ile metin kopyalanır
Ctrl + C ile çoklu kopyalama yapılır
Başlığa çift tıklama tüm metni kopyalar
7. Performans
Cache sistemi (mtime + size)
Worker thread kullanımı
Live watch sistemi
8. Çalıştırma
python app.py
