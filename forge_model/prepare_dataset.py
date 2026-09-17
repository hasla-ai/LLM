import argparse
import json
import re
from pathlib import Path

EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".cs", ".sql"}
EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
SECRET_WORDS = ("api_key", "secret", "password", "token", "private_key")


def is_safe_code(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in relative.parts):
        return False
    if path.name in {".env", ".env.local"} or path.suffix.lower() not in EXTENSIONS:
        return False
    return path.stat().st_size <= 300_000


def scrub(text: str) -> str:
    text = re.sub(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]", r"\1 = '<REDACTED>'", text)
    return text.replace("\x00", "")


def chunks(text: str, size: int = 12000, overlap: int = 500):
    start = 0
    while start < len(text):
        piece = text[start:start + size]
        if len(piece.strip()) >= 80:
            yield piece
        if start + size >= len(text):
            break
        start += size - overlap


def build_dataset(root: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with output.open("w", encoding="utf-8") as target:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or not is_safe_code(path, root):
                continue
            try:
                text = scrub(path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                continue
            for index, piece in enumerate(chunks(text)):
                record = {"id": f"{path.relative_to(root).as_posix()}#{index}", "language": path.suffix[1:], "text": piece}
                target.write(json.dumps(record, ensure_ascii=False) + "\n")
                count += 1
    print(f"wrote {count} examples to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("data/forge_code.jsonl"))
    args = parser.parse_args()
    build_dataset(args.root.resolve(), args.out)
