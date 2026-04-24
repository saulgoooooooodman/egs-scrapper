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
Liste odaktayken klavyeden harf yazarsan program o önekle başlayan ilk habere atlar.
Örnek: `e` yazınca `E...`, hızlıca `erd` yazınca `ERD...` ile başlayan ilk başlık seçilir.

### 3.3 Önizleme Alanı
Sağ bölümde seçili haberin tam metni görülür.
Burada metin düzenleme, kopyalama ve bul/değiştir işlemleri yapılabilir.

## 4. Menü Rehberi

### 4.1 Dosya
- `Profili Değiştir`: Kullanıcı, kanal ve kök klasör bilgilerini değiştirir.
- `Ayarlar`: tüm temel ayarları ayrı pencerede toplar.
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
- `Sembol ile Başlayan Başlıkları Gizle`
- `Önceki Günün Haberlerini Gizle`
- aynı başlıklı haberleri gösterme/gizleme seçenekleri
- `Yazı Boyutu`

### 4.5 Ayarlar
Ayarlar artık ayrı pencere olarak açılır.
Sol tarafta kategori, sağ tarafta ilgili seçenekler yer alır.

Bu pencerede şunları bir arada yönetebilirsin:
- profil hatırlama
- açılışta profil penceresi
- kaldığım günü hatırla
- kaynak klasör boşsa uyar
- canlı izleme
- otomatik başlık yazım denetimi
- sembol ile başlayan başlıkları gizle
- haber kodu sütununu gizle
- listede düzeltilmiş başlığı göster
- eski haberleri gizle
- aynı haber başlıkları davranışı
- yazı boyutları
- pencere konumu ve her zaman üstte göster ayarları

### 4.6 Araçlar
- `Başlık Sözlüğü`
- `Sözlük Paketini Yönet`
- `Kanal Kuralları`
- `Kodları Filtreleme`
- `Geçmişi Tara`

### 4.7 Yardım
- `Yardım`
- `Sürüm Notları`
- `Günlük Görüntüleyici`
- `Düzenli İfadeler`

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

### 6.1 Sayfayı Yenile
Seçili tarihin klasörünü yeniden tarar ve listeyi günceller.
Normal kullanımda ilk tercih budur.
Yeni dosya geldiyse veya mevcut dosya değiştiyse çoğu zaman tek başına yeterlidir.
Dosya değişmediyse program daha önce parse edilmiş kaydı veritabanı ve önbellekten okumaya devam eder.

### 6.2 Veritabanını Güncelle
Önbelleği atlar.
Gerekirse eski DB kayıtlarını silip dosyayı tekrar parse ederek tazeler.
Parser düzeltmelerinden sonra en faydalı komuttur.

Kısacası:
- `Sayfayı Yenile`: Günlük normal kullanım için
- `Veritabanını Güncelle`: Parse mantığı, kanal kuralı, sözlük, yazım düzeltmesi ya da başlık davranışı değiştiyse

Ne zaman `Yenile` yetmez:
- Haber başlığı yanlış parse olmuşsa
- Kanal kodu yeni eklendiyse
- Başlık sözlüğüne yeni giriş yapıldıysa ama eski kayıt hâlâ eski görünüyorsa
- Başlık temizleme veya özel kural yeni tanımlandıysa
- Yazım denetimi ya da başlık düzeltme davranışı değiştiyse

### 6.3 Önbelleği Temizle
Dosya önbelleğini sıfırlar.
Bu işlem haber metinlerini silmez.
Yalnızca programın "bu dosyayı tekrar okumama gerek var mı" diye baktığı hızlı kontrol kayıtlarını temizler.
Bir sonraki yüklemede dosyalar yeniden değerlendirilir.

### 6.4 Kaynak Klasör Boşsa Ne Olur
Bazı günlerde kaynak klasör sonradan boşalabilir veya geçici olarak görünmeyebilir.
Program böyle bir durumda o güne ait veritabanını artık otomatik temizlemez.
Önce uyarı gösterir ve veritabanını korur.
İstersen uyarıdaki `Bir daha gösterme` kutusunu işaretleyebilirsin.

