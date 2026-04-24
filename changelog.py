from version_info import APP_RELEASE_DATE, APP_VERSION


PREVIOUS_VERSION = "v1.8.45"
PREVIOUS_RELEASE_DATE = "2026-04-24"


V1825_NOTES = [
    "Veritabanı bakım işlemlerinden sonra çıkan bilgi pencereleri artık bekleme imleci bırakıldıktan sonra açılıyor; program donmuş hissi azaltıldı.",
    "Veritabanı bakım menüsünde `VACUUM` komutu `Veritabanını Toparla`, `ANALYZE` komutu `Arama İstatistiklerini Yenile` olarak Türkçeleştirildi.",
    "Yardım penceresindeki üst boşluk ve arama satırı yerleşimi yeniden düzenlendi; içerik artık üstten daha düzgün başlıyor.",
    "`build_exe.bat` derleme sonunda dağıtım klasörüne boş profil bilgileri içeren bir `settings.json` bırakıyor; yeni EXE ilk açılışta temiz profil akışıyla başlıyor.",
    "Yardım ekranında konu başlığı seçildiğinde artık yalnızca o başlığa ait bölüm görüntüleniyor; tam metin yerine bölüm bazlı wiki akışı sağlandı.",
    "Yardım ekranının üst arama satırı ve boşlukları yeniden düzenlendi; görünüm daha dengeli hale getirildi.",
    "Profil seçim ekranı, son eklenen kök klasör vurguları ve ipucu metinleri kaldırılarak önceki sade görünümüne geri döndürüldü.",
    "Yardım ekranı sol tarafta konu listesi, sağ tarafta içerik olacak şekilde wiki benzeri yapıya dönüştürüldü.",
    "Yardım içeriği ilk kurulum, kök klasör seçimi, arşiv arama, bakım, sık sorulan sorunlar ve terimler dahil olacak şekilde kapsamlı biçimde genişletildi.",
    "Yardım menüsündeki `Günlük Görüntüleyici` artık alt menü yerine doğrudan tek komut olarak yer alıyor.",
    "Başlangıç ekranındaki ipucu metni yenilendi; seçilmesi gereken kök klasör alanı daha görünür biçimde işaretlendi ve doğru/yanlış örneklerle açıklandı.",
    "Başlangıçtaki profil seçimi akışı geri getirildi; çok kullanıcılı ve çok kanallı kullanım için `Profili hatırla` ve `Bu pencereyi açılışta göster` seçenekleri yeniden aktif.",
    "Profil ekranı sadeleştirildi; `Profili hatırla` ve `Bu pencereyi açılışta göster` seçenekleri kaldırıldı, ayarların otomatik kaydolduğu metinle netleştirildi.",
    "Uygulama artık başlangıçta profil penceresini yalnızca zorunlu profil bilgileri eksikse gösteriyor; mevcut ayarlarla doğrudan açılıyor.",
    "Yardım menüsündeki son kullanıcıya dönük olmayan `Sağlık Kontrolü` ve `Smoke Test` komutları kaldırıldı.",
    "Arşiv Arama sonuç listesi artık salt-okunur; yanlışlıkla hücre düzenleme yapılamıyor.",
    "Arşiv Arama sonuçlarına `Editör` sütunu eklendi ve tam önizleme başlığında editör bilgisi gösteriliyor.",
    "Arşiv Arama sonuç tarihleri artık `gün.ay.yıl` biçiminde gösteriliyor.",
    "Arşiv Arama sonuç listesine sağ tık menüsü eklendi; `Kopyala`, `Tarihe Git` ve `Kaynağı Klasörde Göster` komutları kullanılabiliyor.",
    "Arşiv Arama penceresinde Enter artık yalnızca sorgu satırındayken aramayı çalıştırıyor; kod filtresi gibi düğmeler yanlışlıkla tetiklenmiyor.",
    "Ana üst çubukta kök klasör yolu kaldırıldı; logo ve profil bilgisi korunurken görünüm daha sade hale getirildi.",
    "Arşiv Arama tamamlandığında, hata veren veritabanı sayısı artık durum satırında gösteriliyor ve ayrıntılar uyarı penceresinden okunabiliyor.",
    "Arşiv aramada sessizce geçilen veritabanı hataları artık `EGS.ArchiveSearch` log kaynağına kanal, kaynak ve veritabanı yolu bilgisiyle yazılıyor.",
    "Ayar kaydı `SettingsSync` ile merkezileştirildi; sık değişen ana ekran tercihleri artık kısa gecikmeyle toplu kaydediliyor.",
    "Pencere kapanırken bekleyen ayar yazımları zorla tamamlanıyor; profil ve görünüm ayarları daha güvenli saklanıyor.",
    "Arşiv Arama sarmalayıcısında `should_cancel` desteği tamamlandı; arama artık hata vermeden iptal isteğine uyuyor.",
    "Arşiv Arama ilk açılışta başlangıç ve bitiş tarihlerini seçili günle dolduruyor; ilk satırda tek arama varsa `Ayrı/Birlikte/Hariç` seçimi gizleniyor.",
    "Arşiv Arama editör filtresi örnek isimleri `BURHAN AYTEKIN, METIN ALGUL` olarak güncellendi.",
    "`Profili Kaydet` düğmesi kaldırıldı; ana ekran görünüm tercihleri ve profil değişiklikleri artık otomatik kaydediliyor.",
    "Bul/Değiştir, Kanal Kuralları, Başlık Sözlüğü, Sözlük Paketi, Dış Veritabanı, Veritabanı Birleştirme, Yardım, Sürüm Notları ve Log pencerelerine ilk kullanım odaklı tooltip'ler eklendi.",
    "Arşiv Arama ekranına virgülle çoklu değer kabul eden ayrı `Editör Filtresi` alanı eklendi.",
    "Ana pencere, menü komutları ve Arşiv Arama ekranı boyunca ilk kullanım odaklı açıklayıcı tooltip'ler genişletildi.",
    "3. faz kapsamında Arşiv Arama ekranına `İptal` düğmesi eklendi; arama iptal isteğine uyumlu hale getirildi.",
    "Ana yükleme durum metni taranan dosya, işlenen dosya, önbellekten alınan dosya ve yazılan kayıt sayılarını gösterecek şekilde zenginleştirildi.",
    "3. fazın ilk adımı olarak arşiv arama işlemi arka plan işçisine taşındı; uzun aramalarda pencere artık daha akıcı kalıyor.",
    "Arşiv Arama ekranına arama durumu ve sonuç sayısı bilgisi eklendi.",
    "`Araçlar` menüsü alt menüler yerine ayraçlarla mantıksal gruplara ayrıldı.",
    "`Yazım Denetimini Yeniden Algıla` komutu daha anlaşılır isimle güncellendi; bu komut gelişmiş yazım denetimi bileşenini yeniden kontrol ediyor.",
    "`Geçmişi Tara` komutu `Dosya > Tarama ve Yenileme` içinden alınarak `Araçlar` menüsüne taşındı.",
    "`Önceki Günün Haberlerini Gizle` seçeneği adlandırma ve işaretleme mantığı açısından düzeltildi; işaretliyken gerçekten gizliyor.",
    "`Günlük Klasörünü Aç` komutu menüden kaldırıldı.",
    "`Arşiv Ara` komutu `Araçlar` menüsünden alınarak `Ara` menüsüne taşındı; tüm arama akışı tek başlık altında toplandı.",
    "`Veri ve Veritabanı` menüsü klasörler, dış veritabanları ve veritabanı bakımı olarak gruplanıp sadeleştirildi.",
    "`Veri ve Veritabanı` altında yeni `Veritabanı Bakımı` menüsü eklendi.",
    "Bu menüye veritabanı bütünlük kontrolü, `VACUUM` ile sıkıştırma ve `ANALYZE` ile sorgu istatistiği güncelleme komutları bağlandı.",
    "Bakım komutları çalışınca etkilenen veritabanı dosyaları ve sonuç özeti ayrıntılı pencerede gösteriliyor.",
    "A NEWS kanalında `Harfleri Çevir` artık İngilizce kuralla çalışıyor; Türkçe `i/ı/İ/I` eşlemeleri uygulanmıyor.",
    "Bu İngilizce dönüşüm hem üst menüdeki hem sağ tık menüsündeki metin dönüştürme komutlarına bağlandı.",
    "Zorla Yenile akışı, yeniden parse edilecek dosyaların eski DB kayıtlarını önce silip sonra yeniden yazar hale getirildi.",
    "Parser haber kodunu artık yalnızca kanal kurallarında tanımlı kullanıcı kodlarından seçiyor; `VO-AL-AQSA...` gibi dosyalarda kod `VO`, başlık `AL-AQSA...` olarak korunuyor.",
    "Yükleme worker'ına iptal desteği eklendi; yeni tarama başladığında eski worker daha güvenli şekilde durduruluyor.",
]


