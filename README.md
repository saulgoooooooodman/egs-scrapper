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
