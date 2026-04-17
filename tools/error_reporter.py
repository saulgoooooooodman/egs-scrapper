from datetime import datetime

from core.app_paths import ERROR_REPORTS_DIR
from core.logger_setup import LOG_FILE


ERROR_REPORTS_DIR.mkdir(exist_ok=True)


def generate_error_report() -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = ERROR_REPORTS_DIR / f"error_report_{timestamp}.txt"

    lines = [
        "EGS SCRAPPER HATA RAPORU",
        "=" * 40,
        f"Oluşturulma Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Kaynak Log Dosyası: {LOG_FILE}",
        "",
        "SON LOG İÇERİĞİ",
        "-" * 40,
    ]

    try:
        if LOG_FILE.exists():
            content = LOG_FILE.read_text(encoding="utf-8")
            lines.append(content)
        else:
            lines.append("Log dosyası bulunamadı.")
    except Exception as e:
        lines.append(f"Log dosyası okunamadı: {e}")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return str(report_path)