V1826_NOTES = [
    "Yedekleme betiği kendi `backups` klasörüne çarpmayacak şekilde düzeltildi; `prepare_release.bat` artık release öncesinde otomatik kaynak yedeği alıyor.",
    "Harici veritabanı birleştirme akışı güçlendirildi; `news` tablosu yoksa doğru hata veriyor, satır bazlı başarı/atlanan/hatalı sayıları kullanıcıya raporlanıyor.",
    "Günlük tarama akışı, kaynak klasörde silinmiş dosyalara ait eski DB ve cache kayıtlarını otomatik temizleyecek şekilde güncellendi.",
    "Başlık Sözlüğü ve Kanal Kuralları pencereleri artık kaydedilmemiş değişiklikleri kapanışta ve kapsam/kanal değişiminde otomatik saklıyor; kullanıcının eklediği sözlük ve haber kodu girdileri daha güvenli korunuyor.",
    "Haber listesine klavyeyle artımlı hızlı seçim eklendi; liste odaktayken yazılan harfler başlığı o önekle başlayan ilk habere atlatıyor.",
    "Backfill taramasında gün bazlı tarama hataları artık loglanıyor ve iptal isteği dosya döngüsü içinde de daha hızlı uygulanıyor.",
    "Smoke test; harici DB merge, sözlük kalıcılığı ve klavyeyle hızlı seçim senaryolarını kapsayacak şekilde genişletildi. Sağlık kontrolü de backfill dosyalarını izleyecek şekilde güncellendi.",
    "Yardım içeriği; klavyeyle hızlı gezinme, dinamik haber kodu ekleme ve sözlük değişikliklerinin kaydedilmesi akışlarını anlatacak şekilde güncellendi.",
]


V1827_NOTES = [
    "Kanal Kuralları penceresindeki `Boş satırları göster` seçeneği kaldırıldı; liste artık gereksiz boş satırlar üretmiyor ve `Satır Ekle` komutu doğrudan yeni satıra odaklanıyor.",
    "A SPOR için `SP` taban kodu varsayılan kurallara eklendi; `SP01`, `SP13` gibi sayısal varyantlar parser tarafından otomatik olarak `SP` ailesi altında çözümleniyor.",
    "Smoke test; spor bülteni sayısal kod varyantlarını ve Kanal Kuralları ekranındaki yeni satıra otomatik odaklanma davranışını doğrulayacak şekilde genişletildi.",
    "Yardım içeriği ve sürüm kaydı, sayısal kod varyantlarının nasıl yorumlandığını anlatacak şekilde güncellendi.",
]


V1828_NOTES = [
    "Kaynağı klasörde göster akışları ortak `explorer` yardımcı fonksiyonuna taşındı; kabuk komutları daha güvenli ve denetlenebilir hale getirildi.",
    "Ana veri yükleme akışındaki kritik geniş `except Exception` blokları daraltıldı; veritabanı, dosya sistemi ve UI hataları daha anlamlı hata türleriyle ayrıştırılıyor.",
    "Veritabanı birleştirme ve arşiv arama worker akışlarında da hata yakalama kapsamı sıkılaştırıldı; beklenmeyen hataların gizlenme riski azaltıldı.",
    "Sağlık kontrolü yeni kabuk yardımcı modülünü izleyecek şekilde güncellendi; yardım içeriğine Kanal Kuralları ekranındaki doğrudan yeni satıra odaklanma davranışı eklendi.",
]


V1829_NOTES = [
    "Eski `database_core` katmanı bağımsız veritabanı mantığı taşımayacak şekilde emekliye ayrıldı; dosya artık yeni veritabanı katmanına yönlenen ince bir uyumluluk sarmalı olarak çalışıyor.",
    "Smoke test, `database_core` uyumluluk katmanının aktif veritabanı yoluna yönlendiğini doğrulayacak şekilde genişletildi.",
    "Worker, pencere kapanışı, klasör tarama ve arşiv arama akışlarında kalan bazı geniş hata yakalama blokları daha dar hata türlerine indirildi; gerçek beklenmeyen hataların gizlenme riski biraz daha azaltıldı.",
    "Sağlık kontrolü `database_core` uyumluluk katmanını da izleyecek şekilde güncellendi.",
]


V1830_NOTES = [
    "Ayar yükleme, kural dosyası okuma, atomik dosya yazma, log temizleme ve pencere durumu saklama akışlarında kalan bazı geniş hata yakalama blokları daha dar hata türlerine indirildi.",
    "Uygulama başlangıcı ile backfill worker akışında hata kapsamı sıkılaştırıldı; beklenmedik hataların sessizce yutulma alanı biraz daha küçültüldü.",
    "Klasör tarama ve bazı destek akışlarında yalnızca beklenen dosya sistemi/çalışma zamanı hataları tutulacak şekilde temizlik yapıldı.",
    "Bu bakım turu `v1.8.30` altında kayıt altına alındı ve yeni sürüm öncesi kaynak yedeği oluşturuldu.",
]


V1831_NOTES = [
    "Kalan son genel `except Exception` blokları da dialog, düzenleme ve yardımcı akışlarda daraltıldı; hata yakalama artık daha hedefli hale geldi.",
    "Sözlük dışa/içe aktarma, log görüntüleme, veritabanı birleştirme ve kural kaydetme pencerelerinde yalnızca beklenen dosya ve veri hataları tutuluyor.",
    "Pano kopyalama ve benzeri küçük düzenleme yardımcılarında da çalışma zamanı hataları daha net ayrıştırıldı.",
    "Genel taramada uygulama kodunda hedeflenen geniş `except Exception` kullanımı kalmayacak seviyeye getirildi ve bu durum `v1.8.31` olarak kayıt altına alındı.",
]


