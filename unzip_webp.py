#!/usr/bin/env python3
"""
Windows / Python 3.12
自动提取同一目录下的 book.size + book.copy

目录结构：
    本脚本.py
    book.size
    book.copy

直接双击运行，或：
    python extract_copy.py

输出：
    extracted/
        0001.webp
        0002.webp
        ...

要求：
    .size 内容形如：
    856070#copy#102670#copy#120582#copy#...

    .copy 是多个 RIFF/WEBP 文件首尾拼接而成。
"""

from __future__ import annotations

import re
import struct
import sys
from pathlib import Path


# ------------------------------------------------------------
# 配置
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
SIZE_FILE = BASE_DIR / "book.size"
COPY_FILE = BASE_DIR / "book.copy"
OUTPUT_DIR = BASE_DIR / "extracted"


# ------------------------------------------------------------
# 读取 size 文件
# ------------------------------------------------------------

def parse_sizes(path: Path) -> list[int]:
    # 先尝试 UTF-8，失败后使用常见 Windows 编码
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raw = path.read_text(encoding="gb18030", errors="replace")

    raw = raw.strip()

    if not raw:
        raise ValueError("book.size 是空文件")

    parts = re.split(r"#copy#", raw, flags=re.IGNORECASE)

    sizes: list[int] = []

    for index, part in enumerate(parts, 1):
        part = part.strip()

        if not part:
            continue

        if not part.isdigit():
            raise ValueError(
                f"book.size 第 {index} 项不是有效数字：{part!r}"
            )

        size = int(part)

        if size <= 0:
            raise ValueError(
                f"book.size 第 {index} 项大小无效：{size}"
            )

        sizes.append(size)

    if not sizes:
        raise ValueError("book.size 中没有找到有效的图片大小")

    return sizes


# ------------------------------------------------------------
# 提取
# ------------------------------------------------------------

def extract() -> None:
    print("=" * 60)
    print("       .size + .copy WebP 图片提取器")
    print("=" * 60)
    print()

    # 检查文件
    if not SIZE_FILE.exists():
        raise FileNotFoundError(
            f"找不到：{SIZE_FILE.name}\n"
            f"请确认 book.size 与本脚本位于同一目录。"
        )

    if not COPY_FILE.exists():
        raise FileNotFoundError(
            f"找不到：{COPY_FILE.name}\n"
            f"请确认 book.copy 与本脚本位于同一目录。"
        )

    print(f"[+] 目录：{BASE_DIR}")
    print(f"[+] size：{SIZE_FILE.name}")
    print(f"[+] copy：{COPY_FILE.name}")
    print()

    # 解析 size
    sizes = parse_sizes(SIZE_FILE)

    copy_size = COPY_FILE.stat().st_size
    expected_size = sum(sizes)

    print(f"[+] 图片数量：{len(sizes)}")
    print(f"[+] size 总和：{expected_size:,} bytes")
    print(f"[+] copy 大小：{copy_size:,} bytes")
    print()

    # 最重要的完整性检查
    if expected_size != copy_size:
        raise ValueError(
            "size 总和 != book.copy 文件大小\n\n"
            f"size 总和：{expected_size:,}\n"
            f"copy 大小：{copy_size:,}\n\n"
            "请确认 book.size 和 book.copy 属于同一本书。"
        )

    print("[OK] 文件大小校验通过")
    print()

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 提取
    offset = 0

    with COPY_FILE.open("rb") as src:

        for page, size in enumerate(sizes, 1):

            data = src.read(size)

            if len(data) != size:
                raise IOError(
                    f"第 {page} 页读取失败：\n"
                    f"期望：{size:,} bytes\n"
                    f"实际：{len(data):,} bytes"
                )

            # RIFF
            if data[:4] != b"RIFF":
                raise ValueError(
                    f"第 {page} 页不是 RIFF 文件。\n"
                    f"文件偏移：{offset:,}"
                )

            # WEBP
            if data[8:12] != b"WEBP":
                raise ValueError(
                    f"第 {page} 页 RIFF 容器不是 WEBP。\n"
                    f"文件偏移：{offset:,}"
                )

            if len(data) < 12:
                raise ValueError(
                    f"第 {page} 页数据长度异常：{len(data)}"
                )

            # RIFF header 中的长度字段
            # RIFF length = 整个文件长度 - 8
            riff_length = struct.unpack_from("<I", data, 4)[0]
            expected_riff_length = size - 8

            if riff_length != expected_riff_length:
                raise ValueError(
                    f"第 {page} 页 RIFF 长度校验失败。\n"
                    f"Header：{riff_length:,}\n"
                    f"实际：{expected_riff_length:,}\n"
                    f"文件偏移：{offset:,}"
                )

            # 输出
            output_file = OUTPUT_DIR / f"{page:04d}.webp"
            output_file.write_bytes(data)

            print(
                f"[OK] {page:04d}/{len(sizes):04d}  "
                f"{size:>10,} bytes  "
                f"offset={offset:>12,}"
            )

            offset += size

    print()
    print("=" * 60)
    print(f"[完成] 成功提取 {len(sizes)} 张 WebP")
    print(f"[输出] {OUTPUT_DIR}")
    print("=" * 60)


# ------------------------------------------------------------
# 主程序
# ------------------------------------------------------------

if __name__ == "__main__":
    try:
        extract()

    except Exception as e:
        print()
        print("=" * 60)
        print("[错误]")
        print(e)
        print("=" * 60)

    finally:
        # Windows 双击运行时不要让窗口立即消失
        print()
        input("按 Enter 键退出...")
