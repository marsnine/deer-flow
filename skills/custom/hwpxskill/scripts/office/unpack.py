#!/usr/bin/env python3
"""Unpack an HWPX file into a directory with pretty-printed XML.

Usage:
    python unpack.py input.hwpx output_dir/
"""

import argparse
import os
import sys
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


def unpack(hwpx_path: str, output_dir: str, *, pretty: bool = False) -> None:
    """Extract HWPX archive, preserving original byte content by default.

    Args:
        pretty: If True, pretty-print XML (for human readability).
                If False (default), preserve original bytes exactly.
    """

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    with ZipFile(hwpx_path, "r") as zf:
        for entry in zf.namelist():
            data = zf.read(entry)
            dest = output / entry
            dest.parent.mkdir(parents=True, exist_ok=True)

            if pretty and (entry.endswith(".xml") or entry.endswith(".hpf")):
                try:
                    tree = etree.fromstring(data)
                    etree.indent(tree, space="  ")
                    formatted = etree.tostring(
                        tree,
                        pretty_print=True,
                        xml_declaration=True,
                        encoding="UTF-8",
                    )
                    dest.write_bytes(formatted)
                    continue
                except etree.XMLSyntaxError:
                    pass  # Fall through to raw write

            dest.write_bytes(data)

    print(f"Unpacked: {hwpx_path} -> {output_dir}")
    print(f"  Files: {len(list(output.rglob('*')))} entries")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unpack HWPX file into a directory with pretty-printed XML"
    )
    parser.add_argument("input", help="Path to .hwpx file")
    parser.add_argument("output", help="Output directory path")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print XML files (default: preserve original bytes)")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    unpack(args.input, args.output, pretty=args.pretty)


if __name__ == "__main__":
    main()