V1832_NOTES = [
    "Ortak başlık sözlüğü kaldırıldı; her kanal artık yalnızca kendi sözlüğünü kullanıyor ve eski ortak sözlük girdileri ilk geçişte kanal sözlüklerine taşınıyor.",
    "Sözlük paylaşımı kanal bazlı import/export akışına dönüştürüldü; `Sözlük Paketini Yönet` penceresi artık aktif kanalın sözlüğünü dışa aktarır ve gelen paketi yine o kanala ekler.",
    "Kanal kuralları kullanıcı verisi alanına taşındı; böylece güncelleme paketleri kullanıcıların eklediği haber kodlarını ezmeden uygulanabiliyor.",
    "Release sürecine hafif update paketi hattı eklendi. `prepare_release.bat` artık tam paket yanında `apply_update.bat` kullanan ayrı bir güncelleme paketi de üretiyor.",
    "Yardım, README, smoke test ve sağlık kontrolü yeni kanal bazlı sözlük modeli ile güncelleme paketi akışını kapsayacak şekilde güncellendi.",
]


V1833_NOTES = [
    "Yeni `MINI_SURUM_REHBERI.md` dosyası eklendi; teknik olmayan, kısa ve adım adım sürüm çıkarma kontrol listesi proje içine kalıcı olarak yerleştirildi.",
    "README ve yardım içeriği mini sürüm rehberine yönlendirecek şekilde güncellendi; yeni sürüm hazırlarken tek yerden takip edilebilecek basit anlatım eklendi.",
    "Release hazırlama akışı mini sürüm rehberini portable ve update paketlerine de dahil edecek şekilde güncellendi.",
    "Sağlık kontrolü mini sürüm rehberi dosyasını da izleyecek şekilde genişletildi ve bu dokümantasyon güncellemesi `v1.8.33` olarak kayıt altına alındı.",
]


V1834_NOTES = [
    "Update akışı komut satırından çıkarıldı; `apply_update.bat` artık kullanıcıdan kurulu klasörü seçmesini isteyen basit bir pencere açıyor ve güncelleme öncesi yedeği bu arayüzden alıyor.",
    "Kanal Kuralları ekranı başlık sözlüğüne benzer hızlı ekleme alanıyla yenilendi; kanal kodları artık üstteki `kanal kodu + açıklama + ekle` akışıyla giriliyor ve `K STD`, `K - STD`, `K- STD` gibi yazımlar standart `K-STD` biçimine çevriliyor.",
    "Kanal kurallarına kod detayı ve kanal geneli başlık temizleme ayarları eklendi; kullanıcı artık seçili kod için başlığa etiket ekleme, haber metninin üstüne sabit satır koyma, başlıktan ifade kaldırma ve sondaki saat/sayıyı silme gibi kuralları kendisi tanımlayabiliyor.",
    "A PARA başlık son eki boşluksuz `-APR` olarak düzeltildi; Cinegy metni artık düzeltilmiş başlığı ilk satıra, orijinal başlığı hemen alt satıra birlikte yazıyor.",
    "Türkçe başlık düzeltme altyapısı `Wordfreq + RapidFuzz` desteğiyle güçlendirildi; `ERDOGAN`, `TURKIYE`, `MECLIS` gibi ASCII başlıklar Türkçe karakterlerle daha güvenli düzeltiliyor. Build ve test akışı da yeni altyapıyı kapsayacak şekilde güncellendi.",
]


V1835_NOTES = [
    "Yazım denetimi daha temkinli hale getirildi; sistem artık anlam tahmini yapmadan öncelikle güvenli Türkçe karakter onarımına odaklanıyor. Böylece `COKUSU -> ÇÖKÜŞÜ` gibi düzeltmeler korunurken `KURGUNUN -> KURUNUN` gibi agresif sapmalar büyük ölçüde engellendi.",
    "Haber listesi sağ tık menüsüne `Yazımı Düzelt` ve `Yazımı Geri Al` komutları eklendi; kullanıcı artık başlık düzeltmesini satır satır uygulayabilir veya seçili haberlerde temizleyebilir.",
    "Kanal Kuralları ekranındaki tablo genişletildi; mevcut kurallar için başlık ön/son eki, silinen ifadeler ve sondaki sayı silme durumu artık doğrudan listede görülebiliyor.",
    "Yazı boyutu ayarı odaklı hale getirildi; haber listesi seçiliyken liste boyutu, haber metni seçiliyken metin boyutu ayrı ayrı büyütülüp küçültülebiliyor.",
    "Yardım içeriği veritabanında orijinal/düzeltilmiş başlık davranışını, geri alma mantığını ve `Yenile / Zorla Yenile` farkını daha sade anlatacak şekilde güncellendi. Bu bakım turu `v1.8.35` olarak kayda alındı.",
]


V1836_NOTES = [
    "Başlık yazım denetimi artık menüden açılıp kapatılabiliyor; otomatik başlık düzeltmesi isteğe bağlı hale getirildi. A NEWS kanalında Türkçe yazım denetimi uygulanmıyor.",
    "`Yazımı Geri Al` akışındaki başlık çoğaltma hatası düzeltildi. Sağ tıkta `Yazımı Düzelt` artık doğrudan tıklanan satıra uygulanıyor ve `Seçili Haberi Güncelle` komutuyla kaynak dosyadan tek haber yeniden okunabiliyor.",
    "Canlı izleme altyapısı güçlendirildi; seçili tarih klasörü henüz oluşmamış olsa bile üst klasörler izleniyor. Boş gün sonradan dosya alırsa liste artık uygulamayı kapatıp açmadan oluşabiliyor.",
    "Arama ve filtre tarafı sadeleştirildi; arama kutusuna temizleme düğmesi eklendi, regex ana ekrandan kaldırılıp `Ara > Düzenli İfadeler` altına taşındı, örnek desenler menüden arama kutusuna eklenebilir hale geldi.",
    "Sağ tık bağlam menüsüne `Haber Kodunu Gizle`, `Yalnızca Bu Haber Kodunu Göster`, `Filtreyi Geri Al`, `Filtreleri Temizle`, `Sayfayı Yenile` ve `Veritabanını Güncelle` komutları eklendi.",
    "Kanal Kuralları ekranından `Metin Üst Etiketi` alanı kaldırıldı. `+` ile başlayan dosyaları gizleme davranışı kanal bazında açılıp kapatılabiliyor.",
    "Haber listesi için kod bazlı renk atama eklendi; kullanıcı satır ve yazı rengini haber koduna göre belirleyebiliyor. İstenirse eski tarihli haberler için ayrı renk atanabiliyor.",
    "Pencere bölme oranı ve son açılan gün artık hatırlanabiliyor. `Kaynağı Klasörde Göster` komutu Explorer ile daha doğru çalışacak şekilde düzeltildi. Güncelleme arayüzü UTF-8 olarak yeniden kaydedildi.",
    "Yardım içeriği, yeni menü adları, önbellek açıklaması, canlı izleme davranışı ve sağ tık bağlam menüsü komutlarıyla güncellendi. Bu tur `v1.8.36` olarak kayda alındı.",
]


