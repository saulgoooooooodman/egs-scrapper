from __future__ import annotations

import os
import shutil
import tempfile
import traceback
from dataclasses import asdict
from datetime import date
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from core.app_paths import BASE_DIR, SETTINGS_FILE
from core.settings_manager import save_settings
from data.database import get_db_path, get_legacy_db_path, get_news_for_date, init_db, search_archive, upsert_news
from dialogs.archive_search_dialog import ArchiveSearchDialog
from dialogs.help_dialog import HelpDialog
from main_window import MainWindow
from parsing.parser import parse_egs_file


REPORT_FILE = BASE_DIR / "smoke_test_report.txt"


def _write_report(lines: list[str]) -> None:
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def _restore_settings(original_text: str | None) -> None:
    if original_text is None:
        if SETTINGS_FILE.exists():
            SETTINGS_FILE.unlink()
        return
    SETTINGS_FILE.write_text(original_text, encoding="utf-8")


def run_smoke_test() -> int:
    report: list[str] = ["EGS Scrapper Smoke Test", ""]
    temp_root = Path(tempfile.mkdtemp(prefix="egs_smoke_"))
    smoke_channel = "SMOKE TEST"
    smoke_date = "2026-04-17"
    original_settings = None
    app = QApplication.instance() or QApplication([])
    help_dialog = None
    archive_dialog = None
    main_window = None

    created_db_paths = {
        get_db_path(smoke_channel, smoke_date),
        get_db_path(smoke_channel, date.today().isoformat()),
        get_legacy_db_path(smoke_channel),
    }

    try:
        sample_dir = temp_root / "04172026.egs"
        sample_dir.mkdir(parents=True, exist_ok=True)

        sample_file = sample_dir / "WAM-TRUMP IRAN POPE (SOT) 13_OGLE.txt"
        sample_text = "HEAD¤Smoke özet¥STORY: İran ve Pope içeren smoke gövde metni."
        sample_file.write_bytes(sample_text.encode("cp1254", errors="ignore"))

        parsed = parse_egs_file(sample_file, smoke_channel)
        if parsed.news_code != "WAM":
            raise AssertionError(f"Beklenen haber kodu WAM, gelen: {parsed.news_code}")
        if parsed.title != "TRUMP IRAN POPE (SOT)":
            raise AssertionError(f"Beklenen başlık ayrışmadı: {parsed.title}")
        report.append("[OK] Parser örnek dosyada haber kodu ve başlığı doğru ayrıştırdı.")

        init_db(smoke_channel, smoke_date)
        sample_item = asdict(parsed)
        stat = sample_file.stat()
        sample_item.update(
            {
                "iso_date": smoke_date,
                "date_str": "17.04.2026",
                "mtime": stat.st_mtime,
                "size": stat.st_size,
            }
        )
        upsert_news(smoke_channel, sample_item)

        stored_items = get_news_for_date(smoke_channel, smoke_date)
        if len(stored_items) != 1:
            raise AssertionError(f"Beklenen 1 kayıt, gelen: {len(stored_items)}")
        report.append("[OK] Parse edilen kayıt veritabanına yazıldı ve geri okundu.")

        archive_results = search_archive(smoke_channel, "iran", smoke_date, smoke_date)
        if not archive_results:
            raise AssertionError("Basit arşiv araması sonuç döndürmedi.")

        clause_results = search_archive(
            smoke_channel,
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
        report.append("[OK] Arşiv arama temel ve çok satırlı sorgularda çalıştı.")

        help_dialog = HelpDialog()
        archive_dialog = ArchiveSearchDialog(smoke_channel)
        if help_dialog.windowTitle() != "Yardım":
            raise AssertionError("Yardım penceresi başlığı beklenmiyor.")
        if archive_dialog.windowTitle() != "Arşiv Arama":
            raise AssertionError("Arşiv Arama penceresi başlığı beklenmiyor.")
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

        for path in created_db_paths:
            try:
                if path.exists():
                    path.unlink()
            except Exception:
                pass

        try:
            _restore_settings(original_settings)
        except Exception:
            pass

        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    result = run_smoke_test()
    print(REPORT_FILE.read_text(encoding="utf-8"))
    return result


if __name__ == "__main__":
    raise SystemExit(main())
