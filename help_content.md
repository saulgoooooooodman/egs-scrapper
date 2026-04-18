# EGS Scrapper Yardım Viki

Bu yardım ekranı, programı ilk kez kullanan birinin hızlıca yönünü bulabilmesi için konu konu düzenlendi.
Sol taraftaki başlıklardan ilgili bölüme geçebilir, üstteki arama kutusuyla içerikte anahtar kelime arayabilirsin.

## 1. Program Nedir
EGS Scrapper, EGS haber dosyalarını okuyup temiz, düzenlenebilir ve kopyalanabilir haber metni üretir.
Program yalnızca günlük listeleme yapmaz; aynı zamanda arşiv arama, başlık düzeltme, kod filtreleme, toplu tarama ve veritabanı bakımı da sunar.

## 2. İlk Açılış

### 2.1 Profil Seçimi Ekranı
Açılışta gelen profil ekranı, hangi kullanıcıyla ve hangi kanal köküyle çalışacağını belirler.
Bu ekran özellikle aynı bilgisayarı birden fazla editör kullanıyorsa önemlidir.

### 2.2 Neden Gerekli
- Farklı kullanıcılar farklı kanal kökleriyle çalışabilir.
- Aynı kullanıcı gün içinde farklı kanallara geçebilir.
- Yanlış klasör seçimi yüzünden haber bulunamama sorunu yaşanmasını önler.

### 2.3 Kök Klasör Nasıl Seçilir
Program tarih klasörünü değil, kanalın ana haber kökünü bekler.

Doğru örnekler:
- `C:\DeeR\ANEWS\HABER`
- `C:\DeeR\Haber\HABER`
- `C:\DeeR\ASPOR\HABER`

Yanlış örnekler:
- `C:\DeeR\ANEWS\HABER\2026\04182026.egs`
- `C:\DeeR\ANEWS\HABER\HABER\2026\04182026.egs`
- `C:\DeeR\ANEWS\HABER\17.04.2026`

### 2.4 Profil Logosu
Profil logosu zorunlu değildir.
Sadece kullanıcıyı görsel olarak ayırt etmeyi kolaylaştırır.

### 2.5 Profili Hatırla
İşaretliyse son seçilen kullanıcı, kanal ve klasör bir sonraki açılışta korunur.

### 2.6 Bu Pencereyi Açılışta Göster
İşaretliyse program her açılışta profil ekranını sorar.
Ortak kullanım bilgisayarlarında önerilir.

## 3. Ana Ekran

### 3.1 Üst Çubuk
Üst bölümde kanal logosu, profil butonu ve tarih seçici bulunur.
Buradaki tarih değiştiğinde ilgili günün haberleri yeniden yüklenir.

### 3.2 Haber Listesi
Sol taraftaki ana liste, o gün taranmış haberleri gösterir.
Kod, başlık, editör ve metin bilgileri filtrelere göre listelenir.

### 3.3 Önizleme Alanı
Sağ bölümde seçili haberin tam metni görülür.
Burada metin düzenleme, kopyalama ve bul/değiştir işlemleri yapılabilir.

## 4. Menü Rehberi

### 4.1 Dosya
- `Profili Değiştir`: Kullanıcı, kanal ve kök klasör bilgilerini değiştirir.
- `Veri ve Veritabanı`: veri klasörleri, dış veritabanları ve bakım komutlarını içerir.
- `Tarama ve Yenileme`: yenile, zorla yenile, önbellek temizleme işlemleri.
- `Kapat`: uygulamayı güvenli kapatır.

### 4.2 Düzen
- Kes, kopyala, yapıştır, sil, geri al, yinele
- `Harfleri Çevir`
- `Çoklu Seç`

### 4.3 Ara
- `Bul`
- `Bul / Değiştir`
- `Sonrakini Bul`
- `Öncekini Bul`
- `Arşiv Ara`

### 4.4 Görünüm
- `Her Zaman Üstte Göster`
- `Canlı İzleme`
- `Haber Kodlarını Göster / Gizle`
- `Önceki Günün Haberlerini Gizle`
- aynı başlıklı haberleri gösterme/gizleme seçenekleri
- `Yazı Boyutu`

### 4.5 Araçlar
- `Başlık Sözlüğü`
- `Sözlük Paketini Yönet`
- `Kanal Kuralları`
- `Yazım Denetimini Yeniden Algıla`
- `Kodları Filtreleme`
- `Geçmişi Tara`

### 4.6 Yardım
- `Yardım`
- `Sürüm Notları`
- `Günlük Görüntüleyici`

## 5. Günlük Kullanım Akışı