V1837_NOTES = [
    "Kanal Kuralları ekranına üstte hızlı ekleme satırı eklendi; `kanal kodu + açıklama + Hızlı Ekle` akışıyla yeni kod girildiğinde filtre temizleniyor, kod standart biçime çevriliyor ve yeni satıra doğrudan odaklanılıyor.",
    "Kanal Kuralları ekranı sağ tık bağlam menüsü ve çift tıklama düzenleme akışıyla güçlendirildi. `Yeni Kanal Kodu Ekle` detay penceresi açıyor, `Düzenle` adı netleştirildi ve kanal geneli başlık kuralları ayrı pencerede açılıyor.",
    "Kanal kurallarına `açıklamayı başlığın sonuna ekle` davranışı eklendi; artık açıklama istenirse başlığın sonuna da otomatik yazılabiliyor.",
    "Sembollü haber kodları ile genel sembol başlıkları ayrıştırıldı. `+SES` gibi gerçek kodlar tanınmaya devam ederken listede haber kodu gösterimi sadeleşti; `+` işareti kullanıcıya görünen haber kodunda gösterilmiyor.",
    "`Sembol ile Başlayan Başlıkları Gizle` seçeneği Görünüm ve Ayarlar menülerine eklendi. Bu ayar kanal bazında saklanıyor ve gerçek sembollü haber kodlarını yanlışlıkla gizlemiyor.",
    "`Aynı Haber Başlıkları` menüsü sadeleştirildi; `Tümünü Göster` seçeneği aynı başlıklar altına taşındı. Düzenli ifade örnekleri de Yardım menüsündeki `Düzenli İfadeler` bölümüne alındı.",
    "Ayarlar üst menüden çıkarılıp `Dosya > Ayarlar` altına taşındı. Yeni Ayarlar penceresi kategori bazlı çalışıyor ve temel kullanıcı ayarlarını tek ekranda topluyor.",
    "Kaynak klasör boş görünüyorsa program artık o güne ait veritabanı kayıtlarını koruyor. Kullanıcıya uyarı gösteriliyor ve isterse `Bir daha gösterme` seçeneğiyle bu uyarıyı kapatabiliyor.",
    "`Yazım Altyapısını Denetle` komutu son kullanıcı menüsünden kaldırıldı; bu kontrol artık bakım amacıyla geliştirici tarafında tutuluyor.",
]

V1838_NOTES = [
    "Haber listesi artık kural eklerini alfabetik sıralamayı bozmayacak ayrı `liste başlığı` ile gösteriyor; böylece `ÖZEL DOSYA-...` gibi eklenmiş başlıklar listede aranırken asıl haber adına göre bulunabiliyor.",
    "Haber listesi sıralaması Türkçe alfabe mantığına göre güncellendi; `Ç, Ğ, İ, Ö, Ş, Ü` içeren başlıklar listenin sonuna düşmüyor.",
    "Durum çubuğu artık görünen haber sayısının yanında gizlenen haber miktarını da yazıyor.",
    "Canlı izleme klasör ağacı güçlendirildi; seçili günün klasörü, üst yıl klasörü ve mevcut alt klasörler birlikte izleniyor. Boş başlayan gün klasörüne sonradan dosya gelirse liste kendini daha kolay toparlıyor.",
    "`Dosya > Ayarlar` penceresi genişletildi. Başlık yazım denetimi artık `Kapalı / Elle / Otomatik` olarak seçilebiliyor.",
    "Sağ tık bağlam menüsündeki `Metni Kaydet` ifadesi `Kaydet` olarak sadeleştirildi, `Renk Ata` ifadesi `Renklendir` olarak güncellendi.",
    "Haber kodu renklendirmeleri kanal kuralı mantığına taşındı; satır rengi ve yazı rengi artık ilgili kanal koduyla birlikte saklanıyor. Kanal kodu düzenleme penceresine canlı renk önizlemesi eklendi.",
    "Görünüm ve renk ayarlarında temel geri alma / yineleme desteği eklendi; haber metni odakta değilken `Ctrl+Z` son ayar değişikliğini geri alır, `Ctrl+Y` tekrar uygular.",
    "Yeni `Araçlar > İstatistikler` penceresi eklendi. Tarih aralığı ve kanal seçerek yıl, ay, gün ve editör bazında haber sayılarını görebilirsin.",
    "Güncelleme arayüzü Türkçe metinlerle yeniden yazıldı ve UTF-8 BOM ile kaydedildi; `Güncelleme`, `Gözat`, `Hazır` gibi başlıklar artık bozuk görünmemeli.",
]

V1839_NOTES = [
    "Kanal Kuralı düzenleme penceresine satır rengi ve yazı rengi için `Temizle` düğmeleri eklendi; girilen renk kodunu silince artık önizleme tarafında stil hatası vermemeli.",
    "Haber listesi üç sütunlu hale getirildi: `Kod`, `Açıklama`, `Haber`. Kullanıcı başlıktaki sağ tık bağlam menüsünden istediği sütunu gizleyip tekrar gösterebilir.",
    "`(OD)` gibi özel durumlu haberlerde liste başlığı artık haberin asıl adına göre gösteriliyor. Örneğin `DS- (OD) ...` listede `ÖZEL DOSYA-...` diye değil, haber adıyla sıralanıyor; haber metnindeki düzeltilmiş başlık yine korunuyor.",
    "Eski veritabanı kayıtlarında kalmış hatalı liste başlıkları için de ek koruma eklendi; uygulama yükleme sırasında dosya adından temiz liste başlığını yeniden türetebiliyor.",
    "Canlı izlemeye ikinci güvenlik katmanı olarak kısa aralıklı klasör yoklaması eklendi. Windows bildirimini kaçırsa bile seçili gün klasöründeki yeni dosya veya silme değişikliği fark edilip liste yenilenebiliyor.",
    "Canlı izleme tetiklendiğinde aynı günün haberleri daha güvenli yenilensin diye yeniden tarama akışı güçlendirildi.",
]


PREVIOUS_VERSION_NOTES = V1839_NOTES


V1840_NOTES = [
    "Canlı izleme katmanı hafifletildi. Ağır klasör imzası taraması kaldırılarak izleme tarafındaki yavaşlama azaltıldı; canlı yenileme artık gereksiz `Zorla Yenile` yerine normal günlük yenileme mantığıyla çalışıyor.",
    "Daha önce parse edilmiş bir gün, dosya değişmemişse veritabanı ve önbellekten okunmaya devam ediyor. Canlı izleme ya da `Sayfayı Yenile` yalnızca yeni veya değişen dosyaları yeniden işler.",
    "`Metni Kaydet` düğmesi `Kaydet` olarak sadeleştirildi.",
    "`AZ / ANALİZ` haberleri listede artık sade başlıkla görünür. `ANALİZ-...` eki alfabetik aramayı bozmaz; düzeltme yine haber metninde korunur.",
    "`AZ- APS- KAC POSETE SIGAR KI DUNYA_OGLE` gibi düzensiz başlıklarda `APS` temizlendikten sonra kalan fazla tire ve çift boşluk sorunu giderildi. Başlık artık `ANALİZ- KAC POŞETE SIĞAR KI DÜNYA VTR` gibi daha temiz üretilir.",
    "A HABER `AZ` kodu için varsayılan `VTR` son eki eklendi. Başlık zaten `VTR` ile bitiyorsa tekrar eklenmez; bu mantık Kanal Kuralları içindeki başlık son eki alanıyla diğer kodlara da uygulanabilir.",
]


