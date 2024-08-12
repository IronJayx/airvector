import hashlib


def hash_file(file_path: str) -> bytes:
    """Compute the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.digest()


def hash_text(text: str) -> str:
    """Compute the MD5 hash of a string."""
    hash_md5 = hashlib.md5()
    hash_md5.update(text.encode("utf-8"))
    return hash_md5.hexdigest()