### 5.1 Normal Günlük Akış
1. Profili seç.
2. Doğru tarihi seç.
3. Listeyi kontrol et.
4. Gerekirse arama ve filtreleri uygula.
5. Başlığı veya metni düzelt.
6. Kopyala veya kaydet.

### 5.2 Haber Gelmediğinde
Önce kök klasör doğru mu kontrol et.
Sonra tarih doğru mu bak.
Gerekirse `Yenile`, sonra `Zorla Yenile` kullan.

## 6. Tarama ve Yenileme

### 6.1 Yenile
Seçili tarihin klasörünü yeniden tarar ve listeyi günceller.

### 6.2 Zorla Yenile
Önbelleği atlar.
Gerekirse eski DB kayıtlarını silip dosyayı tekrar parse ederek tazeler.
Parser düzeltmelerinden sonra en faydalı komuttur.

### 6.3 Önbelleği Temizle
Dosya önbelleğini sıfırlar.
Bir sonraki yüklemede dosyalar yeniden değerlendirilir.

### 6.4 Geçmişi Tara
Belirli bir tarih aralığını topluca tarayıp arşiv veritabanlarını doldurur.
İlk büyük kurulum veya eksik ayları tamamlama için kullanılır.

## 7. Canlı İzleme
Canlı izleme, seçili tarihin klasörünü dinler.
Klasöre yeni dosya düşerse ya da değişiklik olursa listeyi otomatik yeniler.
Canlı yayın akışında manuel yenile ihtiyacını azaltır.

## 8. Ana Ekran Araması

### 8.1 Ne Üzerinde Çalışır
Ana ekran araması yalnızca o anda yüklenmiş haberler üzerinde çalışır.
Veritabanının tamamını taramaz.

### 8.2 Kapsamlar
- `Tümü`
- `Başlık`
- `Haber Metni`

### 8.3 Örnekler
- `iran`
- `hormuz`
- `erdogan`
- `protest`

### 8.4 Regex
Regex açılırsa gelişmiş desen araması yapılır.
Örnek:
- `iran|israil`
- `trump.*pope`
- `\bpak\b`

## 9. Kodları Filtreleme
Kod filtresi yalnızca kanal kurallarında tanımlı haber kodlarını gösterir.

### 9.1 Göster Modu
Yalnızca seçilen kodları ekranda bırakır.

### 9.2 Gizle Modu
Seçilen kodları görünümden çıkarır.

### 9.3 Örnek
- `Göster: WAM, WME`
- `Gizle: LIVE`

## 10. Arşiv Arama
Arşiv arama, dahili aylık veritabanları ve tanımlı dış veritabanları üzerinde geçmiş kayıt arar.
Uzun arama işlemleri arka planda yürür.

### 10.1 Tarih Aralığı
Başlangıç ve bitiş tarihini belirleyerek yalnızca ilgili dönemi ararsın.

### 10.2 Arama Satırları
Birden fazla satır eklenebilir.

Satır mantıkları:
- `Ayrı`: satırlardan en az biri eşleşsin
- `Birlikte`: bu satır mutlaka eşleşsin
- `Hariç`: bu satır eşleşirse sonuç dışlansın

### 10.3 Tek Satır Kullanımı
Tek satır varken `Ayrı / Birlikte / Hariç` seçimi görünmez.
Çünkü tek satırda buna ihtiyaç yoktur.

### 10.4 Editör Filtresi
Editör alanına virgülle birden fazla isim yazılabilir.
Örnek:
- `BURHAN AYTEKIN, METIN ALGUL`

Girilen editörlerden herhangi biri kayıt içinde varsa sonuç gelir.

### 10.5 Sonuç Listesi
Sonuç listesi salt-okunurdur.
Burada yanlışlıkla veri düzenlenmez.

### 10.6 Sağ Tık Menüsü
Arşiv sonucunda sağ tık menüsünde şunlar vardır:
- `Kopyala`
- `Tarihe Git`
- `Kaynağı Klasörde Göster`

### 10.7 Sonuç Tarihi
Tarih `gün.ay.yıl` biçiminde gösterilir.

### 10.8 Uyarılar
Bazı veritabanları hata verirse arama yine devam eder.
İşlem sonunda kaç veritabanının hata verdiği kullanıcıya bildirilir.

## 11. Bul / Değiştir
`Ctrl+H` ile açılır.
Sadece o anda yüklenmiş içerik üzerinde çalışır.

### 11.1 Kapsamlar
- `Önizleme Metni`
- `Seçili Haber Metinleri`
- `Listelenen Haber Metinleri`
- `Geçerli Haber Başlığı`
- `Seçili Haber Başlıkları`
- `Tüm Haber Başlıkları`

