from __future__ import annotations

import os
import shutil
import sys
import tempfile
import traceback
from datetime import date
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

BASE_DIR = Path(__file__).resolve().parent
REPORT_FILE = BASE_DIR / "smoke_test_report.txt"


def _write_report(lines: list[str]) -> None:
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def _restore_settings(settings_file: Path | None, original_text: str | None) -> None:
    if settings_file is None:
        return

    if original_text is None:
        if settings_file.exists():
            settings_file.unlink()
        return
    settings_file.write_text(original_text, encoding="utf-8")


def run_smoke_test() -> int:
    report: list[str] = ["EGS Scrapper Smoke Test", ""]
    temp_root = Path(tempfile.mkdtemp(prefix="egs_smoke_"))
    temp_app_data = temp_root / "app_data"
    smoke_channel = "A NEWS"
    smoke_date = "2026-04-17"
    original_settings = None
    original_app_data = os.environ.get("EGS_SCRAPPER_APP_DATA_DIR")
    original_disable_migration = os.environ.get("EGS_SCRAPPER_DISABLE_MIGRATION")
    app = None
    help_dialog = None
    archive_dialog = None
    dictionary_bundle_dialog = None
    title_dictionary_dialog = None
    rules_dialog = None
    settings_dialog = None
    statistics_dialog = None
    main_window = None
    settings_file = None
    created_db_paths: set[Path] = set()

    try:
        os.environ["EGS_SCRAPPER_APP_DATA_DIR"] = str(temp_app_data)
        os.environ["EGS_SCRAPPER_DISABLE_MIGRATION"] = "1"

        for module_name in [
            "core.app_paths",
            "core.settings_manager",
            "data.database",
            "data.database_core",
            "data.database_merge",
            "dictionaries.dictionary_store",
            "dictionaries.title_spellcheck",
            "dialogs.archive_search_dialog",
            "dialogs.dictionary_bundle_dialog",
            "dialogs.help_dialog",
            "dialogs.rules_manager_dialog",
            "dialogs.title_dictionary_manager",
            "main_window",
            "parsing.parser",
        ]:
            sys.modules.pop(module_name, None)

        from PySide6.QtWidgets import QApplication

        from core.app_paths import SETTINGS_FILE
        from core.settings_manager import save_settings
        from data.database import get_db_path, get_legacy_db_path
        from data.database_core import db_path as compatibility_db_path
        from data.database_merge import merge_external_database_into_channel
        from data.news_repository import NewsRepository
        from dialogs.archive_search_dialog import ArchiveSearchDialog
        from dialogs.dictionary_bundle_dialog import DictionaryBundleDialog
        from dialogs.help_dialog import HelpDialog
        from dialogs.settings_dialog import SettingsDialog
        from dialogs.rules_manager_dialog import RulesManagerDialog
        from dialogs.statistics_dialog import StatisticsDialog
        from dialogs.title_dictionary_manager import TitleDictionaryManagerDialog
        from dictionaries.dictionary_store import load_channel_dictionary
        from dictionaries.spell_backend import apply_spell_suggestions
        from main_window import MainWindow
        from parsing.news_service import NewsIngestService
        from parsing.parser import parse_egs_file

        settings_file = SETTINGS_FILE
        app = QApplication.instance() or QApplication([])

        created_db_paths = {
            get_db_path(smoke_channel, smoke_date),
            get_db_path(smoke_channel, date.today().isoformat()),
            get_legacy_db_path(smoke_channel),
        }

        sample_dir = temp_root / "04172026.egs"
        sample_dir.mkdir(parents=True, exist_ok=True)

        sample_file = sample_dir / "WAM-TRUMP IRAN POPE (SOT) 13_OGLE.txt"
        sample_text = "HEAD¤Smoke özet¥STORY: İran ve Pope içeren smoke gövde metni."
        sample_file.write_bytes(sample_text.encode("cp1254", errors="ignore"))

        vo_sample_file = sample_dir / "VO-AL-AQSA MOSQUE (VO) 10_OGLE.txt"
        vo_sample_file.write_bytes("HEAD¤VO özet¥STORY: VO haber gövdesi.".encode("cp1254", errors="ignore"))

        sp_sample_file = sample_dir / "SP13 DERBI OZET_OGLE.txt"
        sp_sample_file.write_bytes("HEAD¤SP özet¥STORY: Spor bülteni gövdesi.".encode("cp1254", errors="ignore"))

        repository = NewsRepository(smoke_channel)
        ingest_service = NewsIngestService(smoke_channel)

        legacy_common_path = temp_app_data / "common_dictionary.json"
        legacy_common_path.parent.mkdir(parents=True, exist_ok=True)
        legacy_common_path.write_text('{"MECLIS": "MECLİS"}', encoding="utf-8")

        migrated_channel_dictionary = load_channel_dictionary("A HABER")
        if migrated_channel_dictionary.get("MECLIS") != "MECLİS":
            raise AssertionError("Eski ortak sözlük girdisi kanal sözlüğüne taşınmadı.")
        report.append("[OK] Eski ortak sözlük girdileri kanal sözlüklerine taşındı.")

        compatibility_path = compatibility_db_path(smoke_channel, smoke_date)
        if compatibility_path != get_db_path(smoke_channel, smoke_date):
            raise AssertionError("database_core uyumluluk katmanı yeni DB yoluna yönlenmedi.")
        report.append("[OK] database_core uyumluluk katmanı aktif veritabanı yoluna yönleniyor.")

        parsed = parse_egs_file(sample_file, smoke_channel)
        if parsed.news_code != "WAM":
            raise AssertionError(f"Beklenen haber kodu WAM, gelen: {parsed.news_code}")
        if parsed.title != "TRUMP IRAN POPE (SOT)":
            raise AssertionError(f"Beklenen başlık ayrışmadı: {parsed.title}")
        report.append("[OK] Parser örnek dosyada haber kodu ve başlığı doğru ayrıştırdı.")

        vo_parsed = parse_egs_file(vo_sample_file, smoke_channel)
        if vo_parsed.news_code != "VO":
            raise AssertionError(f"Beklenen haber kodu VO, gelen: {vo_parsed.news_code}")
        if vo_parsed.title != "AL-AQSA MOSQUE (VO)":
            raise AssertionError(f"Beklenen VO başlığı ayrışmadı: {vo_parsed.title}")
        report.append("[OK] Parser yalnızca tanımlı haber kodlarını kullanarak VO-AL ayrışmasını doğru yaptı.")

        sp_parsed = parse_egs_file(sp_sample_file, "A SPOR")
        if sp_parsed.news_code != "SP":
            raise AssertionError(f"Beklenen haber kodu SP, gelen: {sp_parsed.news_code}")
        if sp_parsed.title != "DERBI OZET":
            raise AssertionError(f"Beklenen SP başlığı ayrışmadı: {sp_parsed.title}")
        report.append("[OK] Parser SP13 gibi sayısal varyantları taban spor bülteni koduna eşledi.")

        repository.ensure_storage(smoke_date)
        sample_item = ingest_service.build_news_item(
            sample_file,
            iso_date=smoke_date,
            date_str="17.04.2026",
        )
        sample_item.editors = ["JAVED RANA", "MEHMET CELIK"]
        repository.save_item(sample_item)

        stored_items = repository.fetch_by_date(smoke_date)
        if len(stored_items) != 1:
            raise AssertionError(f"Beklenen 1 kayıt, gelen: {len(stored_items)}")
        report.append("[OK] Parse edilen kayıt veritabanına yazıldı ve geri okundu.")

        external_repository = NewsRepository("ATV")
        external_repository.ensure_storage(smoke_date)
        external_item = ingest_service.build_news_item(
            vo_sample_file,
            iso_date=smoke_date,
            date_str="17.04.2026",
        )
        external_item.path = str(sample_dir / "ATV_EXTERNAL_VO.txt")
        external_item.file_name = "ATV_EXTERNAL_VO.txt"
        external_item.title = "ERDOGAN EK TEST"
        external_item.final_text = "ERDOGAN EK TEST\n\nHarici DB satırı."
        external_repository.save_item(external_item)
        external_db_path = get_db_path("ATV", smoke_date)
        created_db_paths.add(external_db_path)

        merge_result = merge_external_database_into_channel(smoke_channel, str(external_db_path))
        if merge_result.get("merged", 0) < 1:
            raise AssertionError(f"Harici DB merge sonucu beklenenden düşük: {merge_result}")
        if len(repository.fetch_by_date(smoke_date)) < 2:
            raise AssertionError("Harici DB birleştirme sonrası hedef kanalda yeni kayıt görünmüyor.")
        report.append("[OK] Harici veritabanı birleştirme akışı kayıtları hedef kanala taşıdı.")

        archive_results = repository.search_archive("iran", smoke_date, smoke_date)
        if not archive_results:
            raise AssertionError("Basit arşiv araması sonuç döndürmedi.")

        clause_results = repository.search_archive(
            "iran",
            smoke_date,
            smoke_date,
            query_clauses=[
                {"mode": "must", "scope": "all", "text": "iran"},
                {"mode": "exclude", "scope": "all", "text": "sports"},
            ],
        )
        if not clause_results:
            raise AssertionError("Çok satırlı arşiv arama koşulları sonuç döndürmedi.")

        editor_results = repository.search_archive(
            "iran",
            smoke_date,
            smoke_date,
            editor_filters=["JAVED RANA"],
        )
        if not editor_results:
            raise AssertionError("Editör filtresi arşiv aramada sonuç döndürmedi.")
        report.append("[OK] Arşiv arama temel ve çok satırlı sorgularda çalıştı.")

        help_dialog = HelpDialog()
        archive_dialog = ArchiveSearchDialog(smoke_channel)
        dictionary_bundle_dialog = DictionaryBundleDialog(smoke_channel)
        title_dictionary_dialog = TitleDictionaryManagerDialog(smoke_channel)
        rules_dialog = RulesManagerDialog("A SPOR")
        settings_dialog = SettingsDialog({"title_spellcheck_mode": "manual", "auto_title_spellcheck": False}, smoke_channel, {"hide_symbol_prefixed_titles": True})
        statistics_dialog = StatisticsDialog(smoke_channel)
        if help_dialog.windowTitle() != "Yardım":
            raise AssertionError("Yardım penceresi başlığı beklenmiyor.")
        if archive_dialog.windowTitle() != "Arşiv Arama":
            raise AssertionError("Arşiv Arama penceresi başlığı beklenmiyor.")
        if archive_dialog.cancel_btn.isEnabled():
            raise AssertionError("Arşiv arama iptal düğmesi başlangıçta pasif olmalı.")
        if archive_dialog.result_info_label.text() != "Hazır":
            raise AssertionError("Arşiv arama durum etiketi beklenen başlangıç değerinde değil.")
        if dictionary_bundle_dialog.channel_name != smoke_channel:
            raise AssertionError("Sözlük paketi penceresi aktif kanal bilgisiyle açılmadı.")
        if settings_dialog.windowTitle() != "Ayarlar":
            raise AssertionError("Ayarlar penceresi başlığı beklenmiyor.")
        if statistics_dialog.windowTitle() != "İstatistikler":
            raise AssertionError("İstatistikler penceresi başlığı beklenmiyor.")
        report.append("[OK] Yardım, Arşiv Arama, Sözlük Paketi ve Kanal Kuralları pencereleri oluşturuldu.")

        initial_rule_rows = rules_dialog.table.rowCount()
        rules_dialog.search_input.setText("zzz")
        rules_dialog.code_input.setText("K STD")
        rules_dialog.desc_input.setText("KONUK STÜDYO TEST")
        rules_dialog.add_entry()
        if rules_dialog.table.currentRow() != rules_dialog.table.rowCount() - 1:
            raise AssertionError("Kanal Kuralları yeni eklenen koda otomatik odaklanmadı.")
        if rules_dialog.table.rowCount() != initial_rule_rows + 1:
            raise AssertionError("Kanal Kuralları yeni kodu tabloya eklemedi.")
        if rules_dialog.table.item(rules_dialog.table.currentRow(), 0).text() != "K-STD":
            raise AssertionError("Kanal kuralları kanal kodunu esnek yazımdan standart biçime çevirmedi.")
        rules_dialog.table.removeRow(rules_dialog.table.rowCount() - 1)
        rules_dialog._set_dirty(False)
        report.append("[OK] Kanal Kuralları yeni eklenen kodu standart biçime çevirip doğrudan o satıra odakladı.")

        title_dictionary_dialog.wrong_input.setText("MECLIS")
        title_dictionary_dialog.correct_input.setText("MECLİS")
        title_dictionary_dialog.add_entry()
        title_dictionary_dialog.accept()
        saved_dictionary = load_channel_dictionary(smoke_channel)
        if saved_dictionary.get("MECLIS") != "MECLİS":
            raise AssertionError("Başlık sözlüğü diyaloğu yeni girdiyi kalıcı kaydetmedi.")
        report.append("[OK] Başlık sözlüğü diyaloğu yeni girdileri kapanışta kaydetti.")

        if apply_spell_suggestions("ERDOGAN TURKIYE MECLIS") != "ERDOĞAN TÜRKİYE MECLİS":
            raise AssertionError("Türkçe yazım denetimi beklenen başlık düzeltmesini yapmadı.")
        report.append("[OK] Türkçe yazım denetimi ASCII başlıkları Türkçe karakterlerle düzeltti.")

        if SETTINGS_FILE.exists():
            original_settings = SETTINGS_FILE.read_text(encoding="utf-8")

        save_settings(
            {
                "user_name": "Smoke Test",
                "channel_name": smoke_channel,
                "root_folder": str(temp_root),
                "remember_me": True,
                "show_startup_wizard": False,
            }
        )

        main_window = MainWindow()
        app.processEvents()

        menu_titles = [action.text() for action in main_window.menuBar().actions()]
        if "Dosya" not in menu_titles or "Yardım" not in menu_titles:
            raise AssertionError("Ana pencere menüleri beklenen şekilde yüklenmedi.")
        if main_window.action_toggle_code.text() != "Haber Kodlarını Gizle":
            raise AssertionError("Kod sütunu menü metni beklenen yeni ifadeye güncellenmedi.")
        if not hasattr(main_window, "action_open_settings"):
            raise AssertionError("Dosya menüsündeki Ayarlar komutu oluşturulmadı.")

        main_window.news_items = [
            {
                "news_code": "A",
                "title": "ANKARA GUNDEM",
                "corrected_title": "",
                "summary": "",
                "body": "",
                "final_text": "ANKARA GUNDEM",
                "file_name": "ankara.txt",
                "editors": [],
                "iso_date": smoke_date,
                "date_str": "17.04.2026",
                "news_category": "ANKARA",
            },
            {
                "news_code": "E",
                "title": "ERDOGAN MECLIS KONUSMA VTR",
                "corrected_title": "",
                "summary": "",
                "body": "",
                "final_text": "ERDOGAN MECLIS KONUSMA VTR",
                "file_name": "erdogan.txt",
                "editors": [],
                "iso_date": smoke_date,
                "date_str": "17.04.2026",
                "news_category": "EKONOMI",
            },
        ]
        main_window.filtered_items = list(main_window.news_items)
        main_window.fill_tree(main_window.news_items)
        main_window.navigate_news_by_prefix("erd")
        current_item = main_window.news_model.item_at(main_window.news_view.currentIndex().row())
        if not current_item or current_item.get("title") != "ERDOGAN MECLIS KONUSMA VTR":
            raise AssertionError("Hızlı klavye seçimi beklenen habere gitmedi.")

        a_para_sample_file = sample_dir / "AP PIYASA 1300_OGLE.txt"
        a_para_sample_file.write_bytes("HEAD¤Özet¥STORY: Metin.".encode("cp1254", errors="ignore"))
        a_para_item = NewsIngestService("A PARA").build_news_item(
            a_para_sample_file,
            iso_date=smoke_date,
            date_str="17.04.2026",
        )
        if not str(a_para_item.corrected_title or "").endswith("-APR"):
            raise AssertionError("A PARA başlık son eki düzeltilmiş başlıkta boşluksuz -APR olarak eklenmedi.")
        if "PİYASA 1300-APR\n\nPIYASA 1300" not in a_para_item.final_text:
            raise AssertionError("Düzeltilmiş ve orijinal başlık Cinegy metninde birlikte yer almadı.")
        report.append("[OK] A PARA başlığı boşluksuz -APR eki aldı ve düzeltilmiş/orijinal başlık metinde birlikte yazıldı.")

        od_sample_file = sample_dir / "A- 45 YILLIK KRIZ COZULECEK MI VTR (OD)_OGLE.txt"
        od_sample_file.write_bytes("HEAD¤Özet¥STORY: Metin.".encode("cp1254", errors="ignore"))
        od_item = NewsIngestService("A HABER").build_news_item(
            od_sample_file,
            iso_date=smoke_date,
            date_str="17.04.2026",
        )
        if od_item.news_code != "A-OD":
            raise AssertionError(f"Özel dosya haber kodu A-OD olmalıydı, gelen: {od_item.news_code}")
        if not od_item.final_text.startswith("ÖZEL DOSYA-"):
            raise AssertionError("Özel dosya haberi metinde başlık üstüne ayrı satır yerine tek satır ön ek almalı.")
        report.append("[OK] Özel dosya haberleri A-OD koduyla işlenip metinde tek satır 'ÖZEL DOSYA-' ön eki aldı.")

        report.append("[OK] Ana pencere offscreen olarak açıldı ve temel menüler yüklendi.")
        report.append("[OK] Haber listesinde klavyeyle artımlı hızlı seçim çalıştı.")

        report.append("")
        report.append("SONUÇ: SMOKE TEST BAŞARILI")
        _write_report(report)
        return 0

    except Exception:
        report.append("[HATA] Smoke test başarısız oldu.")
        report.append(traceback.format_exc().rstrip())
        report.append("")
        report.append("SONUÇ: SMOKE TEST BAŞARISIZ")
        _write_report(report)
        return 1

    finally:
        try:
            if main_window is not None:
                main_window.close()
        except Exception:
            pass

        for dialog in (statistics_dialog, rules_dialog, title_dictionary_dialog, dictionary_bundle_dialog, archive_dialog, help_dialog):
            try:
                if dialog is not None:
                    dialog.close()
            except Exception:
                pass

        try:
            if app is not None:
                app.processEvents()
        except Exception:
            pass

        for path in created_db_paths:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

        try:
            _restore_settings(settings_file, original_settings)
        except Exception:
            pass

        if original_app_data is None:
            os.environ.pop("EGS_SCRAPPER_APP_DATA_DIR", None)
        else:
            os.environ["EGS_SCRAPPER_APP_DATA_DIR"] = original_app_data

        if original_disable_migration is None:
            os.environ.pop("EGS_SCRAPPER_DISABLE_MIGRATION", None)
        else:
            os.environ["EGS_SCRAPPER_DISABLE_MIGRATION"] = original_disable_migration

        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    result = run_smoke_test()
    print(REPORT_FILE.read_text(encoding="utf-8"))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
