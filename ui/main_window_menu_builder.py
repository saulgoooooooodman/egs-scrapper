from __future__ import annotations

from PySide6.QtGui import QAction


def build_main_window_menu(self):
    menu_bar = self.menuBar()
    menu_bar.clear()

    file_menu = menu_bar.addMenu("Dosya")
    edit_menu = menu_bar.addMenu("Düzen")
    search_menu = menu_bar.addMenu("Ara")
    view_menu = menu_bar.addMenu("Görünüm")
    tools_menu = menu_bar.addMenu("Araçlar")
    help_menu = menu_bar.addMenu("Yardım")

    self.action_change_profile = QAction("Profili Değiştir", self)
    self.action_change_profile.triggered.connect(self.change_profile)
    file_menu.addAction(self.action_change_profile)

    file_menu.addSeparator()

    database_menu = file_menu.addMenu("Veri ve Veritabanı")

    self.action_open_db_dir = QAction("Veritabanı Klasörünü Aç", self)
    self.action_open_db_dir.triggered.connect(self.open_databases_folder)
    database_menu.addAction(self.action_open_db_dir)

    self.action_open_data_dir = QAction("Veri Klasörünü Aç", self)
    self.action_open_data_dir.triggered.connect(self.open_data_folder)
    database_menu.addAction(self.action_open_data_dir)

    self.action_manage_external_dbs = QAction("Dış Veritabanlarını Yönet...", self)
    self.action_manage_external_dbs.triggered.connect(self.open_external_db_manager)
    database_menu.addAction(self.action_manage_external_dbs)

    self.action_merge_external_db = QAction("Veritabanı İçe Aktar / Birleştir...", self)
    self.action_merge_external_db.triggered.connect(self.open_db_merge_dialog)
    database_menu.addAction(self.action_merge_external_db)

    folders_menu = file_menu.addMenu("Günlükler ve Klasörler")

    self.action_open_logs_dir = QAction("Günlük Klasörünü Aç", self)
    self.action_open_logs_dir.triggered.connect(self.open_logs_folder)
    folders_menu.addAction(self.action_open_logs_dir)

    scan_menu = file_menu.addMenu("Tarama ve Yenileme")

    self.action_refresh = QAction("Yenile", self)
    self.action_refresh.setShortcut("F5")
    self.action_refresh.triggered.connect(self.load_news)
    scan_menu.addAction(self.action_refresh)

    self.action_force_refresh = QAction("Zorla Yenile", self)
    self.action_force_refresh.triggered.connect(lambda: self.load_news(force_refresh=True))
    scan_menu.addAction(self.action_force_refresh)

    self.action_clear_cache = QAction("Önbelleği Temizle", self)
    self.action_clear_cache.triggered.connect(self.clear_cache)
    scan_menu.addAction(self.action_clear_cache)

    self.action_history_scan = QAction("Geçmişi Tara", self)
    self.action_history_scan.triggered.connect(self.run_history_scan)
    scan_menu.addAction(self.action_history_scan)

    file_menu.addSeparator()

    self.action_close = QAction("Kapat", self)
    self.action_close.setShortcut("Ctrl+Q")
    self.action_close.triggered.connect(self.close)
    file_menu.addAction(self.action_close)

    self.action_cut = QAction("Kes", self)
    self.action_cut.setShortcut("Ctrl+X")
    self.action_cut.triggered.connect(self.cut_text)
    edit_menu.addAction(self.action_cut)

    self.action_copy = QAction("Kopyala", self)
    self.action_copy.setShortcut("Ctrl+C")
    self.action_copy.triggered.connect(self.copy_active_context)
    edit_menu.addAction(self.action_copy)

    self.action_paste = QAction("Yapıştır", self)
    self.action_paste.setShortcut("Ctrl+V")
    self.action_paste.triggered.connect(self.paste_text)
    edit_menu.addAction(self.action_paste)

    self.action_select = QAction("Seç", self)
    self.action_select.triggered.connect(self.focus_preview_text)
    edit_menu.addAction(self.action_select)

    self.action_select_all = QAction("Tümünü Seç", self)
    self.action_select_all.setShortcut("Ctrl+A")
    self.action_select_all.triggered.connect(self.select_all_text)
    edit_menu.addAction(self.action_select_all)

    self.action_delete = QAction("Sil", self)
    self.action_delete.triggered.connect(self.delete_selected_text)
    edit_menu.addAction(self.action_delete)

    edit_menu.addSeparator()

    self.action_undo = QAction("Geri Al", self)
    self.action_undo.setShortcut("Ctrl+Z")
    self.action_undo.triggered.connect(self.undo_text)
    edit_menu.addAction(self.action_undo)

    self.action_redo = QAction("Yinele", self)
    self.action_redo.setShortcut("Ctrl+Y")
    self.action_redo.triggered.connect(self.redo_text)
    edit_menu.addAction(self.action_redo)

    case_menu = edit_menu.addMenu("Harfleri Çevir")

    self.action_upper = QAction("TÜMÜNÜ BÜYÜK", self)
    self.action_upper.triggered.connect(self.to_upper)
    case_menu.addAction(self.action_upper)

    self.action_lower = QAction("tümünü küçük", self)
    self.action_lower.triggered.connect(self.to_lower)
    case_menu.addAction(self.action_lower)

    self.action_title_case = QAction("İlk Harfler Büyük", self)
    self.action_title_case.triggered.connect(self.to_title_case)
    case_menu.addAction(self.action_title_case)

    multi_select_menu = edit_menu.addMenu("Çoklu Seç")

    self.action_select_same_codes = QAction("Seçili haber kodlarını seç", self)
    self.action_select_same_codes.triggered.connect(self.select_same_codes)
    multi_select_menu.addAction(self.action_select_same_codes)

    self.action_select_other_codes = QAction("Seçili haberlerin dışındakileri seç", self)
    self.action_select_other_codes.triggered.connect(self.select_other_codes)
    multi_select_menu.addAction(self.action_select_other_codes)

    self.action_find = QAction("Bul", self)
    self.action_find.setShortcut("Ctrl+F")
    self.action_find.triggered.connect(self.focus_search)
    search_menu.addAction(self.action_find)

    self.action_find_replace = QAction("Bul / Değiştir", self)
    self.action_find_replace.setShortcut("Ctrl+H")
    self.action_find_replace.triggered.connect(self.open_find_replace_dialog)
    search_menu.addAction(self.action_find_replace)

    self.action_find_next = QAction("Sonrakini Bul", self)
    self.action_find_next.setShortcut("F3")
    self.action_find_next.triggered.connect(self.find_next_in_preview)
    search_menu.addAction(self.action_find_next)

    self.action_find_prev = QAction("Öncekini Bul", self)
    self.action_find_prev.setShortcut("Shift+F3")
    self.action_find_prev.triggered.connect(self.find_prev_in_preview)
    search_menu.addAction(self.action_find_prev)

    self.action_always_on_top = QAction("Her Zaman Üstte Göster", self)
    self.action_always_on_top.setCheckable(True)
    self.action_always_on_top.triggered.connect(self.toggle_always_on_top)
    view_menu.addAction(self.action_always_on_top)

    self.action_live_watch = QAction("Canlı İzleme", self)
    self.action_live_watch.setCheckable(True)
    self.action_live_watch.triggered.connect(self.toggle_live_watch)
    view_menu.addAction(self.action_live_watch)

    self.action_toggle_code = QAction("Haber Kodlarını Göster / Gizle", self)
    self.action_toggle_code.triggered.connect(self.toggle_code_column)
    view_menu.addAction(self.action_toggle_code)

    self.action_show_previous_day_news = QAction("Önceki Günün Haberlerini Göster", self)
    self.action_show_previous_day_news.setCheckable(True)
    self.action_show_previous_day_news.triggered.connect(self.toggle_previous_day_news)
    view_menu.addAction(self.action_show_previous_day_news)

    self.action_show_all_titles = QAction("Tüm Haber Başlıklarını Göster", self)
    self.action_show_all_titles.setCheckable(True)
    self.action_show_all_titles.triggered.connect(self.set_duplicate_mode_off)
    view_menu.addAction(self.action_show_all_titles)

    same_titles_menu = view_menu.addMenu("Aynı Haber Başlıkları")

    self.action_hide_old = QAction("Yalnızca Eski Tarihli Haberleri Gizle", self)
    self.action_hide_old.setCheckable(True)
    self.action_hide_old.triggered.connect(self.set_duplicate_mode_latest)
    same_titles_menu.addAction(self.action_hide_old)

    self.action_hide_new = QAction("Yalnızca Yeni Tarihli Haberleri Gizle", self)
    self.action_hide_new.setCheckable(True)
    self.action_hide_new.triggered.connect(self.set_duplicate_mode_oldest)
    same_titles_menu.addAction(self.action_hide_new)

    self.action_remember_window = QAction("Pencereyi Mevcut Konuma Sabitle", self)
    self.action_remember_window.setCheckable(True)
    self.action_remember_window.triggered.connect(self.toggle_remember_window_geometry)
    view_menu.addAction(self.action_remember_window)

    font_menu = view_menu.addMenu("Yazı Boyutu")

    self.action_font_increase = QAction("Büyüt", self)
    self.action_font_increase.setShortcut("Ctrl++")
    self.action_font_increase.triggered.connect(self.increase_ui_font_size)
    font_menu.addAction(self.action_font_increase)

    self.action_font_decrease = QAction("Küçült", self)
    self.action_font_decrease.setShortcut("Ctrl+-")
    self.action_font_decrease.triggered.connect(self.decrease_ui_font_size)
    font_menu.addAction(self.action_font_decrease)

    self.action_font_reset = QAction("Varsayılan Boyut", self)
    self.action_font_reset.setShortcut("Ctrl+0")
    self.action_font_reset.triggered.connect(self.reset_ui_font_size)
    font_menu.addAction(self.action_font_reset)

    language_tools_menu = tools_menu.addMenu("Dil ve Kurallar")

    self.action_title_dictionary = QAction("Başlık Sözlüğü", self)
    self.action_title_dictionary.triggered.connect(self.open_title_dictionary_manager)
    language_tools_menu.addAction(self.action_title_dictionary)

    self.action_dictionary_bundle = QAction("Sözlük Paketini Yönet...", self)
    self.action_dictionary_bundle.triggered.connect(self.open_dictionary_bundle_dialog)
    language_tools_menu.addAction(self.action_dictionary_bundle)

    self.action_rules = QAction("Kanal Kuralları", self)
    self.action_rules.triggered.connect(self.open_rules_manager)
    language_tools_menu.addAction(self.action_rules)

    archive_tools_menu = tools_menu.addMenu("Arşiv ve Veri")

    self.action_code_filter = QAction("Kodları Filtreleme", self)
    self.action_code_filter.triggered.connect(self.open_code_filter)
    archive_tools_menu.addAction(self.action_code_filter)

    self.action_archive_search = QAction("Arşiv Arama", self)
    self.action_archive_search.setShortcut("F7")
    self.action_archive_search.triggered.connect(self.open_archive_search)
    archive_tools_menu.addAction(self.action_archive_search)

    maintenance_menu = tools_menu.addMenu("Bakım")

    self.action_reload_spell = QAction("Yazım Denetimini Kontrol Et", self)
    self.action_reload_spell.triggered.connect(self.reload_spell_backend)
    maintenance_menu.addAction(self.action_reload_spell)

    self.action_help = QAction("Yardım", self)
    self.action_help.triggered.connect(self.open_help_dialog)
    help_menu.addAction(self.action_help)

    self.action_info = QAction("Sürüm Notları", self)
    self.action_info.triggered.connect(self.show_info_dialog)
    help_menu.addAction(self.action_info)

    diagnostics_menu = help_menu.addMenu("Tanılama")

    self.action_logs = QAction("Günlük Görüntüleyici", self)
    self.action_logs.triggered.connect(self.open_log_viewer)
    diagnostics_menu.addAction(self.action_logs)

    self.action_health_check = QAction("Sağlık Kontrolü Çalıştır", self)
    self.action_health_check.triggered.connect(self.run_health_check_tool)
    diagnostics_menu.addAction(self.action_health_check)

    self.action_smoke_test = QAction("Smoke Test Çalıştır", self)
    self.action_smoke_test.triggered.connect(self.run_smoke_test_tool)
    diagnostics_menu.addAction(self.action_smoke_test)