### 6.5 Geçmişi Tara
Belirli bir tarih aralığını topluca tarayıp arşiv veritabanlarını doldurur.
İlk büyük kurulum veya eksik ayları tamamlama için kullanılır.

## 7. Canlı İzleme
Canlı izleme, seçili tarihin klasörünü dinler.
Klasöre yeni dosya düşerse ya da değişiklik olursa listeyi otomatik yeniler.
Canlı yayın akışında manuel yenile ihtiyacını azaltır.
Tarih klasörü henüz yoksa program üst klasörü izler; klasör daha sonra oluşursa liste yine otomatik yenilenebilir.
Canlı izleme günlük kullanım için normal yenileme mantığıyla çalışır; gereksiz yere tüm günü baştan parse etmeye çalışmaz.

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

### 8.4 Düzenli İfadeler
`Ara` menüsündeki `Düzenli İfadeler` seçeneği açılırsa gelişmiş desen araması yapılır.
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
İlk satır sabit kalır.
Yanındaki `+` düğmesiyle alta yeni arama satırı açılır.

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
Bu alan aksan duyarsız çalışır.
Yani `BURHAN AYTEKIN` için `burhan aytekin` diye de arayabilirsin.
Arama satırlarında veya editör filtresinde Enter'a basarsan arama başlar.

### 10.5 Sonuç Listesi
Sonuç listesi salt-okunurdur.
Burada yanlışlıkla veri düzenlenmez.
Sütun başlıklarına göre genişlik ayarlanabilir.
Sütun başlığına sağ tıklarsan istediğin sütunu gizleyip yeniden gösterebilirsin.
Bu tercihler pencere tekrar açıldığında hatırlanır.
Bulunan ifadeler sonuç hücrelerinde işaretlenir.

### 10.6 Sağ Tık Menüsü
Arşiv sonucunda sağ tık menüsünde şunlar vardır:
- `Kopyala`
- `Tarihe Git`
- `Kaynağı Klasörde Göster`

### 10.7 Dışa Aktarma
`Dışa Aktar` düğmesiyle sonuçları:
- `CSV`
- `XLS`

olarak kaydedebilirsin.

### 10.8 Sonuç Tarihi
Tarih `gün.ay.yıl` biçiminde gösterilir.

### 10.9 Durum Çubuğu
Pencerenin altında ayrı bir durum çubuğu vardır.
Arama sürerken, bittiğinde ve hata olduğunda kısa durumu burada görürsün.

### 10.10 Uyarılar
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
- Her kanal yalnızca kendi sözlüğünü kullanır.
- Varsa gelişmiş yazım denetimi son aşamada devreye girer.
- Başlık düzeltilirse Cinegy metninde düzeltilmiş başlık ilk satıra, orijinal başlık hemen alt satıra yazılır.

### 12.2 Otomatik Başlık Yazım Denetimi
`Araçlar > Haber Başlığı Yazım Denetimi > Otomatik Yazım Denetimi` seçeneğiyle açılıp kapatılır.
Kapatılırsa yeni okunan haberlerde otomatik Türkçe karakter düzeltmesi uygulanmaz.
İstenirse sağ tık menüsündeki `Yazımı Düzelt` komutuyla satır satır uygulanabilir.

### 12.3 A NEWS İstisnası
A NEWS İngilizce kanal olarak kabul edilir.
Bu kanalda Türkçe yazım denetimi otomatik ya da manuel fark etmeksizin Türkçe karakter üretmez.
Kanal sözlüğündeki özel kullanıcı düzeltmeleri yine çalışır.

### 12.4 Sağ Tık Bağlam Menüsü
Haber listesinde sağ tık açılan menünün teknik adı `bağlam menüsü` ya da `context menu`dür.
Bu menüden:
- `Yazımı Düzelt`
- `Yazımı Geri Al`
- `Seçili Haberi Güncelle`
- `Haber Kodunu Gizle`
- `Yalnızca Bu Haber Kodunu Göster`
- `Filtreyi Geri Al`
- `Filtreleri Temizle`
- `Sayfayı Yenile`
- `Veritabanını Güncelle`
komutlarına ulaşılabilir.

