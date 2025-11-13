"""Hyperbolic API client for advanced models."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, List

import aiohttp


class HyperbolicClient:
    """Async wrapper around Hyperbolic API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        base_url: str = "https://api.hyperbolic.xyz/v1",
        timeout: int = 120,
    ) -> None:
        self.api_key = api_key or os.getenv("HYPERBOLIC_API_KEY")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        messages: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request to Hyperbolic."""

        if not self.is_available():
            raise RuntimeError("Hyperbolic API key not configured (HYPERBOLIC_API_KEY)")

        session = await self._ensure_session()
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Build messages
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with session.post(url, json=payload, headers=headers, timeout=self.timeout) as resp:
            resp.raise_for_status()
            data = await resp.json()

        # Extract response
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")

        return {
            "content": content,
            "usage": data.get("usage", {}),
            "raw": data,
        }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Convenience helper returning only the generated text."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.get("content", "")

    async def analyze_image(
        self,
        prompt: str,
        image,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> str:
        """
        Analyze image using vision model (NVIDIA-Nemotron-Nano-12B-v2-VL).
        
        Args:
            prompt: Analysis prompt
            image: PIL Image object
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            
        Returns:
            Analysis text
        """
        if not self.is_available():
            raise RuntimeError("Hyperbolic API key not configured (HYPERBOLIC_API_KEY)")

        if image is None:
            return ""

        import base64
        import io

        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        session = await self._ensure_session()
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Build message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with session.post(url, json=payload, headers=headers, timeout=self.timeout) as resp:
            resp.raise_for_status()
            data = await resp.json()

        # Extract response
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")

        return content

    async def generate_with_image(
        self,
        prompt: str,
        image,
        temperature: float = 0.4,
        max_tokens: int = 2048,
    ) -> str:
        """Alias for analyze_image to match MoE orchestrator interface."""
        return await self.analyze_image(
            prompt=prompt,
            image=image,
            temperature=temperature,
            max_tokens=max_tokens,
        )
