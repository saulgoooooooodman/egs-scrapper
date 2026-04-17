# EGS Scrapper Yardım

## 1. Programın Amacı
EGS Scrapper, EGS haber dosyalarını okuyup temiz, kopyalanabilir ve düzenlenebilir haber metni üretir. Program aynı zamanda günlük tarama, arşiv arama, kod filtreleme, başlık düzeltme ve metin düzenleme işlevlerini tek arayüzde toplar.

## 2. Ana Menü Özeti

### Dosya
- `Profili Değiştir`: Kullanıcı, kanal ve kök klasör bilgilerini değiştirir.
- `Veri ve Veritabanı`: veritabanı klasörü, veri klasörü, dış veritabanı yönetimi ve veritabanı birleştirme komutlarını toplar.
- `Günlükler ve Klasörler`: uygulamanın günlük klasörüne hızlı erişim verir.
- `Tarama ve Yenileme`: yenile, zorla yenile, önbelleği temizle ve geçmişi tara komutlarını toplar.
- `Kapat`: uygulamayı güvenli şekilde kapatır.

### Düzen
- Kes, kopyala, yapıştır, sil, geri al, yinele
- `Harfleri Çevir`: Türkçe büyük/küçük harf dönüşümleri
- `Çoklu Seç`: aynı kodlu veya farklı kodlu haberleri seçme

### Ara
- `Bul`
- `Bul / Değiştir`
- `Sonrakini Bul`
- `Öncekini Bul`

### Görünüm
- `Her Zaman Üstte Göster`
- `Canlı İzleme`
- `Haber Kodlarını Göster / Gizle`
- `Önceki Günün Haberlerini Göster`
- tekrar eden başlıklar için gösterme/gizleme tercihleri
- `Yazı Boyutu`: liste ve önizleme yazılarını büyütüp küçültür.

### Araçlar
- `Dil ve Kurallar`: başlık sözlüğü, sözlük paketi ve kanal kuralları araçlarını toplar.
- `Arşiv ve Veri`: arşiv arama ve kod filtreleme araçlarını toplar.
- `Bakım`: yazım denetimi durumu gibi bakım komutlarını içerir.

### Yardım
- `Yardım`
- `Sürüm Notları`
- `Tanılama`: günlük görüntüleyici, sağlık kontrolü ve smoke test komutlarını içerir.

## 3. Doğru Kök Klasör Seçimi
Program tarih klasörünü değil kanalın ana haber kökünü bekler.

### Doğru örnekler
- `C:\DeeR\ANEWS\HABER`
- `C:\DeeR\Haber\HABER`
- `C:\DeeR\ASPOR\HABER`

### Yanlış örnekler
- `C:\DeeR\ANEWS\HABER\HABER\2026\04172026.egs`
- `C:\DeeR\ANEWS\HABER\17.04.2026`

## 4. Tarama ve Dosya Kuralları
- `_OGLE`, `_AKSAM`, `_SABAH` ve benzeri son ekli dosyalar okunur.
- `COPLUK` klasörü tamamen yok sayılır.
- ayraç/separator dosyaları listelenmez.
- dosya adının sonundaki gün numarası başlık gösteriminden çıkarılır.
- istenirse bir önceki günün haberleri görünümden gizlenebilir.

## 5. Başlık Düzeltme ve Sözlük

### Genel mantık
- A NEWS kendi kanal sözlüğünü kullanır.
- diğer kanallarda ortak sözlük + kanal sözlüğü birlikte çalışır.
- varsa yazım denetimi önerileri son aşamada devreye girer.

### Örnek sözlük girişleri
- `ERDOGAN -> ERDOĞAN`
- `ISTANBUL -> İSTANBUL`
- `TURKIYE -> TÜRKİYE`
- `ISRAIL -> İSRAİL`

### Nereden yönetilir
- `Araçlar > Başlık Sözlüğü`
- `Araçlar > Kanal Kuralları`

## 6. Ana Ekranda Arama
Ana penceredeki arama kutusu o gün yüklenmiş haberler üzerinde çalışır.

### Normal arama örnekleri
- `iran`
- `protest`
- `erdogan`
- `hormuz`

### Arama alanı örnekleri
- `Başlık`: yalnızca başlıkta arar.
- `Haber Metni`: özet, gövde, final text ve editör alanlarında arar.
- `Tümü`: başlık ve metni birlikte tarar.

### Regex arama örnekleri
- `iran|israil`
- `trump.*pope`
- `\bpak\b`
- `^(live|canli)`  
  Not: regex kullanımında hatalı ifade girilirse sonuç boşalır ve uyarı verilir.

## 7. Kodları Filtreleme
`Araçlar > Kodları Filtreleme` ekranı yalnızca `Kanal Kuralları` içinde tanımlı haber kodlarını gösterir.