V1841_NOTES = [
    "16 Nisan gibi önce boş görünen, sonra klasöre dosya düşen günlerde yaşanan ana sorun çözüldü. Tarih klasörü çözümleme mantığı düzeltilerek yanlış `...\\HABER\\HABER\\...` yoluna bakma ihtimali giderildi.",
    "Tarih klasörü çözümünde olumsuz sonuçları bellekte tutan önbellek kaldırıldı. Böylece bir gün açıldığında klasör henüz yoksa, daha sonra dosya gelince `Sayfayı Yenile` ve canlı izleme artık doğru klasörü yeniden görebilir.",
    "Canlı izleme ve yenileme sorunlarını teşhis etmek için geliştirici tarafında `tools/day_scan_debugger.py` eklendi. Bu araç seçili gün için hangi klasöre bakıldığını, kaç dosya bulunduğunu ve veritabanında kaç kayıt olduğunu tek seferde gösterir.",
]


V1844_NOTES = [
    "Tarama logları sadeleştirildi. Tek tek yüzlerce dosya için bilgi satırı yazmak yerine, ayıklanan ve gizlenen dosya sayıları artık tarama sonunda özet olarak kaydediliyor; günlük log dosyaları daha okunur hale geldi.",
    "Ana yükleme akışındaki kritik veritabanı ve önbellek hataları artık çıplak `traceback` yerine açıklayıcı log kayıtlarıyla tutuluyor. Böylece sorun çıkarsa hangi adımda, hangi dosyada olduğunu anlamak daha kolay.",
    "Uygulama açılışında exception hook kurulamazsa veya ana pencere açılamazsa başlangıç hataları da standart log sistemine düşecek şekilde toparlandı.",
]


V1845_NOTES = [
    "Arşiv Arama penceresine `Dışa Aktar` eklendi; sonuçlar artık CSV veya Excel'in açabildiği XLS formatında dışa alınabiliyor.",
    "Arşiv Arama'da arama satırlarında ve editör filtresinde Enter tuşuna basmak aramayı başlatıyor. Bulunan ifadeler sonuç tablosunda hücre bazında, alt önizlemede ise metin içinde vurgulanıyor.",
    "Güncelleme arayüzüne temel sürüm kontrolü eklendi. Çok eski sürüm tespit edilirse kullanıcıya uyarı gösteriliyor ve güncellemeden sonra `Veritabanını Güncelle` çalıştırması öneriliyor.",
    "Ana haber listesine `Düzeltilmiş Başlıkları Göster` seçeneği eklendi. Bu görünümde düzeltilmiş başlıklar listelenir; ancak `ANALİZ-`, benzeri ön ekler alfabetik düzeni bozmasın diye gizlenir.",
]


PREVIOUS_VERSION_NOTES = V1845_NOTES


CURRENT_VERSION_NOTES = [
    "Özel dosya haberleri artık güncel akışta da tek satır başlıkla üretiliyor. `A- ... (OD)` gibi dosyalar haber metninde `ÖZEL DOSYA-...` olarak yazılıyor; başlık üstüne ayrı `ÖZEL DOSYA` satırı eklenmiyor.",
    "Haber kodu gösterimi sadeleştirildi. Parantezli `YY-(OD)`, `A-(OD)` gibi kodlar artık kullanıcıya `YY-OD`, `A-OD` olarak gösteriliyor; eski kayıtlar ve eski veritabanları ise geriye dönük uyumla okunmaya devam ediyor.",
    "Veritabanından yüklenen eski özel dosya kayıtları ekrana gelirken sessizce onarılıyor. Daha önce ayrı satır `ÖZEL DOSYA` ile yazılmış kayıtlar yeni kurala göre birleşik başlık biçiminde gösterilebiliyor.",
    "Smoke test, özel dosya haberlerinde yeni `-OD` kod gösterimini ve tek satır `ÖZEL DOSYA-...` başlık üretimini doğrulayacak şekilde genişletildi.",
]


