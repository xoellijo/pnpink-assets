from __future__ import annotations

import json
import os
import re
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
PNPINK_REPO = "https://github.com/xoellijo/pnpink"
PNPINK_GUIDE = "https://xoellijo.github.io/pnpink/"
PNPINK_FORUM = "https://boardgamegeek.com/guild/4569"
SERIES_RE = re.compile(r"^(.*?)(\d+)$")


def iter_asset_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        cur = Path(dirpath)
        for name in sorted(filenames):
            p = cur / name
            if p.suffix.lower() in IMAGE_EXTS:
                yield p


def slugify(path_str: str) -> str:
    return path_str.replace('/', '__').replace('\\', '__').replace(' ', '_')


def dir_sort_key(path_str: str):
    parts = path_str.split('/') if path_str else []
    is_ia = 1 if parts and parts[0].upper() == 'IA' else 0
    return (is_ia, path_str.lower())


def build_dirs(root: Path):
    dirs: dict[str, list[dict[str, str]]] = {}
    for path in iter_asset_files(root):
        rel = path.relative_to(root).as_posix()
        d = path.relative_to(root).parent.as_posix()
        stem = path.stem
        ext = path.suffix.lower().lstrip('.')
        dirs.setdefault(d, []).append({"stem": stem, "ext": ext, "rel": rel})
    for k in list(dirs.keys()):
        dirs[k] = sorted(dirs[k], key=lambda x: (x["stem"].lower(), x["ext"].lower()))
    return {k: dirs[k] for k in sorted(dirs.keys(), key=dir_sort_key)}


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


def _ranges(nums: list[int]) -> str:
    nums = sorted(set(nums))
    if not nums:
        return ""
    chunks = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        chunks.append(f"{start}..{prev}" if start != prev else str(start))
        start = prev = n
    chunks.append(f"{start}..{prev}" if start != prev else str(start))
    return ",".join(chunks)


def compact_name_labels(stems: list[str], *, limit: int = 12) -> list[str]:
    singles: list[str] = []
    grouped: dict[str, list[int]] = {}
    for stem in sorted(set(stems), key=str.lower):
        m = SERIES_RE.match(stem)
        if not m:
            singles.append(stem)
            continue
        prefix, num = m.group(1), int(m.group(2))
        grouped.setdefault(prefix, []).append(num)
    labels: list[str] = []
    for prefix in sorted(grouped.keys(), key=str.lower):
        nums = grouped[prefix]
        if len(nums) == 1:
            labels.append(f"{prefix}{nums[0]}")
        else:
            labels.append(f"{prefix}[{_ranges(nums)}]")
    labels.extend(sorted(singles, key=str.lower))
    return labels[:limit]


