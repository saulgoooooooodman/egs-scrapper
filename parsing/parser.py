from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from core.rules_store import get_channel_rules


FORMAT_NAMES = {
    "PKG": "VTR",
    "SOT": "SES",
    "VTR": "VTR",
    "VO": "SES",
    "LIVE": "CANLI",
}


@dataclass
class ParsedNews:
    path: str
    file_name: str
    title: str
    corrected_title: str = ""
    news_code: str = ""
    news_category: str = ""
    format_code: str = ""
    format_name: str = ""
    summary: str = ""
    body: str = ""
    kj_lines: list[str] = field(default_factory=list)
    final_text: str = ""
    editors: list[str] = field(default_factory=list)


def _read_egs_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("cp1254", "cp1252", "latin-1", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="ignore")


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"[ \xa0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_single_line(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _normalize_egs_markers(text: str) -> str:
    replacements = {
        "\x8c": "Œ",
        "\x9c": "œ",
        "\xad": "­",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _strip_file_suffix(name: str) -> str:
    return re.sub(r"_(?:[A-Z0-9]+)$", "", name, flags=re.IGNORECASE).strip()


def extract_story_day_from_name(name: str) -> int | None:
    base = _strip_file_suffix(Path(str(name or "")).stem if "." in str(name or "") else str(name or ""))
    match = re.search(r"\s(\d{1,2})$", base)
    if not match:
        return None

    try:
        day = int(match.group(1))
    except ValueError:
        return None

    if 1 <= day <= 31:
        return day
    return None


def _extract_editors(raw_text: str) -> list[str]:
    pattern = re.compile(
        r"\b([A-ZÇĞİÖŞÜ]+(?:\.[A-ZÇĞİÖŞÜ]+)+)\s+\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}"
    )
    result = []
    seen = set()

    for item in pattern.findall(raw_text):
        clean = re.sub(r"\s{2,}", " ", item.replace(".", " ")).strip()
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)

    return result


def _clean_display_title(title: str) -> str:
    title = re.sub(
        r"\s*\((PKG|SOT|VTR|VO|LIVE)\)",
        r" (\1)",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"([A-ZÇĞİÖŞÜ0-9])\((PKG|VTR|SOT|VO|LIVE)\)", r"\1 (\2)", title)
    title = re.sub(r"(\((?:PKG|VTR|SOT|VO|LIVE)\))(\d+)", r"\1 \2", title)
    title = re.sub(r"\s{2,}", " ", title).strip()
    return title


def _strip_story_day_suffix(title: str) -> str:
    match = re.search(r"\s(\d{1,2})$", title)
    if not match:
        return title.strip()

    try:
        day = int(match.group(1))
    except ValueError:
        return title.strip()

    if 1 <= day <= 31:
        return title[:match.start()].strip()
    return title.strip()


def _get_valid_news_codes(channel_name: str) -> list[str]:
    rules = get_channel_rules(channel_name)
    codes = rules.get("news_codes", {})
    if not isinstance(codes, dict):
        return []

    valid_codes = [str(code).strip() for code in codes.keys() if str(code).strip()]
    valid_codes.sort(key=len, reverse=True)
    return valid_codes


