from __future__ import annotations

import json
import os
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
INDEX_JSON = OUT / "assets-index.json"
INDEX_HTML = OUT / "index.html"
COLL_DIR = OUT / "collections"
THUMB_DIR = OUT / "_thumbs"

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


def slugify(path_str: str) -> str:
    return path_str.replace('/', '__').replace('\\', '__').replace(' ', '_')


def build_dirs(root: Path):
    dirs: dict[str, list[dict[str, str]]] = {}
    thumbs: dict[str, str] = {}
    for path in iter_asset_files(root):
        rel = path.relative_to(root).as_posix()
        d = path.relative_to(root).parent.as_posix()
        stem = path.stem
        ext = path.suffix.lower().lstrip('.')
        dirs.setdefault(d, []).append({"stem": stem, "ext": ext, "rel": rel})
        thumbs.setdefault(d, rel)
    for k in list(dirs.keys()):
        dirs[k] = sorted(dirs[k], key=lambda x: (x["stem"].lower(), x["ext"].lower()))
    return dict(sorted(dirs.items())), thumbs


def write_index_json(dirs: dict[str, list[dict[str, str]]]):
    compact_dirs = {k: [x["stem"] for x in vals] for k, vals in dirs.items()}
    data = {"v": 1, "base": BASE_URL, "dirs": compact_dirs}
    OUT.mkdir(parents=True, exist_ok=True)
    INDEX_JSON.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def reset_output_dirs():
    for p in (COLL_DIR, THUMB_DIR):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)


def copy_thumb(rel_path: str, key: str) -> str:
    src = ROOT / rel_path
    ext = src.suffix.lower()
    dst = THUMB_DIR / f"{slugify(key)}{ext}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst.relative_to(OUT).as_posix()


def page_shell(title: str, body: str, back_href: str = "../index.html") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ --bg:#f4efe4; --ink:#1f2a2a; --muted:#5f6b6b; --card:#fffaf0; --line:#d8cfbd; --accent:#305c53; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Georgia, "Times New Roman", serif; color:var(--ink); background:linear-gradient(180deg,#f8f3e9 0%,#efe6d3 100%); }}
    a {{ color:inherit; text-decoration:none; }}
    header {{ padding:40px 24px 20px; max-width:1180px; margin:0 auto; }}
    .back {{ color:var(--accent); font-size:14px; }}
    h1 {{ margin:8px 0 10px; font-size:clamp(28px,4.6vw,52px); line-height:1; }}
    .lead {{ color:var(--muted); max-width:760px; font-size:18px; }}
    main {{ max-width:1180px; margin:0 auto; padding:8px 24px 64px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:18px; }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:20px; overflow:hidden; box-shadow:0 10px 30px rgba(63,44,14,.08); display:block; }}
    .thumb-wrap {{ height:220px; background:#e8decb; display:flex; align-items:center; justify-content:center; }}
    .thumb-wrap img {{ width:100%; height:100%; object-fit:contain; display:block; }}
    .thumb.empty {{ color:var(--muted); font-style:italic; }}
    .body {{ padding:16px 18px 18px; }}
    h2 {{ margin:0 0 8px; font-size:22px; }}
    p {{ margin:0; color:var(--muted); }}
    .chips {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:12px; }}
    code {{ background:#efe5d1; border:1px solid #dfd1b6; border-radius:999px; padding:4px 9px; font-size:12px; }}
  </style>
</head>
<body>
  <header>
    <div class="back"><a href="{escape(back_href)}">&larr; Back</a></div>
    {body}
  </header>
</body>
</html>
'''


def render_collection_pages(dirs: dict[str, list[dict[str, str]]]):
    cards = []
    for directory, items in dirs.items():
        slug = slugify(directory)
        coll_subdir = COLL_DIR / slug
        coll_subdir.mkdir(parents=True, exist_ok=True)
        preview_rel = copy_thumb(items[0]["rel"], directory) if items else ""
        preview_html = f'<img src="{escape(preview_rel)}" alt="{escape(directory)}" loading="lazy">' if preview_rel else '<div class="thumb empty">No preview</div>'
        item_cards = []
        for item in items:
            raw_url = f"{BASE_URL}/{item['rel']}"
            item_cards.append(
                f'<a class="card" href="{escape(raw_url)}" target="_blank" rel="noopener"><div class="thumb-wrap"><img src="{escape(raw_url)}" alt="{escape(item["stem"])}" loading="lazy"></div><div class="body"><h2>{escape(item["stem"])}</h2><p>{escape(item["rel"])}</p></div></a>'
            )
        coll_html = page_shell(
            f"PnPInk Assets - {directory}",
            f'<h1>{escape(directory)}</h1><div class="lead">{len(items)} assets in this folder. Click any item to open the raw file.</div><main><div class="grid">{"".join(item_cards)}</div></main>',
            back_href='../../index.html',
        )
        (coll_subdir / 'index.html').write_text(coll_html, encoding='utf-8')
        names = " ".join(f"<code>{escape(x['stem'])}</code>" for x in items[:24])
        more = f' <span class="more">+{len(items)-24} more</span>' if len(items) > 24 else ''
        cards.append(
            f'<a class="card" href="collections/{escape(slug)}/index.html"><div class="thumb-wrap">{preview_html}</div><div class="body"><h2>{escape(directory)}</h2><p>{len(items)} assets</p><div class="chips">{names}{more}</div></div></a>'
        )
    index_html = page_shell(
        'PnPInk Assets',
        '<h1>PnPInk Assets</h1><div class="lead">Static gallery and compact index for the public asset repository used by <code>pnp://</code>.</div><div class="meta"><a href="assets-index.json">assets-index.json</a></div><main><div class="grid">' + ''.join(cards) + '</div></main>',
        back_href='#',
    ).replace('<div class="back"><a href="#">&larr; Back</a></div>', '')
    INDEX_HTML.write_text(index_html, encoding='utf-8')


def main():
    reset_output_dirs()
    dirs, thumbs = build_dirs(ROOT)
    write_index_json(dirs)
    render_collection_pages(dirs)


if __name__ == "__main__":
    main()