def page_shell(title: str, body: str, back_href: str = "../index.html") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{ --bg:#f4efe4; --ink:#1f2a2a; --muted:#5f6b6b; --card:#fffaf0; --line:#d8cfbd; --accent:#305c53; --accent2:#7a4f2f; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Georgia, "Times New Roman", serif; color:var(--ink); background:linear-gradient(180deg,#f8f3e9 0%,#efe6d3 100%); }}
    a {{ color:inherit; text-decoration:none; }}
    header {{ padding:28px 22px 12px; max-width:1220px; margin:0 auto; }}
    .back {{ color:var(--accent); font-size:13px; margin-bottom:6px; }}
    h1 {{ margin:6px 0 10px; font-size:clamp(20px,2.4vw,30px); line-height:1.05; letter-spacing:.02em; }}
    .lead {{ color:var(--muted); max-width:960px; font-size:15px; line-height:1.45; }}
    .meta {{ margin-top:10px; color:var(--accent); font-size:13px; display:flex; flex-wrap:wrap; gap:14px; }}
    .meta a {{ color:var(--accent2); text-decoration:underline; text-underline-offset:2px; }}
    .example {{ margin-top:12px; background:#f3ead7; border:1px solid #decfb1; border-radius:14px; padding:10px 12px; font-size:13px; line-height:1.45; }}
    .example code {{ font-size:12px; }}
    main {{ max-width:1220px; margin:0 auto; padding:8px 22px 56px; }}
    .grid {{ display:grid; gap:14px; }}
    .grid.collections {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .grid.assets {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
    .card {{ background:var(--card); border:1px solid var(--line); border-radius:16px; overflow:hidden; box-shadow:0 8px 22px rgba(63,44,14,.07); display:block; }}
    .card.collection .thumb-wrap {{ height:118px; }}
    .card.asset .thumb-wrap {{ height:138px; }}
    .thumb-wrap {{ background:#e8decb; display:flex; align-items:center; justify-content:center; }}
    .thumb-wrap img {{ width:100%; height:100%; object-fit:contain; display:block; }}
    .thumb.empty {{ color:var(--muted); font-style:italic; font-size:13px; }}
    .body {{ padding:10px 12px 12px; }}
    .titleline {{ display:flex; align-items:baseline; justify-content:space-between; gap:8px; margin-bottom:6px; }}
    h2 {{ margin:0; font-size:16px; line-height:1.15; }}
    .card.asset h2 {{ font-size:14px; }}
    p {{ margin:0; color:var(--muted); font-size:12px; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:5px; align-items:center; margin-top:8px; }}
    code {{ background:#efe5d1; border:1px solid #dfd1b6; border-radius:999px; padding:2px 7px; font-size:10px; }}
    .more {{ color:var(--accent); font-size:11px; }}
    @media (min-width: 860px) {{ .grid.collections {{ grid-template-columns:repeat(5,minmax(0,1fr)); }} }}
    @media (max-width: 980px) {{ .grid.assets {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} }}
    @media (max-width: 780px) {{ .grid.collections {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .grid.assets {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
    @media (max-width: 520px) {{ .grid.collections, .grid.assets {{ grid-template-columns:1fr; }} .titleline {{ display:block; }} }}
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
                f'<a class="card asset" href="{escape(raw_url)}" target="_blank" rel="noopener"><div class="thumb-wrap"><img src="{escape(raw_url)}" alt="{escape(item["stem"])}" loading="lazy"></div><div class="body"><div class="titleline"><h2>{escape(item["stem"])}</h2><p>{escape(item["ext"])} file</p></div></div></a>'
            )
        coll_html = page_shell(
            f"PnPInk Assets - {directory}",
            f'<h1>{escape(directory)}</h1><div class="lead">Assets for direct use from <a href="{escape(PNPINK_REPO)}"><code>PnPInk</code></a>. Click any item to open the raw file.</div><div class="meta"><a href="{escape(PNPINK_REPO)}">PnPInk</a><a href="{escape(PNPINK_GUIDE)}">Guide</a><a href="{escape(PNPINK_FORUM)}">Forum</a><a href="https://github.com/xoellijo/pnpink-assets">Assets</a></div><main><div class="grid assets">{"".join(item_cards)}</div></main>',
            back_href='../../index.html',
        )
        (coll_subdir / 'index.html').write_text(coll_html, encoding='utf-8')
        labels = compact_name_labels([x['stem'] for x in items], limit=10)
        names = " ".join(f"<code>{escape(label)}</code>" for label in labels)
        more = f' <span class="more">+{len(items)-len(labels)} more</span>' if len(items) > len(labels) else ''
        cards.append(
            f'<a class="card collection" href="collections/{escape(slug)}/index.html"><div class="thumb-wrap">{preview_html}</div><div class="body"><div class="titleline"><h2>{escape(directory)}</h2><p>{len(items)} assets</p></div><div class="chips">{names}{more}</div></div></a>'
        )
    intro = (
        '<h1>PnPInk Assets</h1>'
        '<div class="lead">This repository is made for <a href="' + escape(PNPINK_REPO) + '"><code>PnPInk</code></a>. The idea is to compose cards and other tabletop components from reusable visual pieces that PnPInk can place automatically from datasets such as CSV or Google Sheets.</div>'
        '<div class="meta"><a href="' + escape(PNPINK_REPO) + '">PnPInk</a><a href="' + escape(PNPINK_GUIDE) + '">Guide</a><a href="' + escape(PNPINK_FORUM) + '">Forum</a><a href="https://github.com/xoellijo/pnpink-assets">Assets</a><a href="assets-index.json">assets-index.json</a></div>'
        '<div class="example"><strong>PnPInk usage</strong>: instead of downloading and placing images by hand, you can reference assets directly from a dataset with tokens such as <code>@{pnp://egg}~i7^</code>, and let PnPInk fetch, rotate, scale and place them automatically across one card or a whole deck.</div>'
        '<main><div class="grid collections">' + ''.join(cards) + '</div></main>'
    )
    index_html = page_shell('PnPInk Assets', intro, back_href='#').replace('<div class="back"><a href="#">&larr; Back</a></div>', '')
    INDEX_HTML.write_text(index_html, encoding='utf-8')


def main():
    reset_output_dirs()
    dirs = build_dirs(ROOT)
    write_index_json(dirs)
    render_collection_pages(dirs)


if __name__ == "__main__":
    main()

