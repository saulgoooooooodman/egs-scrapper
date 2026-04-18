# EGS Scrapper

EGS Scrapper, EGS haber dosyalarini tarayip editorlerin hizlica kopyalayabilecegi, duzenleyebilecegi ve arsivde arayabilecegi temiz haber metni ureten masaustu bir PySide6 uygulamasidir.

Bu repo, uygulamanin kaynak kodunu icerir. Yerel ayarlar, veritabanlari, loglar ve kullaniciya ozel calisma verileri bilerek repoya dahil edilmez.

## Ozellikler

- Gunluk EGS klasorunu tarama
- Haber kodu ve baslik parse etme
- Baslik sozlugu ve kanal kurallari ile duzeltme
- Arsiv veritabanlarinda tarih araligina gore arama
- Editor filtresi ile arsiv arama
- Salt okunur arsiv sonuc listesi
- Veritabani bakimi
- Cok kullanicili profil secimi
- EXE derleme destegi

## Teknoloji

- Python
- PySide6
- SQLite
- PyInstaller

## Klasor Yapisi

```text
EGS Scrapper/
|- actions/
|- core/
|- data/
|- dialogs/
|- dictionaries/
|- models/
|- parsing/
|- tools/
|- ui/
|- watchers/
|- app.py
|- main_window.py
|- build_exe.bat
|- requirements.txt
|- EGS_Scrapper.spec
\- channel_rules.json
```

## Kurulum

### 1. Repoyu klonlayin

```powershell
git clone https://github.com/saulgoooooooodman/egs-scrapper.git
cd egs-scrapper
```

### 2. Sanal ortam olusturun

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Bagimliliklari kurun

```powershell
pip install -r requirements.txt
```

### 4. Uygulamayi calistirin

```powershell
python app.py
```

## Gelistirme Ortami

Projeyi kaynak kod uzerinden gelistirin. EXE yalnizca dagitim icindir.

Onerilen gunluk akis:

```powershell
git pull origin main
python app.py
git add .
git commit -m "Degisiklik aciklamasi"
git push origin main
```

## Baska Bilgisayarda Gelistirmeye Devam Etme

Bu proje GitHub uzerinden farkli bilgisayarlarda rahatca surdurulebilir.

Onerilen akis:

1. Bu bilgisayarda degisiklik yapin
2. Commit edin
3. GitHub'a push edin
4. Diger bilgisayarda repoyu clone edin veya pull alin
5. Calismaya orada devam edin

Ornek:

```powershell
git pull origin main
```

## Kullanici Verileri Nerede Tutulur

Uygulama yazilabilir verileri varsayilan olarak kullanici profilinde tutar:

```text
%LOCALAPPDATA%\EGS Scrapper
```

Burada tipik olarak sunlar bulunur:

- `settings.json`
- `databases/`
- `logs/`
- `error_reports/`
- `channel_dictionaries/`
- `common_dictionary.json`

Bu veriler kisiye ve makineye ozeldir, bu yuzden repoya dahil edilmez.

## Profil Sistemi

Uygulama acilisinda profil secimi ekrani gelebilir.

Bu ekran sunlar icin gereklidir:

- Ayni bilgisayari birden fazla editor kullaniyorsa
- Farkli kanallarda calisiliyorsa
- Farkli kok klasorlerle gecis yapilacaksa

Profil ekraninda secilen temel bilgiler:

- Kullanici adi
- Kanal
- Kok klasor
- Profil logosu

## Kok Klasor Mantigi

Uygulama tarih klasorunu degil, kanalin ana haber kokunu bekler.

Dogru ornekler:

- `C:\DeeR\ANEWS\HABER`
- `C:\DeeR\Haber\HABER`
- `C:\DeeR\ASPOR\HABER`

Yanlis ornekler:

- `C:\DeeR\ANEWS\HABER\2026\04182026.egs`
- `C:\DeeR\ANEWS\HABER\HABER\2026\04182026.egs`

## Arsiv Arama

Arsiv arama ekrani:

- tarih araliginda calisir
- birden fazla arama satiri destekler
- editor filtresi destekler
- sonuclari salt okunur gosterir
- sag tik menusunde hizli islem sunar

Sonuc listesinde gorulen baslica alanlar:

- Tarih
- Kod
- Baslik
- Editor
- Kaynak
- Onizleme

## Veritabani Bakimi

Uygulamada veritabani bakim araclari bulunur:

- `Veritabani Sagligini Kontrol Et`
- `Veritabanini Toparla`
- `Arama Istatistiklerini Yenile`

Bu islemler, yerel veritabanlarinda duzen ve arama performansi acisindan yardimci olur.

## EXE Derleme

Windows icin EXE uretmek icin:

```powershell
build_exe.bat
```

Derleme ciktisi:

```text
dist\EGS Scrapper
```

Not:

- `build_exe.bat`, dagitima temiz profil baslangici saglayan bir `settings.json` birakir.
- Bu sayede yeni kurulumda EXE ilk acilista bos profil akisiyla baslar.

## Repo Temizlik Politikasi

Bu repo bilerek asagidakileri izlemez:

- `settings.json`
- `databases/`
- `logs/`
- `error_reports/`
- `trash/`
- `build/`
- `dist/`
- `release/`
- test raporlari
- gecici Python cache dosyalari

Bu amacla `.gitignore` dosyasi eklenmistir.

## Faydali Komutlar

### Durumu kontrol et

```powershell
git status
```

### Son degisiklikleri cek

```powershell
git pull origin main
```

### Degisiklikleri gonder

```powershell
git add .
git commit -m "Proje guncellemesi"
git push origin main
```

## Sorun Giderme

### Uygulama aciliyor ama haber gelmiyor

- Kok klasor yanlis olabilir
- Kanal yanlis olabilir
- Secilen tarih klasorde bulunmuyor olabilir

### Arsiv arama sonuc vermiyor

- Tarih araligini kontrol edin
- Kod filtresini temizleyin
- Editor filtresini bosaltip tekrar deneyin
- `Tam Eslesme` aciksa kapatip deneyin

### Baslik yanlis parse oldu

- Kanal kurallarini kontrol edin
- Sonra `Zorla Yenile` kullanin

## Katki ve Senkronizasyon

Bu repo tek makinede degil, birden fazla makinede gelistirmeye uygun hale getirilmistir.

En guvenli senkronizasyon duzeni:

1. Calismaya baslamadan once `git pull`
2. Is bitince `git add`, `git commit`, `git push`
3. Diger bilgisayarda tekrar `git pull`

## Uzak Repo

GitHub adresi:

[https://github.com/saulgoooooooodman/egs-scrapper](https://github.com/saulgoooooooodman/egs-scrapper)
