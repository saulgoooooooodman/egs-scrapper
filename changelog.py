from version_info import APP_RELEASE_DATE, APP_VERSION


CURRENT_VERSION_NOTES = [
    "Yükleme worker'ları artık her tarama isteği için ayrı bir token ile izleniyor; eski worker sinyalleri yeni ekran durumunu bozmayacak şekilde yok sayılıyor.",
    "Haber yazma ve önbellek güncelleme akışı `on_worker_finished` içinde yerel SQLite bağlantısıyla tamamlanıyor; `self.conn` üzerinden yaşanan `NoneType` hatası giderildi.",
    "Eşzamanlı tarama, yenileme ve arşiv işlemlerinde veritabanı commit ve cache yazımı daha güvenli hale getirildi.",
]


CHANGELOG_HISTORY = [
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