### 12.5 Başlık Sözlüğü ve Güvenli Düzeltme
Yazım denetimi artık daha temkinlidir.
Amaç, mümkün olduğunca eksik Türkçe karakterleri düzeltmektir.
Örnek:
- `MILLI -> MİLLİ`
- `OZET -> ÖZET`
- `DIN SAVASI -> DİN SAVAŞI`
- `COKUSU -> ÇÖKÜŞÜ`

Çok sayıda başlık eski mantıkla bozulduysa en güvenli yol yeni sürümde `Veritabanını Güncelle` çalıştırmaktır.

## 13. Renkler ve Liste Görünümü

### 13.1 Haber Kodu Renkleri
Haber listesinde bir satıra sağ tıklayıp `Renk Ata` menüsünden haber koduna renk verilebilir.
Arka plan ve yazı rengi ayrı ayrı atanabilir.
İlk kurulumda hiçbir renk gelmez; kullanıcı sonradan belirler.

### 13.2 Eski Tarihli Haberler
Listede görünen eski tarihli haberler için ayrı satır rengi ve yazı rengi atanabilir.

### 13.3 Pencere Oranı
Haber listesi ile metin önizlemesi arasındaki bölme oranı artık korunur.
Bir kez kendi kullanımına göre ayarladıysan program bu oranı bozmamaya çalışır.

## 14. Hatırlama Seçenekleri

### 14.1 Kaldığım Günü Hatırla
`Görünüm > Kaldığım Günü Hatırla` açıksa program bir sonraki açılışta son kullanılan tarihle başlar.

### 14.2 Pencereyi Mevcut Konuma Sabitle
Pencerenin genel boyutu ve konumu kaydedilir.
Bu ayar ayrı, son gün hatırlama ayarı ayrıdır.
- Yazım denetimi artık daha temkinli çalışır; anlam tahmini yerine önce güvenli Türkçe karakter onarımı yapmaya çalışır.

### 12.2 Nereden Yönetilir
- `Araçlar > Başlık Sözlüğü`
- `Araçlar > Kanal Kuralları`
- `Araçlar > Sözlük Paketini Yönet`

### 12.3 Kaydetme Davranışı
Başlık Sözlüğü penceresindeki ekleme ve düzenlemeler pencere kapanırken otomatik kaydedilir.
Bu pencere yalnızca aktif kanalın sözlüğünü düzenler.
İstersen `Kapat` düğmesiyle çıkabilirsin; kaydedilmemiş değişiklikler yine saklanır.

### 12.4 Örnek Girişler
- `ERDOGAN -> ERDOĞAN`
- `ISTANBUL -> İSTANBUL`
- `TURKIYE -> TÜRKİYE`

### 12.5 Sözlük Paylaşımı
Bir kanaldaki sözlüğü başka kullanıcıyla paylaşmak için `Araçlar > Sözlük Paketini Yönet` ekranını kullan.
Buradan aktif kanalın sözlüğünü dışa aktarabilir, gelen bir JSON dosyasını yine aktif kanala içe aktarabilirsin.
İçe aktarma mevcut kanal sözlüğüne ekleme/güncelleme yapar; diğer kanallar etkilenmez.

### 12.6 Satır Satır Yazımı Düzeltme
Haber listesinde bir satıra sağ tıklarsan:
- `Yazımı Düzelt`
- `Yazımı Geri Al`

komutları görünür.

Bu sayede otomatik düzeltmeyi tüm listeye bir anda uygulamak yerine haber haber kontrol ederek ilerleyebilirsin.

### 12.7 Veritabanında Ne Saklanır
Program başlıkla ilgili iki bilgiyi ayrı tutar:
- orijinal başlık
- düzeltilmiş başlık

