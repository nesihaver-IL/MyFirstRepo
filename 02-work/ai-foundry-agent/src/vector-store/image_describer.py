"""Image description generator using GPT-4o Vision."""

import base64
import logging
from typing import Optional
from pathlib import Path
from PIL import Image
import io
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class ImageDescriber:
    """Generates descriptions of images using GPT-4o Vision."""

    def __init__(
        self,
        openai_client: AzureOpenAI,
        model: str = "gpt-4o",
        max_image_size: tuple = (1024, 1024),
    ):
        """Initialize Image Describer.

        Args:
            openai_client: Azure OpenAI client
            model: Vision model to use (default: gpt-4o)
            max_image_size: Maximum image dimensions for processing
        """
        self.openai_client = openai_client
        self.model = model
        self.max_image_size = max_image_size

    def describe_image(
        self,
        image_path: str,
        context: Optional[str] = None,
        detail_level: str = "high",
    ) -> str:
        """Generate a description of an image.

        Args:
            image_path: Path to the image file
            context: Optional context about the image (e.g., slide title)
            detail_level: Level of detail ("low", "high", "auto")

        Returns:
            Text description of the image
        """
        try:
            # Load and prepare image
            image_data = self._prepare_image(image_path)

            # Build prompt
            prompt = self._build_prompt(context)

            # Call GPT-4o Vision
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": detail_level,
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            description = response.choices[0].message.content
            logger.info(f"Generated description for {image_path}")
            return description

        except Exception as e:
            logger.error(f"Error describing image {image_path}: {e}")
            return f"[Image: {Path(image_path).name} - description unavailable]"

    def describe_image_from_bytes(
        self,
        image_bytes: bytes,
        image_name: str = "image",
        context: Optional[str] = None,
        detail_level: str = "high",
    ) -> str:
        """Generate a description of an image from bytes.

        Args:
            image_bytes: Image data as bytes
            image_name: Name of the image for logging
            context: Optional context about the image
            detail_level: Level of detail ("low", "high", "auto")

        Returns:
            Text description of the image
        """
        try:
            # Prepare image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            image_data = self._resize_and_encode_image(image)

            # Build prompt
            prompt = self._build_prompt(context)

            # Call GPT-4o Vision
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}",
                                    "detail": detail_level,
                                },
                            },
                        ],
                    }
                ],
                max_tokens=500,
            )

            description = response.choices[0].message.content
            logger.info(f"Generated description for {image_name}")
            return description

        except Exception as e:
            logger.error(f"Error describing image {image_name}: {e}")
            return f"[Image: {image_name} - description unavailable]"

    def _prepare_image(self, image_path: str) -> str:
        """Load, resize, and encode image to base64.

        Args:
            image_path: Path to the image

        Returns:
            Base64-encoded image string
        """
        image = Image.open(image_path)
        return self._resize_and_encode_image(image)

    def _resize_and_encode_image(self, image: Image.Image) -> str:
        """Resize and encode image to base64.

        Args:
            image: PIL Image object

        Returns:
            Base64-encoded image string
        """
        # Convert to RGB if necessary
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")

        # Resize if too large
        if (
            image.width > self.max_image_size[0]
            or image.height > self.max_image_size[1]
        ):
            image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)

        # Encode to base64
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _build_prompt(self, context: Optional[str] = None) -> str:
        """Build prompt for image description.

        Args:
            context: Optional context about the image

        Returns:
            Prompt string
        """
        base_prompt = (
            "Describe this image in detail for a knowledge retrieval system. "
            "Include:\n"
            "- Main subject or content\n"
            "- Key visual elements (charts, diagrams, text, etc.)\n"
            "- Important data or information shown\n"
            "- Overall purpose or message\n\n"
            "Be concise but comprehensive."
        )

        if context:
            return f"{base_prompt}\n\nContext: {context}"

        return base_prompt
