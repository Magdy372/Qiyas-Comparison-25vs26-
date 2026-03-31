from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def fix_mojibake(text: str) -> str:
    # Some decks are extracted with mojibake by shell tooling, but the PPT XML
    # in this project already contains correct Arabic. Keep the original text
    # unless it clearly looks like mojibake.
    if any(token in text for token in ("Ø", "Ù", "ط", "ظ")):
        try:
            repaired = text.encode("cp1252", "ignore").decode("utf-8", "ignore")
            return repaired or text
        except Exception:
            return text
    return text


def slide_key(name: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: extract_ppt_text.py <pptx> <output_json>")
        return 1

    pptx_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    slides = []
    with zipfile.ZipFile(pptx_path) as zf:
        slide_names = sorted(
            [
                name
                for name in zf.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ],
            key=slide_key,
        )
        for slide_name in slide_names:
            xml_bytes = zf.read(slide_name)
            root = ET.fromstring(xml_bytes)
            texts = []
            for node in root.findall(".//a:t", NS):
                raw = node.text or ""
                cleaned = fix_mojibake(raw).strip()
                if cleaned:
                    texts.append(cleaned)
            slides.append(
                {
                    "slide": slide_key(slide_name),
                    "texts": texts,
                }
            )

    output_path.write_text(json.dumps(slides, ensure_ascii=True, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