### 11.2 Regex Örnekleri
- bul: `\bTURKIYE\b`
- değiştir: `TÜRKİYE`

- bul: `\s{2,}`
- değiştir: ` `

### 11.3 Başlıkta Ne Değişir
Başlık değişirse ilgili önizleme ve kayıt bilgisi birlikte güncellenir.

## 12. Başlık Düzeltme ve Sözlük

### 12.1 Genel Mantık
- A NEWS kendi kanal sözlüğünü kullanır.
- Diğer kanallar ortak sözlükten de yararlanır.
- Varsa gelişmiş yazım denetimi son aşamada devreye girer.

### 12.2 Nereden Yönetilir
- `Araçlar > Başlık Sözlüğü`
- `Araçlar > Kanal Kuralları`
- `Araçlar > Sözlük Paketini Yönet`

### 12.3 Örnek Girişler
- `ERDOGAN -> ERDOĞAN`
- `ISTANBUL -> İSTANBUL`
- `TURKIYE -> TÜRKİYE`

## 13. Kanal Kuralları
Kanal kuralları, parser’ın hangi haber kodlarını tanıyacağını ve bazı kanal özel davranışları belirler.
Önemli not: Parser artık yalnızca burada tanımlı kodları haber kodu olarak kabul eder.

## 14. Dış Veritabanları
Başka makinelerden veya eski arşivlerden gelen `.db` dosyaları arşiv aramaya eklenebilir.

### 14.1 Ne İşe Yarar
- Harici kaynakları birlikte tarar
- Sonuçlarda kaynak adını gösterir
- Aynı haber birden fazla veritabanında varsa tekilleştirme yapar

### 14.2 Nereden Açılır
`Dosya > Veri ve Veritabanı > Dış Veritabanları`

## 15. Veritabanı Bakımı

### 15.1 Sağlık Kontrolü
Veritabanı yapısının bozulup bozulmadığını kontrol eder.

### 15.2 VACUUM
Silinmiş alanları temizleyip dosyayı sıkıştırır.

### 15.3 ANALYZE
Sorgu istatistiklerini günceller.
Arşiv arama performansına yardımcı olabilir.

## 16. Günlük Görüntüleyici
Programın loglarını açar.
Bir hata olduğunda ilk bakılması gereken yerlerden biridir.

Loglarda özellikle şunlar aranabilir:
- `Traceback`
- `Parse`
- `Scanner`
- `ArchiveSearch`

## 17. Sık Karşılaşılan Sorunlar

### 17.1 Haber Bulunamadı
- Kök klasör yanlış olabilir
- Tarih yanlış olabilir
- Kanal yanlış olabilir
- İlgili günde dosya gerçekten olmayabilir

### 17.2 Başlık Yanlış Parse Oldu
Önce `Kanal Kuralları` içindeki haber kodlarını kontrol et.
Sonra `Zorla Yenile` çalıştır.

### 17.3 Arşiv Arama Sonuç Vermiyor
- Tarih aralığını büyüt
- Kod filtresini temizle
- Editör filtresini boşalt
- `Tam Eşleşme` açıksa kapat
- Regex açıksa deseni kontrol et

### 17.4 Eski Hatalı Kayıt Görünüyor
Bu çoğu zaman veritabanında kalmış eski parse sonucudur.
İlgili gün için `Zorla Yenile` genelde çözer.

## 18. Kısayollar
- `F5`: Yenile
- `Ctrl+F`: Arama alanına odaklan
- `Ctrl+H`: Bul / Değiştir
- `F3`: Sonrakini bul
- `Shift+F3`: Öncekini bul
- `F7`: Arşiv Ara
- `Ctrl+Q`: Kapat

## 19. İpuçları
- Tooltip’leri takip et; ana ekran ve dialogların çoğunda açıklama var.
- Profil ekranında yanlış klasör seçmek, en sık yaşanan sorunlardan biridir.
- Parser değişikliği sonrası önce `Zorla Yenile` düşün.
- Arşiv aramada sonuçların kaynağına bakmak için `Kaynak` sütununu kullan.

## 20. Terimler

### EGS
Yayın akışında kullanılan kaynak dosya biçimi.

### Kök Klasör
Tarih klasörlerinin altında yer aldığı ana kanal klasörü.

### Kod Filtresi
Belirli haber kodlarını gösteren veya gizleyen görünüm filtresi.

### Arşiv Arama
Geçmiş aylardaki veritabanları üzerinde arama yapan ekran.
