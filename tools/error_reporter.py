from datetime import datetime
from pathlib import Path

from core.atomic_io import atomic_write_text
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

    atomic_write_text(report_path, "\n".join(lines), encoding="utf-8")
    return str(report_path)


def record_parse_error(channel_name: str, file_path: str, error: Exception, phase: str = "parse") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = ERROR_REPORTS_DIR / f"parse_errors_{datetime.now().strftime('%Y%m%d')}.log"
    source_name = Path(str(file_path or "")).name or str(file_path or "")
    line = (
        f"[{timestamp}] kanal={channel_name} faz={phase} dosya={source_name} "
        f"yol={file_path} hata={type(error).__name__}: {error}"
    )

    with report_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")

    return str(report_path)