Bu yüzden otomatik düzeltme bozulsa bile orijinal başlık tamamen kaybolmaz.
Ancak düzeltilmiş metin veritabanına yazıldığı için toplu bir düzeltmeden sonra en güvenli geri dönüş yolu şudur:

1. Gerekirse seçili haberde `Yazımı Geri Al` kullan
2. Çok sayıda kayıt etkilenmişse yeni sürümle `Zorla Yenile` çalıştır

`Zorla Yenile`, kaynak dosyadan yeniden üretim yaptığı için bozulmuş otomatik düzeltmeleri temizlemenin en güvenli yoludur.

## 13. Kanal Kuralları
Kanal kuralları, parser’ın hangi haber kodlarını tanıyacağını ve bazı kanal özel davranışları belirler.
Önemli not: Parser artık yalnızca burada tanımlı kodları haber kodu olarak kabul eder.
Kullanıcı kendi haber kodlarını bu ekrandaki üst alanlardan hızlıca ekleyebilir; sistem sabit bir kod listesine bağlı değildir.
Kanal Kuralları penceresindeki değişiklikler de kapanışta ve kanal değişiminde otomatik kaydedilir.
Bazı akışlarda taban kodun sonuna sayısal varyant gelebilir. Örneğin `SP` tanımlıysa `SP01`, `SP13` gibi dosya adları da aynı spor bülteni kodu altında yorumlanır; bunları tek tek eklemek gerekmez.
Bazı çok parçalı kodlar da esnek biçimde yorumlanır. Örneğin `K-STD` tanımlıysa `K STD`, `K - STD`, `K- STD` gibi yazımlar da aynı kod olarak kabul edilir.

### 13.1 Ekran Nasıl Kullanılır
- Üstte `kanal kodu` ve `açıklama` alanları vardır.
- `Hızlı Ekle` ile kod doğrudan tabloya eklenir.
- `Yeni Kanal Kodu Ekle` daha ayrıntılı düzenleme penceresini açar.
- Tabloda satıra sağ tıklayarak `Düzenle`, `Sil` ve `Kanal Geneli Başlık Kuralları` işlemlerine ulaşabilirsin.
- Bir satıra çift tıklarsan da `Düzenle` penceresi açılır.
- Sütun başlığına tıklarsan tablo o sütuna göre sıralanır.
- Sütun başlığına sağ tıklarsan sütun gizleyip gösterebilirsin.
- Sütun genişlikleri ve görünürlük tercihleri hatırlanır.

### 13.2 Kod Detayı ile Ne Yapılır
Bu pencerede seçili kod için şunlar tanımlanabilir:
- açıklamayı başlığa otomatik ekleme
- açıklamayı başlığın sonuna otomatik ekleme
- başlığa ön ek / son ek ekleme
- başlıktan belirli ifadeleri kaldırma
- sondaki saat veya sayıyı kaldırma

Örnek:
- `AZ` için başlık son ekine `VTR` yazarsan başlık zaten `VTR` ile bitmiyorsa otomatik eklenir.
- `A PARA` için `-APR` gibi bitişik bir son ek de aynı alandan verilebilir.
- `A-OD` gibi kodlarda haber metnindeki ilk başlık `ÖZEL DOSYA-...` biçiminde tek satır yazılır.
- Parantezli `YY-(OD)` gibi eski gösterimler artık sadeleştirilerek `YY-OD` biçiminde görünür.

### 13.2 Mevcut Kuralları Görme
Tabloda artık sadece haber kodu ve açıklama değil, şu özetler de görünür:
- başlık ön eki / son eki
- başlıktan silinen ifadeler
- sondaki sayı silme durumu

### 13.3 Kanal Geneli Başlık Temizliği
`Kanal Geneli Başlık Kuralları` artık ayrı pencerede açılır.
Buradan:
- başlığa genel ön ek ekleyebilir
- başlığa genel son ek ekleyebilir
- başlıktan silinecek ifadeleri girebilir
- sondaki saat/sayıları kaldırmayı açabilirsin
- `Sembol ile Başlayan Başlıkları Gizle` ayarını kanal bazında açıp kapatabilirsin

