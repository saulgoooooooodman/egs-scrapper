import os


def normalize_cache_path(path) -> str:
    text = str(path or "").strip()
    if not text:
        return ""
    return os.path.normpath(text)


def ensure_cache_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            path TEXT PRIMARY KEY,
            mtime REAL,
            size INTEGER
        )
    """)
    conn.commit()


def is_cached(conn, path, mtime, size):
    normalized_path = normalize_cache_path(path)
    if not normalized_path:
        return False

    cur = conn.cursor()
    cur.execute(
        "SELECT mtime,size FROM cache WHERE path = ? COLLATE NOCASE",
        (normalized_path,),
    )
    row = cur.fetchone()
    return row and row[0] == mtime and row[1] == size


def update_cache(conn, path, mtime, size):
    normalized_path = normalize_cache_path(path)
    if not normalized_path:
        return

    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO cache (path,mtime,size)
        VALUES (?,?,?)
    """, (normalized_path, mtime, size))


def clear_cache(conn):
    cur = conn.cursor()
    cur.execute("DELETE FROM cache")


def delete_cache_paths(conn, paths) -> int:
    normalized_paths = []
    for raw_path in paths or []:
        normalized = normalize_cache_path(raw_path)
        if normalized:
            normalized_paths.append(normalized)

    if not normalized_paths:
        return 0

    cur = conn.cursor()
    placeholders = ",".join("?" for _ in normalized_paths)
    cur.execute(
        f"DELETE FROM cache WHERE path COLLATE NOCASE IN ({placeholders})",
        normalized_paths,
    )
    return max(cur.rowcount, 0)