CHANGELOG_HISTORY = [
    {
        "version": PREVIOUS_VERSION,
        "date": PREVIOUS_RELEASE_DATE,
        "notes": PREVIOUS_VERSION_NOTES,
    },
    {
        "version": "v1.8.34",
        "date": "2026-04-20",
        "notes": V1834_NOTES,
    },
    {
        "version": "v1.8.33",
        "date": "2026-04-20",
        "notes": V1833_NOTES,
    },
    {
        "version": "v1.8.32",
        "date": "2026-04-20",
        "notes": V1832_NOTES,
    },
    {
        "version": "v1.8.31",
        "date": "2026-04-20",
        "notes": V1831_NOTES,
    },
    {
        "version": "v1.8.30",
        "date": "2026-04-20",
        "notes": V1830_NOTES,
    },
    {
        "version": "v1.8.29",
        "date": "2026-04-19",
        "notes": V1829_NOTES,
    },
    {
        "version": "v1.8.28",
        "date": "2026-04-19",
        "notes": V1828_NOTES,
    },
    {
        "version": "v1.8.27",
        "date": "2026-04-19",
        "notes": V1827_NOTES,
    },
    {
        "version": "v1.8.26",
        "date": "2026-04-19",
        "notes": V1826_NOTES,
    },
    {
        "version": "v1.8.25",
        "date": "2026-04-17",
        "notes": V1825_NOTES,
    },
    {
        "version": "v1.8.13",
        "date": "2026-04-17",
        "notes": [
            "Arşiv Arama ekranına virgülle çoklu değer kabul eden ayrı `Editör Filtresi` alanı eklendi.",
            "Ana pencere, menü komutları ve Arşiv Arama ekranı boyunca ilk kullanım odaklı açıklayıcı tooltip'ler genişletildi.",
        ],
    },
    {
        "version": "v1.8.12",
        "date": "2026-04-17",
        "notes": [
            "3. faz kapsamında Arşiv Arama ekranına `İptal` düğmesi eklendi; arama iptal isteğine uyumlu hale getirildi.",
            "Ana yükleme durum metni taranan dosya, işlenen dosya, önbellekten alınan dosya ve yazılan kayıt sayılarını gösterecek şekilde zenginleştirildi.",
            "3. fazın ilk adımı olarak arşiv arama işlemi arka plan işçisine taşındı; uzun aramalarda pencere artık daha akıcı kalıyor.",
            "Arşiv Arama ekranına arama durumu ve sonuç sayısı bilgisi eklendi.",
            "`Araçlar` menüsü alt menüler yerine ayraçlarla mantıksal gruplara ayrıldı.",
        ],
    },
    {
        "version": "v1.8.11",
        "date": "2026-04-17",
        "notes": [
            "3. fazın ilk adımı olarak arşiv arama işlemi arka plan işçisine taşındı; uzun aramalarda pencere artık daha akıcı kalıyor.",
            "Arşiv Arama ekranına arama durumu ve sonuç sayısı bilgisi eklendi.",
            "`Araçlar` menüsü alt menüler yerine ayraçlarla mantıksal gruplara ayrıldı.",
            "`Yazım Denetimini Yeniden Algıla` komutu daha anlaşılır isimle güncellendi; bu komut gelişmiş yazım denetimi bileşenini yeniden kontrol ediyor.",
            "`Geçmişi Tara` komutu `Dosya > Tarama ve Yenileme` içinden alınarak `Araçlar` menüsüne taşındı.",
        ],
    },
    {
        "version": "v1.8.10",
        "date": "2026-04-17",
        "notes": [
            "`Araçlar` menüsü ikinci kez sadeleştirildi; `Bakım` alt menüsü kaldırıldı.",
            "`Yazım Denetimini Yeniden Yükle` komutu `Dil ve Kurallar` içine alındı; menü dili işlevle daha uyumlu hale getirildi.",
            "`Kodları Filtreleme` komutu yeni `Filtreler` alt menüsüne taşındı.",
            "`Arşiv Ara` komutu `Araçlar` menüsünden alınarak `Ara` menüsüne taşındı; tüm arama akışı tek başlık altında toplandı.",
            "`Veri ve Veritabanı` menüsü klasörler, dış veritabanları ve veritabanı bakımı olarak gruplanıp sadeleştirildi.",
        ],
    },
    {
        "version": "v1.8.9",
        "date": "2026-04-17",
        "notes": [
            "`Arşiv Ara` komutu `Araçlar` menüsünden alınarak `Ara` menüsüne taşındı; tüm arama akışı tek başlık altında toplandı.",
            "`Veri ve Veritabanı` menüsü klasörler, dış veritabanları ve veritabanı bakımı olarak gruplanıp sadeleştirildi.",
            "`Kodları Filtreleme` komutu tek başına kalan alt menüden çıkarılıp doğrudan `Araçlar` menüsüne alındı.",
            "`Veri ve Veritabanı` altında yeni `Veritabanı Bakımı` menüsü eklendi.",
            "Bu menüye veritabanı bütünlük kontrolü, `VACUUM` ile sıkıştırma ve `ANALYZE` ile sorgu istatistiği güncelleme komutları bağlandı.",
        ],
    },
    {
        "version": "v1.8.8",
        "date": "2026-04-17",
        "notes": [
            "`Veri ve Veritabanı` altında yeni `Veritabanı Bakımı` menüsü eklendi.",
            "Bu menüye veritabanı bütünlük kontrolü, `VACUUM` ile sıkıştırma ve `ANALYZE` ile sorgu istatistiği güncelleme komutları bağlandı.",
            "Bakım komutları çalışınca etkilenen veritabanı dosyaları ve sonuç özeti ayrıntılı pencerede gösteriliyor.",
            "A NEWS kanalında `Harfleri Çevir` artık İngilizce kuralla çalışıyor; Türkçe `i/ı/İ/I` eşlemeleri uygulanmıyor.",
            "Bu İngilizce dönüşüm hem üst menüdeki hem sağ tık menüsündeki metin dönüştürme komutlarına bağlandı.",
        ],
    },
    {
        "version": "v1.8.7",
        "date": "2026-04-17",
        "notes": [
            "A NEWS kanalında `Harfleri Çevir` artık İngilizce kuralla çalışıyor; Türkçe `i/ı/İ/I` eşlemeleri uygulanmıyor.",
            "Bu İngilizce dönüşüm hem üst menüdeki hem sağ tık menüsündeki metin dönüştürme komutlarına bağlandı.",
            "Zorla Yenile akışı, yeniden parse edilecek dosyaların eski DB kayıtlarını önce silip sonra yeniden yazar hale getirildi.",
            "Parser haber kodunu artık yalnızca kanal kurallarında tanımlı kullanıcı kodlarından seçiyor; `VO-AL-AQSA...` gibi dosyalarda kod `VO`, başlık `AL-AQSA...` olarak korunuyor.",
            "Yükleme worker'ına iptal desteği eklendi; yeni tarama başladığında eski worker daha güvenli şekilde durduruluyor.",
        ],
    },
    {
        "version": "v1.8.6",
        "date": "2026-04-17",
        "notes": [
            "Zorla Yenile akışı, yeniden parse edilecek dosyaların eski DB kayıtlarını önce silip sonra yeniden yazar hale getirildi.",
            "Parser haber kodunu artık yalnızca kanal kurallarında tanımlı kullanıcı kodlarından seçiyor; `VO-AL-AQSA...` gibi dosyalarda kod `VO`, başlık `AL-AQSA...` olarak korunuyor.",
            "Yükleme worker'ına iptal desteği eklendi; yeni tarama başladığında eski worker daha güvenli şekilde durduruluyor.",
            "Arşiv taraması için iptal düğmesi eklendi ve çalışan backfill işlemi kullanıcı tarafından durdurulabilir hale geldi.",
            "Worker ve backfill parse hataları ayrı parse hata raporuna da kaydediliyor.",
        ],
    },
    {
        "version": "v1.8.5",
        "date": "2026-04-17",
        "notes": [
            "Parser haber kodunu artık yalnızca kanal kurallarında tanımlı kullanıcı kodlarından seçiyor; `VO-AL-AQSA...` gibi dosyalarda kod `VO`, başlık `AL-AQSA...` olarak korunuyor.",
            "Yükleme worker'ına iptal desteği eklendi; yeni tarama başladığında eski worker daha güvenli şekilde durduruluyor.",
            "Arşiv taraması için iptal düğmesi eklendi ve çalışan backfill işlemi kullanıcı tarafından durdurulabilir hale geldi.",
            "Worker ve backfill parse hataları ayrı parse hata raporuna da kaydediliyor.",
            "Smoke test bu parser regresyonunu kapsayacak şekilde genişletildi.",
        ],
    },
    {
        "version": "v1.8.4",
        "date": "2026-04-17",
        "notes": [
            "Merkezi `NewsItem` veri modeli eklendi; haber nesneleri parser, worker, UI ve veritabanı arasında tek tip alanlarla taşınır hale geldi.",
            "Yeni `NewsRepository` katmanı ana pencere ve düzenleme akışındaki doğrudan veritabanı çağrılarını sadeleştirdi.",
            "`NewsIngestService` parse, başlık düzeltme ve dosya stat toplama sorumluluklarını tek noktada birleştirdi.",
            "Arşiv backfill worker'ı ve yükleme worker'ı yeni servis ve repository katmanını kullanacak şekilde ayrıştırıldı.",
            "Smoke test ve health check kapsamı yeni veri modeli ve servis katmanını doğrulayacak şekilde genişletildi.",
        ],
    },
    {
        "version": "v1.8.3",
        "date": "2026-04-17",
        "notes": [
            "Yazılabilir uygulama verileri kullanıcı profiline taşındı; settings, veritabanları, loglar, hata raporları ve sözlükler artık app-data altında tutuluyor.",
            "Eski proje klasöründeki settings, databases, error_reports ve sözlükler yeni veri konumuna otomatik kopyalanarak güvenli geçiş sağlandı.",
            "Settings ve sözlük kayıtları atomik yazımla kaydedilir hale getirildi; yarım kalan yazma durumlarında dosya bozulma riski azaltıldı.",
            "Tarama akışına desteklenmeyen uzantı filtresi ve worker dosya-hata logları eklendi.",
            "Smoke test gerçek kullanıcı settings ve veritabanlarından izole geçici app-data klasörüyle çalışacak şekilde güçlendirildi.",
        ],
    },
    {
        "version": "v1.8.2",
        "date": "2026-04-17",
        "notes": [
            "Yükleme worker'ları artık her tarama isteği için ayrı bir token ile izleniyor; eski worker sinyalleri yeni ekran durumunu bozmayacak şekilde yok sayılıyor.",
            "Haber yazma ve önbellek güncelleme akışı `on_worker_finished` içinde yerel SQLite bağlantısıyla tamamlanıyor; `self.conn` üzerinden yaşanan `NoneType` hatası giderildi.",
            "Eşzamanlı tarama, yenileme ve arşiv işlemlerinde veritabanı commit ve cache yazımı daha güvenli hale getirildi.",
        ],
    },
    {
        "version": "v1.8.1",
        "date": "2026-04-17",
        "notes": [
            "Dosya menüsüne Kapat komutu eklendi ve uygulama Ctrl+Q ile doğrudan kapatılabilir hale geldi.",
            "Görünüm menüsüne yazı boyutu ayarları eklendi; liste ve önizleme metni büyütülüp küçültülebilir hale geldi.",
            "Profil seçimi ekranına kullanıcı profil logosu alanı eklendi ve seçilen görsel üst çubukta kanal logosunun yanında gösterilmeye başlandı.",
            "Log altyapısı günlük dosya düzenini korurken boyut sınırı ve eski log temizliği ile daha kontrollü hale getirildi.",
            "Yardım içeriği editör odaklı geliştirme ve özelleştirme önerileriyle genişletildi.",
        ],
    },
    {
        "version": "v1.8.0",
        "date": "2026-04-17",
        "notes": [
            "A SPOR kanal logosu yeni görselle güncellendi ve kanal logosu akışı korunarak üst çubukta gösterilmeye devam etti.",
            "3. faz kapsamında gerçek smoke test betiği ve raporu eklendi; parser, veritabanı, arşiv arama ve offscreen pencere açılışı birlikte doğrulanır hale geldi.",
            "Menü yapısı Veri ve Veritabanı, Tarama ve Yenileme, Dil ve Kurallar, Arşiv ve Veri ve Tanılama başlıkları altında daha ürünleşmiş bir yapıya taşındı.",
            "Yardım menüsü içine Sağlık Kontrolü ve Smoke Test çalıştırma komutları eklendi.",
            "Portable build ve release akışına kanal logoları, kanal sözlükleri, ortak sözlük ve tanılama betikleri de dahil edildi.",
        ],
    },
    {
        "version": "v1.7.2",
        "date": "2026-04-17",
        "notes": [
            "Seçili kanal logosu deneysel olarak üst çubukta profil düğmesinin hemen önüne eklendi.",
            "A NEWS, A HABER, ATV, A SPOR ve A PARA için ayrı kanal logo dosyaları uygulamaya dahil edildi.",
            "Profil değiştirildiğinde üst çubuktaki kanal logosu anında yenilenir hale getirildi.",
            "Sürüm notları bu deneysel görsel güncellemeyi de kapsayacak şekilde güncellendi.",
        ],
    },
    {
        "version": "v1.7.1",
        "date": "2026-04-17",
        "notes": [
            "Bul / Değiştir ekranından tehlikeli olabilecek Tüm Yüklü Haberler kapsamı kaldırıldı.",
            "Bul / Değiştir ekranına Geçerli Haber Başlığı, Seçili Haber Başlıkları ve Tüm Haber Başlıkları kapsamları eklendi.",
            "Yardım penceresine yardım içinde arama satırı eklendi ve içerik markdown görünümünde daha okunur hale getirildi.",
            "Yardım içeriği normal arama, çoklu arama ve regex örnekleriyle genişletildi.",
            "Sürüm notları akışı bu sürümde de güncellendi ve yeni değişiklikler kayda geçirildi.",
        ],
    },
    {
        "version": "v1.7.0",
        "date": "2026-04-17",
        "notes": [
            "Ana liste ve arşiv aramada regex desteği eklendi.",
            "Haber metni sağ tık menüsü Türkçeleştirildi ve Harfleri Çevir komutları eklendi.",
            "Bul / Değiştir ekranı seçili haberler, listelenen haberler ve tüm yüklü haberler üzerinde çalışabilir hale geldi.",
            "Veritabanı yapısı aylık dosyalara taşındı; yeni kayıtlar kanal_ay_yıl biçiminde tutuluyor.",
            "Dosya adının sonundaki gün numarası başlık gösteriminden çıkarıldı ve önceki gün haberlerini göster/gizle seçeneği eklendi.",
            "Üst çubuktaki program adı kaldırıldı, haber listesi daha sıkı düz tablo görünümüne alındı ve app.py için başlatıcı bat eklendi.",
        ],
    },
    {
        "version": "v1.6.2",
        "date": "2026-04-17",
        "notes": [
            "Dış veritabanı yönetimi gerçek listeleme, ekleme ve kaldırma ekranına dönüştürüldü.",
            "Arşiv arama artık ana veritabanına ek olarak ayarlara kayıtlı dış veritabanlarını da tarıyor.",
            "Arşiv arama sonuçlarında aynı haber farklı veritabanlarında bulunsa bile tekilleştirme uygulanıyor.",
            "Harici veritabanı listesi ayarlara kalıcı olarak kaydediliyor ve yeniden açılışta korunuyor.",
        ],
    },
    {
        "version": "v1.6.1",
        "date": "2026-04-17",
        "notes": [
            "Sürüm notları akışı güncellendi; güncel sürüm bilgisi artık version_info ile senkron tutuluyor.",
            "Ana pencerenin tarih seçici alanı üst çubuğun sağ tarafına taşındı.",
            "Arşiv aramaya tarih aralığına ek olarak haber kodu filtresi eklendi.",
            "A NEWS başlık düzeltme akışı ortak sözlükten ayrıldı ve kendi kanal sözlüğüyle çalışır hale getirildi.",
            "Çift kayıt oluşturan yol farklılıkları ve kod/kategori görünürlüğü için yapılan stabilizasyonlar sürüm notlarına dahil edildi.",
        ],
    },
    {
        "version": "v1.6.0",
        "date": "2026-04-16",
        "notes": [
            "Proje yapısı klasörlere ayrılmaya hazır hale getirildi.",
            "Haber listesi model/view yapısına taşındı.",
            "Liste sıralama desteği eklendi.",
            "Çoklu seçim ve toplu kopyalama desteği eklendi.",
            "Büyük liste yüklerinde daha akıcı arayüz için altyapı iyileştirildi.",
            "Yeni mimari klasör bazında sabitlendi: core, data, dictionaries, models, watchers, parsing, dialogs, ui, actions.",
            "Canlı izleme, worker ve önbellek yapısı yeni mimariye göre düzenlendi.",
            "Başlık düzeltme sistemi ortak sözlük, kanal sözlüğü ve yazım denetimi sırasıyla çalışacak şekilde merkezileştirildi.",
            "Kod filtreleme, kanal kuralları ve arşiv arama pencereleri yeni yapıya göre sadeleştirildi.",
            "Veritabanı tarafında migration desteği eklendi.",
            "corrected_title, format_code, format_name, kj_lines, mtime ve size kolonları otomatik tamamlanır hale getirildi.",
            "Eski mimariden kalan bağımlılıkların temizlenmesi için stabilizasyon süreci başlatıldı.",
        ],
    },
    {
        "version": "v1.5.0",
        "date": "2026-04-16",
        "notes": [
            "UI donmalarını azaltmak için worker/thread altyapısı eklendi.",
            "Tarama ve yükleme için progress bar eklendi.",
            "Akıllı önbellek sistemi eklendi.",
            "Zorla yenile ve önbellek temizleme komutları eklendi.",
        ],
    },
    {
        "version": "v1.4.0",
        "date": "2026-04-16",
        "notes": [
            "Sözlük yapısı ortak sözlük ve kanala özel sözlük olarak ayrıldı.",
            "Sözlük içe aktarma ve dışa aktarma eklendi.",
            "A NEWS için de ayrı başlık sözlüğü desteği eklendi.",
            "Başlık düzeltme motoru ortak sözlük, kanal sözlüğü ve yazım denetimi sırasıyla çalışacak şekilde güncellendi.",
            "Pano Geçmişi menü maddesi kaldırıldı.",
            "Dış veritabanı içe aktarma ve birleştirme altyapısı eklendi.",
            "Kod filtreleme penceresi daha sıkı tablo görünümüne yaklaştırıldı.",
        ],
    },
    {
        "version": "v1.3.0",
        "date": "2026-04-16",
        "notes": [
            "Başlıktaki büyük program adı kaldırıldı.",
            "Koyu temada menü ayraçları daha görünür hale getirildi.",
            "Kodları Filtreleme penceresi sıkı ve üç sütunlu görünüme taşındı.",
            "Başlık düzeltme motoru büyük harf başlıklarda da çalışacak şekilde güncellendi.",
            "Dış veritabanı yönetimi eklendi.",
            "Arşiv arama artık dış veritabanlarını da kullanabilir hale geldi.",
            "Haber kaynağı artık klasörde seçili olarak açılıyor.",
        ],
    },
    {
        "version": "v1.2.1",
        "date": "2026-04-16",
        "notes": [
            "Uygulama içindeki üst bölümde görünen logo kaldırıldı; simge yalnızca pencere ve görev çubuğunda kullanılacak şekilde düzenlendi.",
            "Haber listesine sağ tık menüsü eklendi; Kaynağı Aç komutuyla dosyanın kendisine ulaşılabilir hale geldi.",
            "(OD)GAZIANTEP gibi bitişik özel dosya başlıkları doğru ayrıştırılmaya başlandı.",
            "ANALİZ-- benzeri çift tire üreten başlık birleştirme hatası düzeltildi.",
        ],
    },
    {
        "version": "v1.2.0",
        "date": "2026-04-16",
        "notes": [
            "Açılış penceresi sadeleştirildi. Klasör seçicide varsayılan yol C:\\DeeR yapıldı.",
            "Başlık sözlüğü yöneticisi eklendi.",
            "Bul / Değiştir ekranına sözlüğe ekle seçeneği eklendi.",
            "Kod filtresi için daha sade bir sihirbaz eklendi.",
            "A NEWS hariç kanallarda başlık için otomatik düzeltme ve ikinci satır önizleme eklendi.",
            "Arayüz sadeleştirildi, tekrar eden başlık ayarı menüye taşındı ve yerelleştirildi.",
            "Tooltipler genişletildi.",
        ],
    },
    {
        "version": "v1.1.0",
        "date": "2026-04-16",
        "notes": [
            "Farklı dosya son ekleri desteklendi: OGLE, AKSAM, SABAH ve benzeri yapılar okunabilir hale geldi.",
            "A SPOR ve A PARA kanal kodları eklendi.",
            "A PARA başlıklarına otomatik -APR desteği eklendi.",
            "COPLUK klasörü ve içeriği tamamen yok sayılacak şekilde tarama iyileştirildi.",
            "+ ile başlayan başlıklar her zaman gizlenecek şekilde kural eklendi.",
            "Veri klasörü, log klasörü ve veritabanı klasörü için Klasörde Göster komutları eklendi.",
            "Tekrar eden başlıklarda en yeni / en eski seçim desteği eklendi.",
            "Başlık temizleme mantığında (PKG)31 benzeri boşluk hataları düzeltildi.",
            "Veri dosyaları _internal dışına taşındı.",
        ],
    },
    {
        "version": "v1.0.0",
        "date": "2026-04-13",
        "notes": [
            "Sürüm sistemi merkezileştirildi.",
            "Program içi yardım, günlük görüntüleyici ve hata raporu sistemi eklendi.",
            "Ana pencere, arşiv arama, kod filtre ve kanal kuralları modüler yapıya geçirildi.",
            "Logo ve marka alanı düzenlendi.",
            "Kanal bazlı ayrıştırma kuralları güçlendirildi.",
            "Portable dağıtım için build ve release altyapısı hazırlandı.",
        ],
    },
    {
        "version": "v0.2.1",
        "date": "2026-04-12",
        "notes": [
            "Menü yapısı genişletildi.",
            "Kanal kuralları ekranı geliştirildi.",
            "Sonda geçen özel kodların algılanmasına destek eklendi.",
            "Tooltip ve sürüm notları güncellendi.",
        ],
    },
    {
        "version": "v0.2.0",
        "date": "2026-04-12",
        "notes": [
            "Kanal seçimi sabit listeye bağlandı: A NEWS, A HABER, ATV, A SPOR, A PARA.",
            "Kanal bazlı ve ay bazlı veritabanı yapısı kuruldu.",
            "Ayarları hatırlama desteği eklendi.",
            "Arşiv arama ve arşiv tarama altyapısı genişletildi.",
        ],
    },
    {
        "version": "v0.1.4",
        "date": "2026-04-11",
        "notes": [
            "SQLite veritabanı otomatik oluşturulup doldurulur hale getirildi.",
            "FTS5 tabanlı arşiv arama altyapısı eklendi.",
            "Tekrar eden başlıkları gizleme seçeneği eklendi.",
        ],
    },
    {
        "version": "v0.1.3",
        "date": "2026-04-10",
        "notes": [
            "Haber listesi iki sütunlu yapıya geçirildi.",
            "Tarih alanına önceki/sonraki gün okları eklendi.",
            "Bilgi penceresi ve temel sürüm notları eklendi.",
        ],
    },
]


def _build_current_entry() -> dict:
    notes = [note for note in CURRENT_VERSION_NOTES if str(note).strip()]
    if not notes:
        notes = ["Bu sürüm için notlar daha sonra eklenecek."]
    return {
        "version": APP_VERSION,
        "date": APP_RELEASE_DATE,
        "notes": notes,
    }


def get_changelog() -> list[dict]:
    current_entry = _build_current_entry()
    older_entries = [
        entry for entry in CHANGELOG_HISTORY
        if entry.get("version") != APP_VERSION
    ]
    return [current_entry, *older_entries]


CHANGELOG = get_changelog()