def _extract_news_code_and_title(name: str, channel_name: str) -> tuple[str, str]:
    base = _strip_file_suffix(name).strip()
    code = ""
    title = base

    for valid_code in _get_valid_news_codes(channel_name):
        pattern = rf"^(?P<code>{re.escape(valid_code)})(?:(?:\s*-\s*|\s+)(?P<title>.+)|$)"
        match = re.match(pattern, base, flags=re.IGNORECASE)
        if not match:
            continue

        code = valid_code
        title = (match.group("title") or "").strip()
        break

    has_od = (
        "(OD)" in title.upper()
        or title.upper().startswith("(OD)")
        or code.upper() == "(OD)"
    )
    title = re.sub(r"\(OD\)", "", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\bAPS\b", "", title, flags=re.IGNORECASE).strip()

    if channel_name == "A HABER" and code.upper() == "AZ":
        title = f"ANALİZ-{title}".replace("ANALİZ- -", "ANALİZ-").replace("ANALİZ--", "ANALİZ-")

    if has_od:
        title = f"ÖZEL DOSYA-{title}".strip("- ").replace("--", "-")
        code = "YY-(OD)"

    title = _clean_display_title(title)
    title = _strip_story_day_suffix(title)

    if channel_name == "A PARA" and title and not title.endswith("-APR"):
        title = f"{title} -APR"

    return code, title


def _detect_format_code(title: str) -> tuple[str, str]:
    upper = title.upper()

    for code in ("LIVE", "PKG", "VTR", "SOT", "VO"):
        if re.search(rf"\b{re.escape(code)}\b", upper):
            return code, FORMAT_NAMES.get(code, code)

    return "", ""


def _resolve_news_category(channel_name: str, news_code: str) -> str:
    rules = get_channel_rules(channel_name)
    codes = rules.get("news_codes", {})
    return codes.get(news_code, codes.get(news_code.upper(), ""))


def _extract_summary_and_body(text: str) -> tuple[str, str]:
    summary = ""
    body = ""

    main_part = text.split("¦", 1)[0]

    if "¤" in main_part:
        after_summary = main_part.split("¤", 1)[1]
    else:
        after_summary = main_part

    if "¥" in after_summary:
        summary, body = after_summary.split("¥", 1)
    else:
        summary = after_summary

    summary = _normalize_text(summary)
    body = _normalize_text(body)
    body = re.sub(r"^\s*STORY:\s*", "", body, flags=re.IGNORECASE)

    return summary, body


def _split_kj_schema_row(row: str) -> tuple[list[str], str]:
    parts = [part.strip() for part in row.split(";;")]
    if not parts:
        return [""], ""

    template = parts[-1].upper()
    columns = parts[:-1] or [""]
    return columns, template


def _extract_kj_block(text: str) -> str:
    if "©ª" not in text:
        return ""

    kj = text.split("©ª", 1)[1]
    end_positions = []

    for marker in ("Œ­", "­", " ®", "®", "¯"):
        pos = kj.find(marker)
        if pos != -1:
            end_positions.append(pos)

    if end_positions:
        kj = kj[:min(end_positions)]

    return kj.strip()


def _split_rows_by_separator(text: str) -> list[str]:
    if "Œ" in text:
        rows = text.split("Œ")
    else:
        rows = text.splitlines()

    return [_normalize_text(row) for row in rows]


def _extract_kj_lines(text: str) -> list[str]:
    kj_block = _extract_kj_block(text)
    if not kj_block:
        return []

    if "«¬" not in kj_block:
        lines = [_normalize_single_line(row) for row in _split_rows_by_separator(kj_block)]
        return [line for line in lines if line]

    schema_part, values_part = kj_block.split("«¬", 1)
    schema_rows = [row for row in _split_rows_by_separator(schema_part) if _normalize_single_line(row)]
    value_rows = [row for row in _split_rows_by_separator(values_part) if _normalize_single_line(row)]

    result = []
    row_count = min(len(schema_rows), len(value_rows))
    editorial_prefixes = (
        "HABER:",
        "GÖRÜNTÜ:",
        "GORUNTU:",
        "KAMERA:",
        "KURGU:",
        "MONTAJ:",
    )

    for index in range(row_count):
        schema_row = _normalize_single_line(schema_rows[index])
        value = _normalize_single_line(value_rows[index])

        columns, template = _split_kj_schema_row(schema_row)
        col1 = _normalize_single_line(columns[0]) if len(columns) > 0 else ""
        col2 = _normalize_single_line(columns[1]) if len(columns) > 1 else ""

        if template == "DOUBLE":
            if value:
                result.append(value)
            if col1:
                result.append(col1)
            if col2:
                result.append(col2)
        elif template == "NAME":
            if col1 and value:
                result.append(f"{col1} {value}".strip())
            elif value:
                result.append(value)
            elif col1:
                result.append(col1)
        elif template == "LOCATION":
            if value:
                result.append(value)
            elif col1:
                result.append(col1)
        elif template in {"1-TEKSATIRKJ", "1-TEKSATIR"}:
            if value:
                result.append(value)
            elif col1:
                result.append(col1)
        elif template in {"4-ISIM-KJ", "4-İSIM-KJ", "4-ISIMKJ"}:
            if col1 and value:
                col1_is_editorial = col1.upper().startswith(editorial_prefixes)
                value_is_editorial = value.upper().startswith(editorial_prefixes)

                if col1_is_editorial or value_is_editorial:
                    if value:
                        result.append(value)
                    if col1:
                        result.append(col1)
                else:
                    result.append(f"{col1} {value}".strip())
            elif value:
                result.append(value)
            elif col1:
                result.append(col1)
        else:
            if value:
                result.append(value)
            if col1:
                result.append(col1)
            if col2:
                result.append(col2)

    unique = []
    seen = set()

    for item in result:
        item = _normalize_single_line(item)
        if not item or item in seen:
            continue
        seen.add(item)
        unique.append(item)

    return unique


def _build_final_text(title: str, summary: str, body: str, kj_lines: list[str]) -> str:
    parts = []

    if title.strip():
        parts.append(title.strip())
    if summary.strip():
        parts.append(summary.strip())
    if body.strip():
        parts.append(body.strip())

    kj_clean = [
        line.strip()
        for line in kj_lines
        if line.strip() and line.strip() != title.strip()
    ]
    if kj_clean:
        parts.append("\n".join(kj_clean))

    return "\n\n".join(parts).strip()


def parse_egs_file(file_path: Path, channel_name: str) -> ParsedNews:
    logger = logging.getLogger("EGS.Parser")
    logger.info("Parse başladı | kanal=%s | dosya=%s", channel_name, file_path.stem)

    raw_text = _normalize_egs_markers(_read_egs_text(file_path))

    news_code, title = _extract_news_code_and_title(file_path.stem, channel_name)
    news_category = _resolve_news_category(channel_name, news_code)
    format_code, format_name = _detect_format_code(title)

    summary, body = _extract_summary_and_body(raw_text)
    kj_lines = _extract_kj_lines(raw_text)
    editors = _extract_editors(raw_text)
    final_text = _build_final_text(title, summary, body, kj_lines)

    parsed = ParsedNews(
        path=str(file_path),
        file_name=file_path.name,
        title=title,
        corrected_title="",
        news_code=news_code,
        news_category=news_category,
        format_code=format_code,
        format_name=format_name,
        summary=summary,
        body=body,
        kj_lines=kj_lines,
        final_text=final_text,
        editors=editors,
    )

    logger.info(
        "Parse tamamlandı | dosya=%s | kod=%s | başlık=%s | kj_sayısı=%s | editör=%s",
        file_path.stem,
        parsed.news_code,
        parsed.title,
        len(parsed.kj_lines),
        len(parsed.editors),
    )

    return parsed
