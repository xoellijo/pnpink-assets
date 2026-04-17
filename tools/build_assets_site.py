from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
INDEX_JSON = OUT / "assets-index.json"
INDEX_HTML = OUT / "index.html"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}
SKIP_DIRS = {".git", ".github", ".vscode", "docs", "tools", "__pycache__"}
BASE_URL = "https://raw.githubusercontent.com/xoellijo/pnpink-assets/main"


def iter_asset_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        cur = Path(dirpath)
        for name in sorted(filenames):
            p = cur / name
            if p.suffix.lower() in IMAGE_EXTS:
                yield p


def build_dirs(root: Path):
    dirs: dict[str, list[str]] = {}
    thumbs: dict[str, str] = {}
    for path in iter_asset_files(root):
        rel = path.relative_to(root).as_posix()
        d = path.relative_to(root).parent.as_posix()
        stem = path.stem
        dirs.setdefault(d, []).append(stem)
        thumbs.setdefault(d, rel)
    for k in list(dirs.keys()):
        dirs[k] = sorted(set(dirs[k]), key=str.lower)
    return dict(sorted(dirs.items())), thumbs


def write_index_json(dirs: dict[str, list[str]]):
    data = {"v": 1, "base": BASE_URL, "dirs": dirs}
    OUT.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def render_html(dirs: dict[str, list[str]], thumbs: dict[str, str]):
    sections = []
    for directory, names in dirs.items():
        thumb = thumbs.get(directory, "")
        thumb_url = f"{BASE_URL}/{thumb}" if thumb else ""
        items = " ".join(f"<code>{escape(name)}</code>" for name in names[:24])
        more = f" <span class=\"more\">+{len(names)-24} more</span>" if len(names) > 24 else ""
        preview = f'<img src="{escape(thumb_url)}" alt="{escape(directory)}" loading="lazy">' if thumb_url else '<div class="thumb empty">No preview</div>'
        sections.append(
            f'<section class="card"><div class="thumb-wrap">{preview}</div><div class="body"><h2>{escape(directory)}</h2><p>{len(names)} assets</p><div class="chips">{items}{more}</div></div></section>'
        )
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PnPInk Assets</title>
  <style>
    :root {{ --bg:#f4efe4; --ink:#1f2a2a; --muted:#5f6b6b; --card:#fffaf0; --line:#d8cfbd; --accent:#305c53; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Georgia, "Times New Roman", serif; color:var(--ink); background:linear-gradient(180deg,#f8f3e9 0%,#efe6d3 100%); }}
    header {{ padding:48px 24px 24px; max-width:1100px; margin:0 auto; }}
    h1 {{ margin:0 0 10px; font-size:clamp(32px,5vw,58px); line-height:1; }}
    .lead {{ color:var(--muted); max-width:760px; font-size:18px; }}
    .meta {{ margin-top:16px; color:var(--accent); font-size:14px; }}
    main {{ max-width:1100px; margin:0 auto; padding:8px 24px 64px; display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:18px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:20px; overflow:hidden; box-shadow:0 10px 30px rgba(63,44,14,.08); }}
    .thumb-wrap {{ height:220px; background:#e8decb; display:flex; align-items:center; justify-content:center; }}
    .thumb-wrap img {{ width:100%; height:100%; object-fit:contain; display:block; }}
    .thumb.empty {{ color:var(--muted); font-style:italic; }}
    .body {{ padding:18px; }}
    h2 {{ margin:0 0 8px; font-size:22px; }}
    p {{ margin:0 0 12px; color:var(--muted); }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; }}
    code {{ background:#efe5d1; border:1px solid #dfd1b6; border-radius:999px; padding:4px 9px; font-size:12px; }}
    .more {{ color:var(--accent); font-size:12px; }}
  </style>
</head>
<body>
  <header>
    <h1>PnPInk Assets</h1>
    <div class="lead">Static gallery and compact index for the public asset repository used by <code>pnp://</code>.</div>
    <div class="meta">Generated from repository folders. Index file: <a href="assets-index.json">assets-index.json</a></div>
  </header>
  <main>{''.join(sections)}</main>
</body>
</html>
'''
    INDEX_HTML.write_text(html, encoding="utf-8")


def main():
    dirs, thumbs = build_dirs(ROOT)
    write_index_json(dirs)
    render_html(dirs, thumbs)


if __name__ == "__main__":
    main()
