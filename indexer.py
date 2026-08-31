#!/usr/bin/env python3
"""
Novacode Codebase Symbol Graph & AST Indexer
Builds a fast symbol table (.novacode/index.json) mapping classes, functions, and imports.
"""
import os, sys, re, json, time
from pathlib import Path

EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
}

PATTERNS = {
    "python": [
        (re.compile(r"^\s*class\s+([A-Za-z0-9_]+)"), "class"),
        (re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z0-9_]+)"), "function"),
    ],
    "javascript": [
        (re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z0-9_]+)"), "class"),
        (re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)"), "function"),
        (re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\("), "function"),
    ],
    "typescript": [
        (re.compile(r"^\s*(?:export\s+)?(?:interface|type)\s+([A-Za-z0-9_]+)"), "type"),
        (re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z0-9_]+)"), "class"),
        (re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)"), "function"),
        (re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\("), "function"),
    ],
    "rust": [
        (re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+([A-Za-z0-9_]+)"), "type"),
        (re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z0-9_]+)"), "function"),
    ],
    "go": [
        (re.compile(r"^\s*type\s+([A-Za-z0-9_]+)\s+(?:struct|interface)"), "type"),
        (re.compile(r"^\s*func\s+(?:\([^\)]+\)\s+)?([A-Za-z0-9_]+)"), "function"),
    ]
}

def scan_file(filepath: Path):
    ext = filepath.suffix.lower()
    lang = EXTENSIONS.get(ext)
    if not lang:
        return []
    rules = PATTERNS.get(lang, [])
    symbols = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_no, line in enumerate(f, start=1):
                for regex, sym_type in rules:
                    m = regex.search(line)
                    if m:
                        symbols.append({
                            "name": m.group(1),
                            "type": sym_type,
                            "line": line_no,
                            "signature": line.strip()
                        })
    except Exception:
        pass
    return symbols

def build_index(root_dir: Path):
    t0 = time.time()
    symbols_map = {}
    file_count = 0
    ignore_dirs = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__", ".novacode", ".nova", "Library", "Applications", "Downloads", "Music", "Pictures", "Movies", "Desktop"}

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            p = Path(root) / file
            if p.suffix.lower() in EXTENSIONS:
                syms = scan_file(p)
                if syms:
                    rel_path = str(p.relative_to(root_dir))
                    symbols_map[rel_path] = syms
                    file_count += 1

    out_dir = root_dir / ".novacode"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.json"
    
    payload = {
        "version": "1.0.0",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_files": file_count,
        "total_symbols": sum(len(v) for v in symbols_map.values()),
        "symbols": symbols_map
    }
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    dt = round((time.time() - t0) * 1000)
    print(f"✨ Novacode Indexer: {file_count} archivos indexados ({payload['total_symbols']} símbolos) en {dt}ms ➔ .novacode/index.json")

def main():
    target = Path.cwd() if len(sys.argv) < 2 else Path(sys.argv[1]).resolve()
    build_index(target)

if __name__ == "__main__":
    main()
