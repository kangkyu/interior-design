"""
Image generation service using Replicate (Stable Diffusion / Flux)
"""

import replicate
from typing import Optional
from dataclasses import dataclass

from app.config import settings
from app.services.storage import storage_service


@dataclass
class GeneratedImage:
    """Result of image generation"""
    url: str
    thumbnail_url: Optional[str] = None
    prompt: str = ""
    seed: Optional[int] = None
    params: Optional[dict] = None


# Generation parameters based on change type
GENERATION_PARAMS = {
    "minor": {
        "strength": 0.35,
        "controlnet_weight": 0.9,
        "description": "Color/material changes only",
    },
    "moderate": {
        "strength": 0.55,
        "controlnet_weight": 0.8,
        "description": "Adding/removing items",
    },
    "major": {
        "strength": 0.75,
        "controlnet_weight": 0.7,
        "description": "Complete style overhaul",
    },
}


NEGATIVE_PROMPT = """blurry, distorted, low quality, cartoon, painting, sketch,
unrealistic proportions, watermark, text, bad lighting, oversaturated,
undersaturated, deformed furniture, weird angles, bad perspective,
extra limbs, mutation, ugly, duplicate, morbid"""


class ImageGenerator:
    """Generate interior design images using Stable Diffusion"""

    def __init__(self):
        self.client = replicate.Client(api_token=settings.replicate_api_token)

    async def generate(
        self,
        prompt: str,
        base_image_url: Optional[str] = None,
        depth_map_url: Optional[str] = None,
        change_type: str = "moderate",
        seed: Optional[int] = None,
    ) -> GeneratedImage:
        """
        Generate a new interior design image

        Args:
            prompt: Text prompt describing the desired design
            base_image_url: URL of the current room image (for img2img)
            depth_map_url: URL of the depth map (for ControlNet)
            change_type: "minor", "moderate", or "major"
            seed: Random seed for reproducibility

        Returns:
            GeneratedImage with URL and metadata
        """
        params = GENERATION_PARAMS.get(change_type, GENERATION_PARAMS["moderate"])

        # Build the full prompt
        full_prompt = self._build_prompt(prompt)

        # Prepare input for Replicate
        input_params = {
            "prompt": full_prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 768,
        }

        # Add img2img parameters if we have a base image
        if base_image_url:
            input_params["image"] = base_image_url
            input_params["strength"] = params["strength"]

        # Add seed if provided
        if seed:
            input_params["seed"] = seed

        # Add ControlNet if we have a depth map
        if depth_map_url:
            input_params["control_image"] = depth_map_url
            input_params["controlnet_conditioning_scale"] = params["controlnet_weight"]

        # Run generation
        try:
            # Using SDXL for high-quality interior design images
            output = self.client.run(
                "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
                input=input_params,
            )

            # Output is a list of URLs
            if isinstance(output, list) and len(output) > 0:
                generated_url = output[0]
            else:
                generated_url = str(output)

            # Upload to our storage for persistence
            stored_url = await storage_service.upload_from_url(
                image_url=generated_url,
                folder="generated",
            )

            # Create thumbnail
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(generated_url)
                thumbnail_url = await storage_service.create_thumbnail(
                    image_bytes=response.content,
                    folder="thumbnails",
                )

            return GeneratedImage(
                url=stored_url,
                thumbnail_url=thumbnail_url,
                prompt=full_prompt,
                seed=seed,
                params=params,
            )

        except Exception as e:
            raise RuntimeError(f"Image generation failed: {str(e)}")

    async def generate_depth_map(
        self,
        image_url: str,
    ) -> str:
        """
        Generate a depth map from an image using MiDaS

        Args:
            image_url: URL of the source image

        Returns:
            URL of the depth map image
        """
        try:
            output = self.client.run(
                "cjwbw/midas:a]5f1f0f0d9a8e9c8a9d8e9c8a9d8e9c8a",  # MiDaS depth estimation
                input={"image": image_url},
            )

            if isinstance(output, list) and len(output) > 0:
                depth_url = output[0]
            else:
                depth_url = str(output)

            # Store depth map
            stored_url = await storage_service.upload_from_url(
                image_url=depth_url,
                folder="depth_maps",
            )

            return stored_url

        except Exception:
            # Depth map is optional, return None if it fails
            return None

    def _build_prompt(self, user_prompt: str) -> str:
        """Build a complete prompt for interior design generation"""
        base_elements = [
            "interior design photo",
            "professional interior photography",
            "high quality",
            "8k resolution",
            "photorealistic",
            "natural lighting",
            "architectural digest style",
        ]

        # Combine user prompt with base elements
        full_prompt = f"{user_prompt}, {', '.join(base_elements)}"

        return full_prompt

    async def inpaint(
        self,
        image_url: str,
        mask_url: str,
        prompt: str,
        seed: Optional[int] = None,
    ) -> GeneratedImage:
        """
        Inpaint a specific area of an image

        Args:
            image_url: URL of the source image
            mask_url: URL of the mask (white = change, black = keep)
            prompt: What to generate in the masked area
            seed: Random seed for reproducibility

        Returns:
            GeneratedImage with URL and metadata
        """
        full_prompt = self._build_prompt(prompt)

        input_params = {
            "image": image_url,
            "mask": mask_url,
            "prompt": full_prompt,
            "negative_prompt": NEGATIVE_PROMPT,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        }

        if seed:
            input_params["seed"] = seed

        try:
            output = self.client.run(
                "stability-ai/stable-diffusion-inpainting",
                input=input_params,
            )

            if isinstance(output, list) and len(output) > 0:
                generated_url = output[0]
            else:
                generated_url = str(output)

            # Store the result
            stored_url = await storage_service.upload_from_url(
                image_url=generated_url,
                folder="generated",
            )

            return GeneratedImage(
                url=stored_url,
                prompt=full_prompt,
                seed=seed,
            )

        except Exception as e:
            raise RuntimeError(f"Inpainting failed: {str(e)}")


# Singleton instance
image_generator = ImageGenerator()
