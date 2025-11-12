"""
OCR-assisted vision helpers for Skyrim AGI.

Provides optional HUD extraction so the agent can obtain precise health,
stamina, magicka, and location data when OCR tools are available.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

try:
    import easyocr  # type: ignore
    _EASY_OCR_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    easyocr = None
    _EASY_OCR_AVAILABLE = False

try:
    import pytesseract  # type: ignore
    from PIL import Image
    _PYTESSERACT_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    pytesseract = None
    Image = None
    _PYTESSERACT_AVAILABLE = False


class EnhancedVision:
    """Optional OCR utilities."""

    def __init__(self) -> None:
        self.reader = self._init_reader()
        self.ui_regions = {
            "health_bar": (60, 1000, 460, 1040),
            "magicka_bar": (60, 1040, 460, 1080),
            "stamina_bar": (60, 1080, 460, 1120),
            "location_text": (700, 40, 1220, 120),
            "compass": (700, 0, 1220, 60),
        }

    def _init_reader(self) -> Optional[Any]:
        if _EASY_OCR_AVAILABLE:
            try:
                return easyocr.Reader(["en"], gpu=False)
            except Exception:
                return None
        return None

    def extract_hud_info(self, screenshot: Any) -> Dict[str, Any]:
        info: Dict[str, Any] = {}
        if screenshot is None:
            return info

        if self.reader:
            info.update(self._extract_with_easyocr(screenshot))
        elif _PYTESSERACT_AVAILABLE and Image is not None:
            info.update(self._extract_with_pytesseract(screenshot))

        return info

    def _extract_with_easyocr(self, screenshot: Any) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        try:
            for key, region in self.ui_regions.items():
                cropped = self._crop_image(screenshot, region)
                if cropped is None:
                    continue
                result = self.reader.readtext(cropped, detail=0)
                if result:
                    data[key] = " ".join(result)
        except Exception:
            pass
        return self._post_process(data)

    def _extract_with_pytesseract(self, screenshot: Any) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        try:
            for key, region in self.ui_regions.items():
                cropped = self._crop_image(screenshot, region)
                if cropped is None:
                    continue
                text = pytesseract.image_to_string(cropped)
                if text:
                    data[key] = text
        except Exception:
            pass
        return self._post_process(data)

    def _crop_image(self, screenshot: Any, region: tuple) -> Optional[Any]:
        try:
            if hasattr(screenshot, "crop"):
                left, top, right, bottom = region
                return screenshot.crop((left, top, right, bottom))
        except Exception:
            return None
        return None

    def _post_process(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        processed: Dict[str, Any] = {}
        if "health_bar" in raw:
            processed["health_percent"] = self._extract_percentage(raw["health_bar"])
        if "magicka_bar" in raw:
            processed["magicka_percent"] = self._extract_percentage(raw["magicka_bar"])
        if "stamina_bar" in raw:
            processed["stamina_percent"] = self._extract_percentage(raw["stamina_bar"])
        if "location_text" in raw:
            processed["location"] = raw["location_text"].strip()
        return processed

    def _extract_percentage(self, text: str) -> Optional[float]:
        if not text:
            return None
        import re

        match = re.search(r"(\d{1,3})", text)
        if not match:
            return None
        value = float(match.group(1))
        return max(0.0, min(100.0, value))

    def detect_interactive_prompt(self, screenshot: Any) -> Optional[str]:
        info = self.extract_hud_info(screenshot)
        prompt = info.get("prompt")
        if prompt:
            return prompt
        return None
