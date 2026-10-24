#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nebulove & Yomi-UI-Emoji 字体子集化与内嵌脚本

  pip install fonttools brotli

  python3 scripts/subset_font.py             # 自动拉取原字体并就地更新 index.html
  python3 scripts/subset_font.py --check     # 只报告字形与体积，不写入
  python3 scripts/subset_font.py --all-text  # 保守模式：连同注释在内全文字符全收
"""
import argparse
import base64
import hashlib
import io
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from typing import Optional
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.subset import Options, Subsetter

NEBULOVE_URL = "https://raw.githubusercontent.com/lingyicute/Nebulove/main/Nebulove.woff2"
EMOJI_URL = "https://raw.githubusercontent.com/lingyicute/Yomi-Android/main/assets/Yomi-UI-Emoji.ttf"

HERE = Path(__file__).resolve().parent
DEFAULT_HTML = HERE.parent / "index.html"

ASCII = {chr(c) for c in range(32, 127)}
PUNCT = set("：，。！？；“”‘’（）【】—…·《》×＝÷＋－←↑→↓「」")
BLOCK_RE = re.compile(r"<style>\s*(?:/\*\s*INLINE_FONTS\s*\*/\s*)?@font-face.*?</style>", re.S)


def strip_non_render_text(html: str) -> str:
    """剔除不会渲染的文字：HTML 注释、<style>、<script> 中的注释。"""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"<style\b[^>]*>.*?</style>", "", html, flags=re.S | re.I)

    def _js(m: re.Match) -> str:
        s = re.sub(r"/\*.*?\*/", " ", m.group(1), flags=re.S)
        return re.sub(r"(?m)^[ \t]*//.*$", " ", s)

    return re.sub(r"<script\b[^>]*>(.*?)</script>", _js, html, flags=re.S | re.I)


def is_emoji(ch: str) -> bool:
    cp = ord(ch)
    # 覆盖常见 Emoji 区间：杂项符号、表情、补充符号及变体选择符
    return cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or cp in (0xFE0F, 0x200D, 0xFE0E)


def download(url: str, dest: str, retries: int = 3) -> None:
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "YiKlot-subset/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                # 流式写入避免一次性占用过大内存
                while True:
                    chunk = r.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            return
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            last_err = e
            if attempt < retries:
                print(f"下载失败（{attempt}/{retries}）：{e}，重试中…", file=sys.stderr)
            else:
                raise RuntimeError(f"下载失败 {url}: {last_err}") from last_err


def subset_font(src_path: str, chars: set[str]) -> tuple[bytes, set[int], int]:
    # 空字符集同样直接走子集化：fontTools 会输出仅剩骨架表的最小字体，
    # 不能跳过子集化整份回写——否则页面一旦去掉全部 Emoji，
    # 会把上 MB 的原字体原样内嵌进单文件页面
    with TTFont(src_path) as font:
        opts = Options()
        # 保留必要表，剔除无用 DSIG 以减小体积
        opts.desubroutinize = False
        sub = Subsetter(options=opts)
        sub.populate(text="".join(sorted(chars)))
        sub.subset(font)
        # 清理 DSIG 并固定时间戳以保证幂等
        if "DSIG" in font:
            del font["DSIG"]
        font.recalcTimestamp = False
        font.flavor = "woff2"
        buf = io.BytesIO()
        font.save(buf)
        cmap = font.getBestCmap() or {}
        return buf.getvalue(), set(cmap.keys()), font["maxp"].numGlyphs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path, default=DEFAULT_HTML)
    ap.add_argument("--font-url", default=NEBULOVE_URL, help="Nebulove 远程地址")
    ap.add_argument("--emoji-url", default=EMOJI_URL, help="Yomi-UI-Emoji 远程地址")
    ap.add_argument("--ttf", help="本地 Nebulove 字体路径（指定后不下载）")
    ap.add_argument("--emoji-ttf", help="本地 Yomi-UI-Emoji 字体路径（指定后不下载）")
    ap.add_argument("--extra-chars", type=Path, help="追加保留字符的文本文件")
    ap.add_argument("--all-text", action="store_true", help="保守模式：文件里出现的字符全收")
    ap.add_argument("--check", action="store_true", help="只检查并输出报告，不修改文件")
    args = ap.parse_args()

    if not args.html.exists():
        sys.exit(f"找不到页面文件：{args.html}")
    html = args.html.read_text(encoding="utf-8")
    if not BLOCK_RE.search(html):
        sys.exit(f"未在 {args.html} 中找到内联 @font-face 块")

    extra = args.extra_chars.read_text(encoding="utf-8") if args.extra_chars else ""
    source_text = BLOCK_RE.sub("", html) if args.all_text else strip_non_render_text(html)

    chars = (set(source_text) | ASCII | PUNCT | set(extra)) - {"\n", "\r", "\t"}
    emoji_chars = {c for c in chars if is_emoji(c)}
    neb_chars = chars - emoji_chars
    mode = "全文本" if args.all_text else "可渲染文本"
    print(f"需要保留字符：Nebulove {len(neb_chars)} 个，Yomi-UI-Emoji {len(emoji_chars)} 个（{mode}）")

    with tempfile.TemporaryDirectory(prefix="yiklotski-font-") as tmp:
        neb_src = args.ttf or os.path.join(tmp, os.path.basename(args.font_url))
        if not args.ttf:
            print(f"下载 Nebulove：{args.font_url}")
            download(args.font_url, neb_src)

        emo_src = args.emoji_ttf or os.path.join(tmp, os.path.basename(args.emoji_url))
        if not args.emoji_ttf:
            print(f"下载 Yomi-UI-Emoji：{args.emoji_url}")
            download(args.emoji_url, emo_src)

        neb_data, neb_cov, neb_glyphs = subset_font(neb_src, neb_chars)
        emo_data, emo_cov, emo_glyphs = subset_font(emo_src, emoji_chars)

    missing_neb = sorted(c for c in neb_chars if ord(c) not in neb_cov)
    # 变体选择符与 ZWJ 不要求独立 cmap 映射，避免 --check 误报缺字
    emoji_base = {c for c in emoji_chars if ord(c) not in (0xFE0F, 0xFE0E, 0x200D)}
    missing_emo = sorted(c for c in emoji_base if ord(c) not in emo_cov)

    print(f"Nebulove 子集：{len(neb_cov)} 字符 / {neb_glyphs} 字形，{len(neb_data)/1024:.2f} KB woff2")
    print(f"Emoji    子集：{len(emo_cov)} 字符 / {emo_glyphs} 字形，{len(emo_data)/1024:.2f} KB woff2")
    if missing_neb:
        print("⚠️ Nebulove 未收录字符：" + " ".join(f"{c}(U+{ord(c):04X})" for c in missing_neb))
    if missing_emo:
        print("⚠️ Yomi-UI-Emoji 未收录字符：" + " ".join(f"{c}(U+{ord(c):04X})" for c in missing_emo))

    if args.check:
        print("--check：不写入页面。")
        if missing_neb or missing_emo:
            sys.exit(1)
        return

    neb_b64 = base64.b64encode(neb_data).decode("ascii")
    emo_b64 = base64.b64encode(emo_data).decode("ascii")
    # 打印哈希便于 CI 校验是否需更新
    print(f"Nebulove sha256: {hashlib.sha256(neb_data).hexdigest()[:12]}")
    print(f"Emoji sha256:    {hashlib.sha256(emo_data).hexdigest()[:12]}")
    new_block = (
        "<style>\n/* INLINE_FONTS */\n"
        '@font-face{\n  font-family:"Nebulove";\n'
        f'  src:url("data:font/woff2;charset=utf-8;base64,{neb_b64}") format("woff2");\n'
        "  font-weight:normal;\n  font-style:normal;\n  font-display:swap;\n}\n"
        '@font-face{\n  font-family:"Yomi-UI-Emoji";\n'
        f'  src:url("data:font/woff2;charset=utf-8;base64,{emo_b64}") format("woff2");\n'
        "  font-weight:normal;\n  font-style:normal;\n  font-display:swap;\n}\n"
        "</style>"
    )
    new_html, n = BLOCK_RE.subn(lambda _: new_block, html, count=1)
    if new_html == html:
        print("页面已经是目标内容，未改动。")
        return
    # 原子写入：先写临时文件再替换
    tmp_html = args.html.with_suffix(args.html.suffix + ".tmp")
    tmp_html.write_text(new_html, encoding="utf-8")
    tmp_html.replace(args.html)
    print(f"已更新 {args.html}（替换 {n} 处）：{len(html.encode())/1024:.1f} KB → {len(new_html.encode())/1024:.1f} KB")


if __name__ == "__main__":
    main()
