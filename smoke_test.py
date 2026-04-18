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
    main_window = None
    settings_file = None

    try:
        os.environ["EGS_SCRAPPER_APP_DATA_DIR"] = str(temp_app_data)
        os.environ["EGS_SCRAPPER_DISABLE_MIGRATION"] = "1"

        for module_name in [
            "core.app_paths",
            "core.settings_manager",
            "data.database",
            "parsing.parser",
            "dialogs.archive_search_dialog",
            "dialogs.help_dialog",
            "main_window",
        ]:
            sys.modules.pop(module_name, None)

        from PySide6.QtWidgets import QApplication

        from core.app_paths import SETTINGS_FILE
        from core.settings_manager import save_settings
        from data.database import (
            get_db_path,
            get_legacy_db_path,
        )
        from data.news_repository import NewsRepository
        from dialogs.archive_search_dialog import ArchiveSearchDialog
        from dialogs.help_dialog import HelpDialog
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

        repository = NewsRepository(smoke_channel)
        ingest_service = NewsIngestService(smoke_channel)

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
        if help_dialog.windowTitle() != "Yardım":
            raise AssertionError("Yardım penceresi başlığı beklenmiyor.")
        if archive_dialog.windowTitle() != "Arşiv Arama":
            raise AssertionError("Arşiv Arama penceresi başlığı beklenmiyor.")
        if archive_dialog.cancel_btn.isEnabled():
            raise AssertionError("Arşiv arama iptal düğmesi başlangıçta pasif olmalı.")
        if archive_dialog.result_info_label.text() != "Hazır":
            raise AssertionError("Arşiv arama durum etiketi beklenen başlangıç değerinde değil.")
        report.append("[OK] Yardım ve Arşiv Arama pencereleri oluşturuldu.")

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
        report.append("[OK] Ana pencere offscreen olarak açıldı ve temel menüler yüklendi.")

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

        for dialog in (archive_dialog, help_dialog):
            try:
                if dialog is not None:
                    dialog.close()
            except Exception:
                pass

        try:
            app.processEvents()
        except Exception:
            pass

        for path in locals().get("created_db_paths", set()):
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
