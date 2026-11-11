import re


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Split text into pieces of about `size` characters, each overlapping the previous by `overlap`.

    Cuts are moved back to the nearest whitespace so words aren't split.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            space = text.rfind(" ", start + overlap + 1, end)
            if space != -1:
                end = space
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks
