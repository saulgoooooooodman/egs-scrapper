from __future__ import annotations

from PySide6.QtGui import QAction


def build_main_window_menu(self):
    def _describe(action, text: str):
        action.setToolTip(text)
        action.setStatusTip(text)
        action.hovered.connect(lambda text=text: self.status_label.setText(text))

    menu_bar = self.menuBar()
    menu_bar.clear()

    file_menu = menu_bar.addMenu("Dosya")
    edit_menu = menu_bar.addMenu("Düzen")
    search_menu = menu_bar.addMenu("Ara")
    view_menu = menu_bar.addMenu("Görünüm")
    tools_menu = menu_bar.addMenu("Araçlar")
    help_menu = menu_bar.addMenu("Yardım")

    self.action_change_profile = QAction("Profili Değiştir", self)
    _describe(self.action_change_profile, "Kullanıcı adı, kanal ve kök klasör gibi profil bilgilerini değiştirir.")
    self.action_change_profile.triggered.connect(self.change_profile)
    file_menu.addAction(self.action_change_profile)

    self.action_open_settings = QAction("Ayarlar", self)
    _describe(self.action_open_settings, "Programın tüm temel ayarlarını ayrı pencerede açar.")
    self.action_open_settings.triggered.connect(self.open_settings_dialog)
    file_menu.addAction(self.action_open_settings)

    file_menu.addSeparator()

    database_menu = file_menu.addMenu("Veri ve Veritabanı")

    database_folders_menu = database_menu.addMenu("Klasörler")

    self.action_open_db_dir = QAction("Veritabanı Klasörünü Aç", self)
    _describe(self.action_open_db_dir, "Aylık veritabanı dosyalarının bulunduğu klasörü açar.")
    self.action_open_db_dir.triggered.connect(self.open_databases_folder)
    database_folders_menu.addAction(self.action_open_db_dir)

    self.action_open_data_dir = QAction("Veri Klasörünü Aç", self)
    _describe(self.action_open_data_dir, "Uygulamanın kullanıcı verilerini tuttuğu klasörü açar.")
    self.action_open_data_dir.triggered.connect(self.open_data_folder)
    database_folders_menu.addAction(self.action_open_data_dir)

    external_db_menu = database_menu.addMenu("Dış Veritabanları")

    self.action_manage_external_dbs = QAction("Dış Veritabanlarını Yönet...", self)
    _describe(self.action_manage_external_dbs, "Arşiv aramada kullanılacak harici veritabanlarını ekler veya kaldırır.")
    self.action_manage_external_dbs.triggered.connect(self.open_external_db_manager)
    external_db_menu.addAction(self.action_manage_external_dbs)

    self.action_merge_external_db = QAction("Veritabanı İçe Aktar / Birleştir...", self)
    _describe(self.action_merge_external_db, "Başka bir veritabanındaki kayıtları seçili kanala aktarır.")
    self.action_merge_external_db.triggered.connect(self.open_db_merge_dialog)
    external_db_menu.addAction(self.action_merge_external_db)

    db_maintenance_menu = database_menu.addMenu("Veritabanı Bakımı")

    self.action_db_integrity = QAction("Veritabanı Sağlığını Kontrol Et", self)
    _describe(self.action_db_integrity, "Seçili kanalın veritabanı dosyalarında bütünlük kontrolü yapar.")
    self.action_db_integrity.triggered.connect(self.run_database_integrity_check)
    db_maintenance_menu.addAction(self.action_db_integrity)

    self.action_db_vacuum = QAction("Veritabanını Toparla", self)
    _describe(self.action_db_vacuum, "Silinmiş alanları temizleyerek veritabanı dosyasını küçültür ve toparlar.")
    self.action_db_vacuum.triggered.connect(self.run_database_vacuum)
    db_maintenance_menu.addAction(self.action_db_vacuum)

    self.action_db_analyze = QAction("Arama İstatistiklerini Yenile", self)
    _describe(self.action_db_analyze, "Veritabanı arama istatistiklerini yenileyerek sorguların daha sağlıklı çalışmasına yardımcı olur.")
    self.action_db_analyze.triggered.connect(self.run_database_analyze)
    db_maintenance_menu.addAction(self.action_db_analyze)

    scan_menu = file_menu.addMenu("Tarama ve Yenileme")

    self.action_refresh = QAction("Sayfayı Yenile", self)
    _describe(self.action_refresh, "Seçili tarihin haberlerini yeniden tarar ve listeyi günceller.")
    self.action_refresh.setShortcut("F5")
    self.action_refresh.triggered.connect(self.load_news)
    scan_menu.addAction(self.action_refresh)

    self.action_force_refresh = QAction("Veritabanını Güncelle", self)
    _describe(self.action_force_refresh, "Seçili günün veritabanı kayıtlarını siler, dosyaları yeniden okur ve tekrar yazar.")
    self.action_force_refresh.triggered.connect(lambda: self.load_news(force_refresh=True))
    scan_menu.addAction(self.action_force_refresh)

    self.action_clear_cache = QAction("Önbelleği Temizle", self)
    _describe(self.action_clear_cache, "Dosya önbelleğini temizler; sonraki yenilemede dosyalar yeniden okunur.")
    self.action_clear_cache.triggered.connect(self.clear_cache)
    scan_menu.addAction(self.action_clear_cache)

    file_menu.addSeparator()

    self.action_close = QAction("Kapat", self)
    _describe(self.action_close, "Uygulamayı güvenli şekilde kapatır.")
    self.action_close.setShortcut("Ctrl+Q")
    self.action_close.triggered.connect(self.close)
    file_menu.addAction(self.action_close)

    self.action_cut = QAction("Kes", self)
    _describe(self.action_cut, "Seçili metni keser.")
    self.action_cut.setShortcut("Ctrl+X")
    self.action_cut.triggered.connect(self.cut_text)
    edit_menu.addAction(self.action_cut)

    self.action_copy = QAction("Kopyala", self)
    _describe(self.action_copy, "Aktif alandaki seçili metni veya seçili haberleri kopyalar.")
    self.action_copy.setShortcut("Ctrl+C")
    self.action_copy.triggered.connect(self.copy_active_context)
    edit_menu.addAction(self.action_copy)

    self.action_paste = QAction("Yapıştır", self)
    _describe(self.action_paste, "Panodaki metni aktif alana yapıştırır.")
    self.action_paste.setShortcut("Ctrl+V")
    self.action_paste.triggered.connect(self.paste_text)
    edit_menu.addAction(self.action_paste)

    self.action_select = QAction("Seç", self)
    _describe(self.action_select, "Odaklanıp önizleme metninde seçim yapmayı kolaylaştırır.")
    self.action_select.triggered.connect(self.focus_preview_text)
    edit_menu.addAction(self.action_select)

    self.action_select_all = QAction("Tümünü Seç", self)
    _describe(self.action_select_all, "Aktif alandaki tüm içeriği seçer.")
    self.action_select_all.setShortcut("Ctrl+A")
    self.action_select_all.triggered.connect(self.select_all_text)
    edit_menu.addAction(self.action_select_all)

    self.action_delete = QAction("Sil", self)
    _describe(self.action_delete, "Seçili metni siler.")
    self.action_delete.triggered.connect(self.delete_selected_text)
    edit_menu.addAction(self.action_delete)

    edit_menu.addSeparator()

    self.action_undo = QAction("Geri Al", self)
    _describe(self.action_undo, "Son düzenleme adımını geri alır.")
    self.action_undo.setShortcut("Ctrl+Z")
    self.action_undo.triggered.connect(self.undo_text)
    edit_menu.addAction(self.action_undo)

    self.action_redo = QAction("Yinele", self)
    _describe(self.action_redo, "Geri alınan son düzenlemeyi yeniden uygular.")
    self.action_redo.setShortcut("Ctrl+Y")
    self.action_redo.triggered.connect(self.redo_text)
    edit_menu.addAction(self.action_redo)

    case_menu = edit_menu.addMenu("Harfleri Çevir")

    self.action_upper = QAction("TÜMÜNÜ BÜYÜK", self)
    _describe(self.action_upper, "Seçili metni büyük harfe çevirir.")
    self.action_upper.triggered.connect(self.to_upper)
    case_menu.addAction(self.action_upper)

    self.action_lower = QAction("tümünü küçük", self)
    _describe(self.action_lower, "Seçili metni küçük harfe çevirir.")
    self.action_lower.triggered.connect(self.to_lower)
    case_menu.addAction(self.action_lower)

    self.action_title_case = QAction("İlk Harfler Büyük", self)
    _describe(self.action_title_case, "Seçili metinde kelime başlarını büyük harfe çevirir.")
    self.action_title_case.triggered.connect(self.to_title_case)
    case_menu.addAction(self.action_title_case)

    multi_select_menu = edit_menu.addMenu("Çoklu Seç")

    self.action_select_same_codes = QAction("Seçili haber kodlarını seç", self)
    _describe(self.action_select_same_codes, "Seçili haberlerle aynı koda sahip satırları topluca seçer.")
    self.action_select_same_codes.triggered.connect(self.select_same_codes)
    multi_select_menu.addAction(self.action_select_same_codes)

    self.action_select_other_codes = QAction("Seçili haberlerin dışındakileri seç", self)
    _describe(self.action_select_other_codes, "Seçili haberlerin kodları dışındaki satırları seçer.")
    self.action_select_other_codes.triggered.connect(self.select_other_codes)
    multi_select_menu.addAction(self.action_select_other_codes)

    self.action_find = QAction("Bul", self)
    _describe(self.action_find, "Ana arama kutusuna odaklanır.")
    self.action_find.setShortcut("Ctrl+F")
    self.action_find.triggered.connect(self.focus_search)
    search_menu.addAction(self.action_find)

    self.action_find_replace = QAction("Bul / Değiştir", self)
    _describe(self.action_find_replace, "Yüklü içerikte bul/değiştir işlemini açar.")
    self.action_find_replace.setShortcut("Ctrl+H")
    self.action_find_replace.triggered.connect(self.open_find_replace_dialog)
    search_menu.addAction(self.action_find_replace)

    self.action_find_next = QAction("Sonrakini Bul", self)
    _describe(self.action_find_next, "Önizleme metnindeki bir sonraki eşleşmeye gider.")
    self.action_find_next.setShortcut("F3")
    self.action_find_next.triggered.connect(self.find_next_in_preview)
    search_menu.addAction(self.action_find_next)

    self.action_find_prev = QAction("Öncekini Bul", self)
    _describe(self.action_find_prev, "Önizleme metnindeki bir önceki eşleşmeye gider.")
    self.action_find_prev.setShortcut("Shift+F3")
    self.action_find_prev.triggered.connect(self.find_prev_in_preview)
    search_menu.addAction(self.action_find_prev)

    search_menu.addSeparator()

    self.action_search_regex = QAction("Düzenli İfadeler", self)
    _describe(self.action_search_regex, "Arama kutusundaki ifadeyi regex olarak yorumlar.")
    self.action_search_regex.setCheckable(True)
    self.action_search_regex.triggered.connect(self.toggle_search_regex)
    search_menu.addAction(self.action_search_regex)

    regex_examples = [
        (".*", "Her şeyi eşleştirir."),
        (".+", "Boş olmayan içeriği eşleştirir."),
        ("\\d+", "Sayıları eşleştirir."),
        ("\\bERD", "Kelime başında ERD arar."),
        ("TRUMP.*ATEŞKES", "İki ifade arasındaki tüm metni kapsar."),
        ("^WEU", "WEU ile başlayan başlıkları bulur."),
        ("VTR$", "VTR ile biten başlıkları bulur."),
        ("[A-Z]{2,}", "Büyük harf bloklarını bulur."),
        ("?", "Tek başına regex değildir; önceki karakteri isteğe bağlı yapar."),
        ("*", "Tek başına regex değildir; önceki ifadeyi tekrarlar."),
    ]
    for pattern, description in regex_examples:
        action = QAction(pattern, self)
        _describe(action, description)
        action.triggered.connect(lambda _=False, pattern=pattern: self.insert_search_pattern(pattern))

    self.action_archive_search = QAction("Arşiv Ara", self)
    _describe(self.action_archive_search, "Tarih aralığında arşiv veritabanlarını tarayarak geçmiş kayıtları bulur.")
    self.action_archive_search.setShortcut("F7")
    self.action_archive_search.triggered.connect(self.open_archive_search)
    search_menu.addAction(self.action_archive_search)

    self.action_always_on_top = QAction("Her Zaman Üstte Göster", self)
    _describe(self.action_always_on_top, "Pencereyi diğer uygulamaların üzerinde sabitler.")
    self.action_always_on_top.setCheckable(True)
    self.action_always_on_top.triggered.connect(self.toggle_always_on_top)
    view_menu.addAction(self.action_always_on_top)

    self.action_live_watch = QAction("Canlı İzleme", self)
    _describe(self.action_live_watch, "Seçili tarihin klasörünü izler; yeni dosya gelince listeyi yeniler.")
    self.action_live_watch.setCheckable(True)
    self.action_live_watch.triggered.connect(self.toggle_live_watch)
    view_menu.addAction(self.action_live_watch)

    self.action_toggle_code = QAction("Haber Kodlarını Gizle", self)
    _describe(self.action_toggle_code, "Listede haber kodu sütununu açıp kapatır.")
    self.action_toggle_code.triggered.connect(self.toggle_code_column)
    view_menu.addAction(self.action_toggle_code)

    self.action_show_corrected_titles = QAction("Düzeltilmiş Başlıkları Göster", self)
    _describe(
        self.action_show_corrected_titles,
        "Listede düzeltilmiş başlığı gösterir. Başlık ön ekleri alfabetik düzeni bozmasın diye gizlenir.",
    )
    self.action_show_corrected_titles.setCheckable(True)
    self.action_show_corrected_titles.triggered.connect(self.toggle_show_corrected_titles_in_list)
    view_menu.addAction(self.action_show_corrected_titles)

    self.action_show_previous_day_news = QAction("Eski Haberleri Gizle", self)
    _describe(self.action_show_previous_day_news, "İşaretliyken dosya adından önceki güne ait olduğu anlaşılan kayıtları gizler.")
    self.action_show_previous_day_news.setCheckable(True)
    self.action_show_previous_day_news.triggered.connect(self.toggle_previous_day_news)
    view_menu.addAction(self.action_show_previous_day_news)

    self.action_toggle_symbol_titles = QAction("Sembol ile Başlayan Başlıkları Gizle", self)
    _describe(
        self.action_toggle_symbol_titles,
        "Seçili kanalda +, !, #, * ile başlayan genel başlıkları gizler. Gerçek haber kodu olarak tanımlı sembollü kodlar etkilenmez.",
    )
    self.action_toggle_symbol_titles.setCheckable(True)
    self.action_toggle_symbol_titles.triggered.connect(self.toggle_symbol_prefixed_titles)
    view_menu.addAction(self.action_toggle_symbol_titles)

    self.action_show_all_titles = QAction("Aynı Başlıklı Haberlerin Tümünü Göster", self)
    _describe(self.action_show_all_titles, "Aynı başlığa sahip tüm kayıtları listede gösterir.")
    self.action_show_all_titles.setCheckable(True)
    self.action_show_all_titles.triggered.connect(self.set_duplicate_mode_off)
    view_menu.addAction(self.action_show_all_titles)

    same_titles_menu = view_menu.addMenu("Aynı Haber Başlıkları")

    self.action_show_all_titles.setText("Tümünü Göster")
    view_menu.removeAction(self.action_show_all_titles)
    same_titles_menu.addAction(self.action_show_all_titles)

    self.action_hide_old = QAction("Eski Tarihli Haberleri Gizle", self)
    _describe(self.action_hide_old, "Aynı başlıkta en güncel kaydı bırakıp eski olanları gizler.")
    self.action_hide_old.setCheckable(True)
    self.action_hide_old.triggered.connect(self.set_duplicate_mode_latest)
    same_titles_menu.addAction(self.action_hide_old)

    self.action_hide_new = QAction("Yeni Tarihli Haberleri Gizle", self)
    _describe(self.action_hide_new, "Aynı başlıkta en eski kaydı bırakıp yeni olanları gizler.")
    self.action_hide_new.setCheckable(True)
    self.action_hide_new.triggered.connect(self.set_duplicate_mode_oldest)
    same_titles_menu.addAction(self.action_hide_new)

    self.action_remember_window = QAction("Pencereyi Mevcut Konuma Sabitle", self)
    _describe(self.action_remember_window, "Pencerenin boyutunu ve konumunu sonraki açılış için kaydeder.")
    self.action_remember_window.setCheckable(True)
    self.action_remember_window.triggered.connect(self.toggle_remember_window_geometry)
    view_menu.addAction(self.action_remember_window)

    self.action_remember_last_date = QAction("Kaldığım Günü Hatırla", self)
    _describe(self.action_remember_last_date, "Açılışta son kullanılan tarihi otomatik geri yükler.")
    self.action_remember_last_date.setCheckable(True)
    self.action_remember_last_date.triggered.connect(self.toggle_remember_last_date)
    view_menu.addAction(self.action_remember_last_date)

    font_menu = view_menu.addMenu("Yazı Boyutu")

    self.action_font_increase = QAction("Büyüt", self)
    _describe(self.action_font_increase, "Uygulamadaki yazı boyutunu bir kademe büyütür.")
    self.action_font_increase.setShortcut("Ctrl++")
    self.action_font_increase.triggered.connect(self.increase_ui_font_size)
    font_menu.addAction(self.action_font_increase)

    self.action_font_decrease = QAction("Küçült", self)
    _describe(self.action_font_decrease, "Uygulamadaki yazı boyutunu bir kademe küçültür.")
    self.action_font_decrease.setShortcut("Ctrl+-")
    self.action_font_decrease.triggered.connect(self.decrease_ui_font_size)
    font_menu.addAction(self.action_font_decrease)

    self.action_font_reset = QAction("Varsayılan Boyut", self)
    _describe(self.action_font_reset, "Yazı boyutunu varsayılan değere döndürür.")
    self.action_font_reset.setShortcut("Ctrl+0")
    self.action_font_reset.triggered.connect(self.reset_ui_font_size)
    font_menu.addAction(self.action_font_reset)

    self.action_title_dictionary = QAction("Başlık Sözlüğü", self)
    _describe(self.action_title_dictionary, "Başlık düzeltmelerinde kullanılan sözlük girişlerini yönetir.")
    self.action_title_dictionary.triggered.connect(self.open_title_dictionary_manager)
    tools_menu.addAction(self.action_title_dictionary)

    self.action_dictionary_bundle = QAction("Sözlük Paketini Yönet...", self)
    _describe(self.action_dictionary_bundle, "Sözlükleri toplu içe/dışa aktarmak için paket ekranını açar.")
    self.action_dictionary_bundle.triggered.connect(self.open_dictionary_bundle_dialog)
    tools_menu.addAction(self.action_dictionary_bundle)

    self.action_rules = QAction("Kanal Kuralları", self)
    _describe(self.action_rules, "Seçili kanalın haber kodu ve parse kurallarını düzenler.")
    self.action_rules.triggered.connect(self.open_rules_manager)
    tools_menu.addAction(self.action_rules)

    spell_menu = tools_menu.addMenu("Haber Başlığı Yazım Denetimi")

    self.action_spellcheck_off = QAction("Kapalı", self)
    _describe(self.action_spellcheck_off, "Başlık yazım denetimini tamamen kapatır.")
    self.action_spellcheck_off.setCheckable(True)
    self.action_spellcheck_off.triggered.connect(lambda: self.set_title_spellcheck_mode("off"))
    spell_menu.addAction(self.action_spellcheck_off)

    self.action_spellcheck_manual = QAction("Elle", self)
    _describe(self.action_spellcheck_manual, "Başlık yazım denetimini yalnızca sağ tık bağlam menüsünden çalıştırır.")
    self.action_spellcheck_manual.setCheckable(True)
    self.action_spellcheck_manual.triggered.connect(lambda: self.set_title_spellcheck_mode("manual"))
    spell_menu.addAction(self.action_spellcheck_manual)

    self.action_spellcheck_auto = QAction("Otomatik", self)
    _describe(self.action_spellcheck_auto, "Yeni okunan başlıklarda yazım denetimini otomatik uygular.")
    self.action_spellcheck_auto.setCheckable(True)
    self.action_spellcheck_auto.triggered.connect(lambda: self.set_title_spellcheck_mode("auto"))
    spell_menu.addAction(self.action_spellcheck_auto)

    self.action_reload_spell = QAction("Yazım Altyapısını Yeniden Algıla", self)
    _describe(self.action_reload_spell, "Yazım denetimi altyapısını yeniden kontrol eder ve durumu günceller.")
    self.action_reload_spell.triggered.connect(self.reload_spell_backend)
    self.action_reload_spell.setText("Yazım Altyapısını Denetle")
    self.action_reload_spell.setToolTip("Türkçe başlık düzeltmesinin hazır olup olmadığını denetler. Yazım düzeltmesi beklenenden zayıfsa bunu kullan.")
    self.action_reload_spell.setStatusTip(self.action_reload_spell.toolTip())

    tools_menu.addSeparator()

    self.action_code_filter = QAction("Kodları Filtreleme", self)
    _describe(self.action_code_filter, "Belirli haber kodlarını gösterir veya listeden gizler.")
    self.action_code_filter.triggered.connect(self.open_code_filter)
    tools_menu.addAction(self.action_code_filter)

    tools_menu.addSeparator()

    self.action_history_scan = QAction("Geçmişi Tara", self)
    _describe(self.action_history_scan, "Seçilen tarih aralığındaki klasörleri tarayıp arşiv veritabanını doldurur.")
    self.action_history_scan.triggered.connect(self.run_history_scan)
    tools_menu.addAction(self.action_history_scan)

    self.action_statistics = QAction("İstatistikler", self)
    _describe(self.action_statistics, "Tarih aralığı ve kanal seçerek haber sayılarını ve editör dağılımını gösterir.")
    self.action_statistics.triggered.connect(self.open_statistics_dialog)
    tools_menu.addAction(self.action_statistics)

    self.action_help = QAction("Yardım", self)
    _describe(self.action_help, "Programın kullanım rehberini açar.")
    self.action_help.triggered.connect(self.open_help_dialog)
    help_menu.addAction(self.action_help)

    self.action_info = QAction("Sürüm Notları", self)
    _describe(self.action_info, "Bu sürümde yapılan değişiklikleri gösterir.")
    self.action_info.triggered.connect(self.show_info_dialog)
    help_menu.addAction(self.action_info)

    self.action_logs = QAction("Günlük Görüntüleyici", self)
    _describe(self.action_logs, "Uygulamanın günlük kayıtlarını görüntüler.")
    self.action_logs.triggered.connect(self.open_log_viewer)
    help_menu.addAction(self.action_logs)

    help_menu.addSeparator()

    help_regex_menu = help_menu.addMenu("Düzenli İfadeler")
    for pattern, description in regex_examples:
        action = QAction(pattern, self)
        _describe(action, description)
        action.triggered.connect(lambda _=False, pattern=pattern: self.insert_search_pattern(pattern))
        help_regex_menu.addAction(action)
