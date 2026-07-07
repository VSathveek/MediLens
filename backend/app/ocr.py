"""Prescription image OCR. Requires the tesseract binary on PATH (installed
via the Dockerfile in production); fails soft with a clear message locally
if it's missing rather than crashing the request."""

import io
import logging

from PIL import Image

logger = logging.getLogger("medilens.ocr")

_TESSERACT_AVAILABLE: bool | None = None


def _check_tesseract() -> bool:
    global _TESSERACT_AVAILABLE
    if _TESSERACT_AVAILABLE is None:
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
            _TESSERACT_AVAILABLE = True
        except Exception as e:
            logger.warning("Tesseract binary not available: %s", e)
            _TESSERACT_AVAILABLE = False
    return _TESSERACT_AVAILABLE


def extract_text(image_bytes: bytes) -> str:
    if not _check_tesseract():
        raise RuntimeError(
            "OCR is not available on this server. Please type your question or medicine "
            "names directly instead of uploading an image."
        )

    import pytesseract

    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)
