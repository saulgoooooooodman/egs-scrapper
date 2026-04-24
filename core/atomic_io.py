from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def atomic_write_text(path: str | Path, content: str, encoding: str = "utf-8") -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.stem}_",
        suffix=".tmp",
        dir=str(target.parent),
    )
    temp_path = Path(temp_name)

    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp_path, target)
        return target
    except OSError:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def atomic_write_json(path: str | Path, data, *, ensure_ascii: bool = False, indent: int = 2) -> Path:
    return atomic_write_text(
        path,
        json.dumps(data, ensure_ascii=ensure_ascii, indent=indent),
        encoding="utf-8",
    )
