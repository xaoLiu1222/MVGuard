import requests
from config import SILICONFLOW_API_KEY, SILICONFLOW_BASE_URL, SILICONFLOW_MODEL


class SiliconFlowClient:
    """SiliconFlow API client for vision model."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or SILICONFLOW_API_KEY
        self.base_url = SILICONFLOW_BASE_URL
        self.model = SILICONFLOW_MODEL

    def analyze_image(self, image_base64: str, prompt: str) -> str:
        """Analyze image with vision model."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0
        }

        resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        return resp.json()["choices"][0]["message"]["content"]

    def analyze_images(self, images_base64: list[str], prompt: str) -> str:
        """Analyze multiple images with vision model."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        content = [{"type": "text", "text": prompt}]
        for img in images_base64[:4]:  # Limit to 4 images
            content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 500,
            "temperature": 0
        }

        resp = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload, timeout=60)
        resp.raise_for_status()

        return resp.json()["choices"][0]["message"]["content"]