Önemli ayrım:
- `+SES` gibi gerçekten tanımlı bir haber kodu varsa bu kayıt haber olarak kalır
- yalnızca genel sembol başlığı gibi duran kayıtlar gizlenir

Örnek:
- A PARA için `-APR` son eki burada tutulur
- `1300, 1430` gibi ifadeler istenirse kaldırılabilir

### 13.4 Güncellemede Korunur mu
Evet. Kanal kuralları artık kullanıcı verisi alanında tutulur.
Bu yüzden update paketi kurulurken kullanıcıya özel haber kodları korunur.

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

### 18.1 Haber Listesinde Hızlı Gezinme
Haber listesi odaktayken doğrudan harf yazabilirsin.
Program yaklaşık 1 saniyelik kısa bir yazma penceresinde girilen harfleri birleştirir ve o önekle başlayan ilk habere gider.
`Backspace` son harfi siler, `Escape` ise birikmiş aramayı temizler.

### 18.2 Yazı Boyutu
`Görünüm > Yazı Boyutu` komutları artık odaklı çalışır.

- haber listesi seçiliyken kullanırsan liste boyutu değişir
- haber metni seçiliyken kullanırsan metin boyutu değişir

Bu sayede liste ve metin alanı ayrı ayrı büyütülüp küçültülebilir.

## 19. İpuçları
- Tooltip’leri takip et; ana ekran ve dialogların çoğunda açıklama var.
- Profil ekranında yanlış klasör seçmek, en sık yaşanan sorunlardan biridir.
- Parser değişikliği sonrası önce `Zorla Yenile` düşün.
- Arşiv aramada sonuçların kaynağına bakmak için `Kaynak` sütununu kullan.

## 20. Güncelleme Paketi

### 20.1 Neden Var
Her sürümde tüm klasörü yeniden dağıtmak yerine yalnızca uygulama dosyalarını güncellemek için kullanılır.
Bu sayede kullanıcı veritabanları, sözlükleri ve kanal kuralları korunur.

### 20.2 Kullanıcı Ne Yapacak
1. Gelen update zip dosyasını ayrı bir klasöre aç.
2. İçindeki `apply_update.bat` dosyasını çalıştır.
3. Açılan küçük pencerede mevcut `EGS Scrapper` kurulum klasörünü seç.
4. `Güncelle` düğmesine bas.
5. Araç önce uygulama dosyalarının yedeğini alır.
6. Sonra yeni dosyaları mevcut kurulumun üstüne kopyalar.

### 20.3 Neler Korunur
- `settings.json`
- `channel_rules.json`
- `databases`
- `logs`
- `error_reports`
- `channel_dictionaries`

### 20.4 Mini Sürüm Rehberi
Yeni sürüm hazırlarken kısa bir kontrol listesine ihtiyaç varsa proje klasöründeki `MINI_SURUM_REHBERI.md` dosyasını aç.
Bu dosya teknik ayrıntıya girmeden şu sırayı hatırlatır:

1. Değişikliği tamamla
2. Sürüm numarasını artır
3. Yedeği al
4. Sürüm notunu yaz
5. Gerekirse yardımı güncelle
6. `build_exe.bat` çalıştır
7. `prepare_release.bat` çalıştır
8. Doğru paketi kullanıcıya gönder

### 20.5 Güncelleme Penceresi
Update paketi artık siyah komut satırı yerine küçük bir pencere açar.
Bu pencerede:

- kurulu klasörü seçersin
- `Güncelle` düğmesine basarsın
- araç önce uygulama dosyalarının yedeğini alır
- sonra yeni dosyaları kopyalar

Kullanıcı verileri yine korunur.

## 21. Yeni Özellikler

### 21.1 Haber Listesi Sıralaması
Haber listesi artık Türkçe alfabe mantığıyla sıralanır.
Bu yüzden `Ç, Ğ, İ, Ö, Ş, Ü` içeren başlıklar listenin en sonuna düşmez.

