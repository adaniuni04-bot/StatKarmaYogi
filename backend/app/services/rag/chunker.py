import re
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Normalizes whitespace and strips control characters."""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def chunk_document_text(
    text: str,
    chunk_size: int = 600,
    chunk_overlap: int = 100,
    page_number: int = 1
) -> List[Dict[str, Any]]:
    cleaned = clean_text(text)
    if not cleaned:
        return []

    words = cleaned.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        # Detect potential section header from beginning of chunk
        match = re.match(r'^(?:Chapter|Section|\d+\.|\b[A-Z\s]{4,}\b)', chunk_text)
        header = match.group(0).strip() if match else None

        # Detect competency keyword
        comp_tag = "GENERAL"
        text_lower = chunk_text.lower()
        if "sampling" in text_lower or "strata" in text_lower or "cluster" in text_lower:
            comp_tag = "SAMPLING"
        elif "survey" in text_lower or "questionnaire" in text_lower:
            comp_tag = "SURVEY_DESIGN"
        elif "quality" in text_lower or "nqaf" in text_lower:
            comp_tag = "DATA_QUALITY"
        elif "national accounts" in text_lower or "gdp" in text_lower or "sna" in text_lower:
            comp_tag = "NATIONAL_ACCOUNTS"
        elif "python" in text_lower or "pandas" in text_lower:
            comp_tag = "PYTHON"
        elif "sql" in text_lower or "query" in text_lower:
            comp_tag = "SQL"

        chunks.append({
            "content": chunk_text,
            "page_number": page_number,
            "section_header": header,
            "competency_code": comp_tag,
            "token_count": len(chunk_words)
        })

        if end >= len(words):
            break
        start += (chunk_size - chunk_overlap)

    return chunks
