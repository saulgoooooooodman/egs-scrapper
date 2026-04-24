from __future__ import annotations

import subprocess


def show_file_in_explorer(path: str) -> None:
    normalized_path = str(path or "").strip()
    if not normalized_path:
        raise ValueError("Explorer için geçerli bir dosya yolu gerekli.")

    subprocess.run(
        ["explorer.exe", "/select,", normalized_path],
        check=False,
        timeout=10,
    )