### Çalışma mantığı
- `Göster`: yalnızca seçilen kodlar görünür.
- `Gizle`: seçilen kodlar görünümden çıkarılır.
- listede olmayan yeni bir kod için önce `Kanal Kuralları` ekranından tanım eklenmelidir.

### Örnek
- `Göster: WAM, WME`
- `Gizle: LIVE`

## 8. Arşiv Arama
`Araçlar > Arşiv Arama` ekranı tarih aralığı içinde veritabanında arama yapar. Dahili aylık veritabanları ve tanımlı dış veritabanları birlikte taranır.

### Gelişmiş Arama Satırları
Arşiv aramada birden fazla satır oluşturulabilir.

### Satır mantıkları
- `Ayrı`: satırlardan en az biri eşleşirse sonuç döner.
- `Birlikte`: bu satır mutlaka eşleşmelidir.
- `Hariç`: eşleşirse sonuç dışlanır.

### Örnek 1
- `Birlikte: iran`
- `Ayrı: pope`
- `Hariç: talks`

Bu örnekte:
- `iran` mutlaka olacak
- `pope` varsa tercih edilecek
- `talks` geçen sonuçlar elenecek

### Örnek 2
- `Ayrı: india`
- `Ayrı: pakistan`

Bu örnekte Hindistan veya Pakistan geçen haberler gelir.

### Örnek 3
- `Birlikte: protest`
- `Hariç: sports`

Bu örnekte protest geçen ama sports içermeyen haberler gelir.

### Kapsam seçenekleri
- `Tümü`
- `Başlık`
- `Haber Metni`
- `Haber Kodu`

### Tam eşleşme örnekleri
- kapsam `Haber Kodu`, arama `WAS`, `Tam Eşleşme` açık  
  Yalnızca kodu tam `WAS` olan kayıtlar gelir.

- kapsam `Başlık`, arama `TRUMP IRAN POPE (SOT)`, `Tam Eşleşme` açık  
  Başlığı birebir bu olan haberler gelir.

### Regex örnekleri
- `iran|israil`
- `trump.*pope`
- `\b(iran|iraq)\b`
- `^(live|canli)`
- `\d{2}\.\d{2}\.\d{4}`  
  Not: regex yalnızca arama satırının içeriğine uygulanır.

### Kod filtresiyle birlikte kullanım
- önce `Kod Filtreleri` ile `Göster: WAM, WME`
- sonra arama satırlarına `Birlikte: iran`

Bu durumda yalnızca seçilen kodlarda ve aranan ifadede eşleşen kayıtlar gelir.

## 9. Bul / Değiştir
`Ctrl+H` ile açılır. Bu ekran yalnızca o anda yüklü içerik üzerinde çalışır; veritabanının tamamını hedeflemez.

### Desteklenen kapsamlar
- `Önizleme Metni`
- `Seçili Haber Metinleri`
- `Listelenen Haber Metinleri`
- `Geçerli Haber Başlığı`
- `Seçili Haber Başlıkları`
- `Tüm Haber Başlıkları`

### Başlık kapsamlarında ne olur
- haber başlığı güncellenir
- düzeltilmiş başlık alanı sıfırlanır
- final metnin ilk satırı da yeni başlığa çekilir

### Metin kapsamlarında ne olur
- final text alanı güncellenir
- aynı yüklenmiş haberler veritabanına geri yazılır

### Güvenlik notu
- önceki `Tüm Yüklü Haberler` kapsamı kaldırılmıştır.
- böylece geniş ve belirsiz bir toplu yazma davranışı engellenmiştir.

### Regex örnekleri
- bul: `\bTURKIYE\b`
- değiştir: `TÜRKİYE`

- bul: `\s{2,}`
- değiştir: ` `  
  Birden fazla boşluğu teke indirir.

- bul: `^LIVE\s+`
- değiştir: ``  
  Başlangıçtaki LIVE etiketini siler.

## 10. Metin Düzenleme
Program yalnızca okuyucu değil, aynı zamanda temel bir metin editörüdür.

### Sağ tık menüsünde bulunanlar
- Geri Al
- Yinele
- Kes
- Kopyala
- Yapıştır
- Sil
- Tümünü Seç
- Bul / Değiştir
- Harfleri Çevir
- Metni Kaydet

### Harfleri Çevir
- `TÜMÜNÜ BÜYÜK`
- `tümünü küçük`
- `İlk Harfler Büyük`

Türkçe `İ / I / i / ı` dönüşümleri özel olarak desteklenir.

## 11. Dış Veritabanları
`Dosya > Dış Veritabanlarını Yönet` ile başka makinelerden gelen `.db` dosyaları eklenebilir.

