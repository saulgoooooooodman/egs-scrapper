# EGS Scrapper

EGS Scrapper, televizyon haber odası sistemi (EGS) ile medya arşiv sistemi (Cinegy) arasında manuel veri girişini ortadan kaldırmak için geliştirilmiş profesyonel bir otomasyon aracıdır.

Haber başlıklarını, KJ (alt bant) metinlerini ve metadata’yı parse eder, temizler ve Cinegy uyumlu formatta hazır hale getirir.

---

## 🚀 Özellikler

- 📂 EGS (.egs) dosyalarını otomatik tarama
- 🧠 Gelişmiş parser (başlık + KJ ayrıştırma)
- 🧹 Başlık normalize sistemi
- 🔤 Türkçe karakter düzeltme (sözlük + spellcheck altyapısı)
- 📋 Çift tıklama ile kopyalama
- 🔎 Gelişmiş filtreleme ve arama
- 🧩 Kanal bazlı kurallar
- ⚡ Cache sistemi (hızlı yükleme)
- 🧵 Worker thread (UI donmaz)
- 👁️ Canlı izleme (Live Watch)
- 🗃️ Arşiv arama
- 🧪 Health Check + Smoke Test

---

## 🧠 Sistem Nasıl Çalışır?

1. EGS klasörü taranır  
2. Haber dosyaları parse edilir  
3. Başlık ve KJ metinleri ayrıştırılır  
4. Kanal kuralları uygulanır  
5. Sonuç Cinegy uyumlu metne dönüştürülür  

---

## 📁 Proje Yapısı
egs-scrapper/
│
├── actions/ # UI davranışları
├── core/ # çekirdek modüller
├── data/ # veritabanı ve cache
├── dialogs/ # pencere bileşenleri
├── dictionaries/ # sözlük ve spellcheck
├── models/ # veri modelleri
├── parsing/ # EGS parser motoru
├── ui/ # arayüz bileşenleri
├── watchers/ # canlı izleme
│
├── channel_dictionaries/ # kanal sözlükleri
├── channel_logos/ # kanal logoları
│
├── app.py
├── main_window.py
├── version_info.py
├── health_check.py
├── smoke_test.py
│
└── channel_rules.json

---

## 📺 Kanal Kuralları

### A NEWS
- Bölge kodları korunur (WME, WEU vb.)
- Format: `(PKG)` → VTR
- Uluslararası haber yapısı

---

### A HABER
- Türkçe karakter düzeltme zorunludur
- Örnek:
  - `ERDOGAN → ERDOĞAN`
  - `VALILIGI → VALİLİĞİ`

---

### A SPOR
- Program isimleri korunur (`90+1`, `SPOR GÜNDEMİ`)
- Minimal normalize uygulanır

---

### A PARA
- Tüm başlıkların sonuna `-APR` eklenir
- Ekonomi içerikleri önceliklidir

---

## ⚙️ Parser Kuralları

### Başlık Normalize

FRANCE MEDIA(PKG)31 → FRANCE MEDIA (PKG) 31
(OD) → ÖZEL HABER -


### Ignore Kuralları

- `COPLUK` klasörü yok sayılır  
- `+` ile başlayan başlıklar filtrelenir  

---

### KJ Parsing

EGS içinden alınan KJ verisi:

;;DOUBLE
;;NAME
;;LOCATION


➡️ Sıralama:

1. Başlık  
2. Açıklama  
3. Kişi  
4. Lokasyon  

---

## 🧾 Kopyalama Davranışı

- 🖱️ Çift tıklama → metni kopyalar  
- ⌨️ Ctrl + C → çoklu kopyalama  
- 🏷️ Başlığa çift tıklama → tüm metni kopyalar  

---

## ⚡ Performans

- Cache sistemi (mtime + size)
- Worker thread
- Lazy loading
- Live file watcher

---

## 🧪 Test ve Kontrol

### Health Check
```bash
python health_check.py
```
### Smoke Test
```bash
python smoke_test.py
```
▶️ Çalıştırma
python app.py
📦 Versiyon

v1.8.2 - Stable

🛠️ Geliştirme

⚠️ **Bilinen Kısıtlar**
Büyük harfli başlıklarda spellcheck sınırlı çalışır
Bazı EGS varyasyonları manuel düzeltme gerektirebilir

📌 **Roadmap**
✅ Gelişmiş parser
⏳ Spellcheck iyileştirme
⏳ Installer sistemi
⏳ Otomatik güncelleme
⏳ Test senaryoları genişletme
👨‍💻 Katkı

Bu proje aktif geliştirme altındadır.
Geri bildirimler değerlidir.

📄 **Lisans**

Internal / Private kullanım amaçlı geliştirilmiştir.