Başlıkta kural gereği eklenen ön ek ve son ekler haber listesindeki alfabetik sıralamayı bozmasın diye liste için ayrı, daha sade bir başlık gösterimi kullanılır.
Özellikle `(OD)` gibi özel dosya haberlerinde listede haberin asıl adı görünür; `ÖZEL DOSYA-...` etiketi yüzünden alfabetik bulma zorlaşmaz.

### 21.1.1 Sütunlar
Haber listesi artık üç sütun gösterir:

- `Kod`
- `Açıklama`
- `Haber`

Bu sütunları başlık satırında sağ tıklayarak gizleyebilir veya tekrar gösterebilirsin.

### 21.2 Gizlenen Haber Sayısı
Durum çubuğu artık yalnızca görünen haber sayısını değil, gizlenen haber miktarını da yazar.
Bu özellikle kod filtresi, eski haber gizleme ve aynı başlık filtresi kullanılırken daha anlaşılır olur.

### 21.3 Haber Başlığı Yazım Denetimi
Bu ayar artık `Dosya > Ayarlar > Yazım` bölümündedir.

Seçenekler:
- `Kapalı`: yazım denetimi uygulanmaz
- `Elle`: yalnızca sağ tık bağlam menüsünden çalışır
- `Otomatik`: yeni okunan başlıklara kendisi uygular

`A NEWS` kanalında Türkçe yazım denetimi uygulanmaz.

### 21.4 Renklendirme ve Geri Alma
Haber kodu renklendirmeleri artık kanal kuralı mantığıyla çalışır.
Yani renk değişikliği yalnızca geçici görünüm ayarı değil, ilgili kanal kodunun kuralı gibi saklanır.

Görünüm ve renk değişikliklerinde `Ctrl+Z` ile geri alma, `Ctrl+Y` ile yeniden uygulama kullanılabilir.
Kanal Kuralı penceresindeki renk alanlarında `Temizle` düğmesi de vardır.

### 21.5 Listede Düzeltilmiş Başlıklar
Bu ayar açılırsa haber listesinde düzeltilmiş başlık gösterilir.
Ama alfabetik arama bozulmasın diye haber ön ekleri listede gizlenir.

Örnek:
- haber metninde: `ANALİZ- ORTADOĞU TÜRK DİPLOMASİSİ`
- listede: `ORTADOĞU TÜRK DİPLOMASİSİ`

### 21.6 İstatistikler
`Araçlar > İstatistikler` ekranından:

- tarih aralığı seçebilirsin
- kanal seçebilirsin
- yıl bazlı haber sayılarını görebilirsin
- ay bazlı haber sayılarını görebilirsin
- gün bazlı haber sayılarını görebilirsin
- editör bazlı haber sayılarını görebilirsin

### 21.7 Çok Eski Sürümden Update
Update paketi program dosyalarını günceller.
Ama daha önce parse edilip veritabanına yazılmış eski kayıtları otomatik yeniden üretmez.

Bu yüzden çok eski sürümden geliyorsan:
1. update'i uygula
2. programı aç
3. ilgili günlerde `Veritabanını Güncelle` çalıştır

Özellikle başlık davranışı, `ÖZEL DOSYA` mantığı, sözlük, parser veya yazım denetimi değiştiyse bu adım önemlidir.

### 21.6 Canlı İzleme
Canlı izleme yalnızca klasör bildirimiyle değil, kısa aralıklarla yaptığı kontrolle de çalışır.
Bu yüzden seçili gün açıkken yeni haber klasöre düşerse program bunu fark edip listeyi yenilemeye çalışır.

## 22. Terimler

### EGS
Yayın akışında kullanılan kaynak dosya biçimi.

### Kök Klasör
Tarih klasörlerinin altında yer aldığı ana kanal klasörü.

### Kod Filtresi
Belirli haber kodlarını gösteren veya gizleyen görünüm filtresi.

### Arşiv Arama
Geçmiş aylardaki veritabanları üzerinde arama yapan ekran.