### Ne işe yarar
- arşiv aramaya ek veri kaynağı ekler
- sonuçlarda kaynak adı gösterilir
- aynı haber birden fazla DB’de varsa tekilleştirilir

## 12. Veritabanı Yapısı
- yeni kayıtlar aylık veritabanlarına yazılır.
- biçim: `kanal_ay_yıl.db`

### Örnekler
- `a_news_04_2026.db`
- `a_haber_12_2026.db`

Bu yapı zamanla tek dosyanın aşırı büyümesini önler.

## 13. Kısayollar
- `Ctrl+F` : Bul
- `Ctrl+H` : Bul / Değiştir
- `Ctrl+C` : Kopyala
- `Ctrl+S` : Metni Kaydet
- `Ctrl++` : Yazıyı büyüt
- `Ctrl+-` : Yazıyı küçült
- `Ctrl+0` : Varsayılan yazı boyutu
- `Ctrl+Q` : Uygulamayı kapat
- `Ctrl+Z` : Geri Al
- `Ctrl+Y` : Yinele
- `F3` : Sonrakini Bul
- `Shift+F3` : Öncekini Bul
- `F5` : Yenile
- `F7` : Arşiv Arama

## 14. Günlükler ve Tanılama

### Günlüklere erişim
- `Dosya > Günlük Klasörünü Aç`
- `Yardım > Tanılama > Günlük Görüntüleyici`

### Sağlık kontrolü
- `python health_check.py`
- `Yardım > Tanılama > Sağlık Kontrolü Çalıştır`

### Smoke test
- `python smoke_test.py`
- `Yardım > Tanılama > Smoke Test Çalıştır`

Smoke test şu başlıkları birlikte doğrular:
- örnek EGS parse akışı
- veritabanına yazma ve geri okuma
- arşiv arama
- yardım ve arşiv arama pencerelerinin açılması
- ana pencerenin offscreen olarak açılması

### Log düzeni
- loglar günlük dosya adıyla tutulur
- büyük loglar parçalara bölünür
- en eski log dosyaları otomatik temizlenir

### Tipik sorunlar
- yanlış kök klasör seçimi
- channel rules içinde eksik haber kodu
- hatalı regex ifadesi
- dış veritabanında `news` tablosu bulunmaması

## 15. Sürüm Notları
Her yeni sürümde yapılan değişiklikler `Yardım > Sürüm Notları` ekranına eklenir. Yeni sürüm sonrası değişiklik görünmüyorsa:
- programı yeniden başlat
- doğru sürüm numarasının pencere başlığında göründüğünü kontrol et

## 16. Yardım Penceresi İçinde Arama
Yardım ekranının üst kısmındaki arama kutusundan şu konular hızlıca bulunabilir:
- `regex`
- `arşiv arama`
- `kod filtreleri`
- `başlık sözlüğü`
- `bul / değiştir`

Bu arama yardım metni içinde ileri/geri gezinmeyi destekler.

## 17. Profil ve Görünüm Özelleştirme

### Profil logosu
- `Dosya > Profili Değiştir` ekranından kullanıcıya özel görsel seçilebilir.
- seçilen görsel üst çubukta kanal logosunun yanında görünür.
- desteklenen biçimler: `png`, `jpg`, `jpeg`, `bmp`, `webp`

### Yazı boyutu
- `Görünüm > Yazı Boyutu > Büyüt`
- `Görünüm > Yazı Boyutu > Küçült`
- `Görünüm > Yazı Boyutu > Varsayılan Boyut`

## 18. Editör Odaklı Geliştirme ve Özelleştirme Önerileri

Parser dışında editör rolü de üstlenen bu yazılım için aşağıdaki geliştirmeler yüksek değer üretir:

- `Otomatik Kaydet`: önizleme metnindeki değişiklikler belli aralıkta taslak olarak saklanabilir.
- `Sürüm Karşılaştırma`: haberin özgün metni ile düzenlenmiş metni yan yana fark görünümünde izlenebilir.
- `Şablon / Snippet`: sık kullanılan kapanış, spot, canlı giriş ve alt yazı kalıpları tek tıkla eklenebilir.
- `Karakter ve Satır Sayacı`: CG, KJ ve başlık kısıtları için canlı sayaç gösterilebilir.
- `Toplu Başlık Dönüştürme`: seçili haberlerde toplu başlık standardizasyonu daha görünür hale getirilebilir.
- `Editör Notları`: her habere veritabanında saklanan kısa editör notu alanı eklenebilir.
- `Klavye Odaklı Kullanım`: sadece klavyeyle gezinme, kopyalama ve kaydetme akışı genişletilebilir.
- `Kişisel Profil Paketleri`: kullanıcı bazlı yazı boyutu, profil logosu, filtreler ve sözlük tercihleri tek profilde saklanabilir.
