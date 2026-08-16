from __future__ import annotations

import io
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import PurePosixPath

from bs4 import BeautifulSoup
from pypdf import PdfReader

from .core import ParsedBook, Segment


def _clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf(data: bytes, filename: str) -> ParsedBook:
    reader = PdfReader(io.BytesIO(data))
    title = None
    author = None
    if reader.metadata:
        title = getattr(reader.metadata, "title", None)
        author = getattr(reader.metadata, "author", None)

    segments: list[Segment] = []
    for i, page in enumerate(reader.pages, start=1):
        text = _clean_text(page.extract_text() or "")
        if text:
            segments.append(Segment(text=text, locator=f"page {i}", order_index=i - 1))

    if not segments:
        raise ValueError(
            "No extractable text was found. This MVP does not OCR image-only/scanned PDFs yet."
        )

    fallback_title = PurePosixPath(filename).stem
    return ParsedBook(
        title=(title or fallback_title).strip(),
        author=(author.strip() if author else None),
        file_type="pdf",
        segments=segments,
    )


def _local_name(tag: str) -> str:
    return tag.split("}")[-1]


def _epub_spine_paths(zf: zipfile.ZipFile) -> tuple[list[str], str | None, str | None]:
    names = set(zf.namelist())
    rootfile = None
    if "META-INF/container.xml" in names:
        container = ET.fromstring(zf.read("META-INF/container.xml"))
        for node in container.iter():
            if _local_name(node.tag) == "rootfile":
                rootfile = node.attrib.get("full-path")
                if rootfile:
                    break

    if not rootfile or rootfile not in names:
        opfs = [n for n in names if n.lower().endswith(".opf")]
        rootfile = opfs[0] if opfs else None

    if not rootfile:
        htmls = sorted(n for n in names if n.lower().endswith((".xhtml", ".html", ".htm")))
        return htmls, None, None

    opf_root = ET.fromstring(zf.read(rootfile))
    manifest: dict[str, str] = {}
    spine_ids: list[str] = []
    title = None
    author = None

    for node in opf_root.iter():
        name = _local_name(node.tag)
        if name == "item":
            item_id = node.attrib.get("id")
            href = node.attrib.get("href")
            media_type = node.attrib.get("media-type", "")
            if item_id and href and ("html" in media_type or href.lower().endswith((".xhtml", ".html", ".htm"))):
                manifest[item_id] = href
        elif name == "itemref":
            ref = node.attrib.get("idref")
            if ref:
                spine_ids.append(ref)
        elif name == "title" and title is None and node.text:
            title = node.text.strip()
        elif name in {"creator", "author"} and author is None and node.text:
            author = node.text.strip()

    base = posixpath.dirname(rootfile)
    ordered = []
    for item_id in spine_ids:
        href = manifest.get(item_id)
        if href:
            path = posixpath.normpath(posixpath.join(base, href))
            if path in names:
                ordered.append(path)

    if not ordered:
        ordered = sorted(
            posixpath.normpath(posixpath.join(base, href))
            for href in manifest.values()
            if posixpath.normpath(posixpath.join(base, href)) in names
        )

    return ordered, title, author


def parse_epub(data: bytes, filename: str) -> ParsedBook:
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        paths, title, author = _epub_spine_paths(zf)
        segments: list[Segment] = []
        for i, path in enumerate(paths):
            try:
                raw = zf.read(path)
            except KeyError:
                continue
            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup(["script", "style", "nav"]):
                tag.decompose()
            text = _clean_text(soup.get_text("\n"))
            if text:
                label = PurePosixPath(path).stem
                segments.append(Segment(text=text, locator=f"section {i + 1}: {label}", order_index=i))

    if not segments:
        raise ValueError("No readable text sections were found in this EPUB.")

    fallback_title = PurePosixPath(filename).stem
    return ParsedBook(
        title=(title or fallback_title).strip(),
        author=(author.strip() if author else None),
        file_type="epub",
        segments=segments,
    )


def parse_book(data: bytes, filename: str) -> ParsedBook:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return parse_pdf(data, filename)
    if lower.endswith(".epub"):
        return parse_epub(data, filename)
    raise ValueError("Supported formats in v0.2 are PDF and EPUB.")
