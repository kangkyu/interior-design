"""
Room analysis service using Claude Vision
"""

import json
import base64
from typing import Optional

import anthropic
import httpx

from app.config import settings
from app.models.schemas import RoomAnalysis, FurnitureItem, RoomColors


ROOM_ANALYSIS_PROMPT = """Analyze this room photo and provide detailed information that will help with interior design modifications.

Provide your analysis in the following JSON format:
{
    "room_type": "living_room|bedroom|kitchen|bathroom|dining_room|office|other",
    "furniture": [
        {"type": "sofa", "color": "beige", "style": "modern", "position": "center-left"}
    ],
    "colors": {
        "walls": "#F5F5DC",
        "floor": "#8B4513",
        "ceiling": "#FFFFFF"
    },
    "lighting": "natural light from large window, ceiling lamp",
    "style": "modern minimalist|traditional|contemporary|bohemian|industrial|scandinavian|other",
    "features": ["large window on left wall", "fireplace", "high ceilings"],
    "dimensions_estimate": {
        "width": "4-5 meters",
        "depth": "5-6 meters",
        "ceiling_height": "2.8 meters"
    }
}

Be specific about colors (use hex codes when possible), furniture styles, and positions.
Only respond with valid JSON, no additional text."""


ROOM_CONVERSATION_PROMPT = """Based on this room analysis, generate a friendly, conversational response as an interior designer meeting a client for the first time.

Room Analysis: {analysis}

Your response should:
1. Acknowledge what you see in the room
2. Note positive aspects
3. Ask what they'd like to change

Keep it concise (2-3 sentences). Be warm and professional."""


class RoomAnalyzer:
    """Analyze room photos using Claude Vision"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def analyze_room(
        self,
        image_url: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> tuple[RoomAnalysis, str]:
        """
        Analyze a room photo and return structured data + conversational response

        Args:
            image_url: URL of the image to analyze
            image_bytes: Raw image bytes (alternative to URL)

        Returns:
            Tuple of (RoomAnalysis, conversation_response)
        """
        # Prepare image content
        if image_bytes:
            image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
            image_content = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data,
                },
            }
        elif image_url:
            # Download image and convert to base64
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = base64.standard_b64encode(response.content).decode("utf-8")
                media_type = response.headers.get("content-type", "image/jpeg")

            image_content = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                },
            }
        else:
            raise ValueError("Either image_url or image_bytes must be provided")

        # Step 1: Get structured analysis
        analysis_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        image_content,
                        {"type": "text", "text": ROOM_ANALYSIS_PROMPT},
                    ],
                }
            ],
        )

        # Parse JSON response
        analysis_text = analysis_response.content[0].text
        try:
            # Clean up response if needed
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0]
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0]

            analysis_dict = json.loads(analysis_text.strip())
        except json.JSONDecodeError:
            # Fallback to basic analysis
            analysis_dict = {
                "room_type": "living_room",
                "furniture": [],
                "colors": {},
                "lighting": "unknown",
                "style": "unknown",
                "features": [],
            }

        # Convert to Pydantic model
        analysis = RoomAnalysis(
            room_type=analysis_dict.get("room_type", "unknown"),
            furniture=[
                FurnitureItem(**f) for f in analysis_dict.get("furniture", [])
            ],
            colors=RoomColors(**analysis_dict.get("colors", {})),
            lighting=analysis_dict.get("lighting"),
            style=analysis_dict.get("style"),
            features=analysis_dict.get("features", []),
            dimensions_estimate=analysis_dict.get("dimensions_estimate"),
        )

        # Step 2: Generate conversational response
        conversation_response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": ROOM_CONVERSATION_PROMPT.format(
                        analysis=json.dumps(analysis_dict, indent=2)
                    ),
                }
            ],
        )

        conversation = conversation_response.content[0].text

        return analysis, conversation

    async def validate_room_photo(
        self,
        image_bytes: bytes,
    ) -> tuple[bool, str]:
        """
        Validate that an uploaded image is actually a room photo

        Args:
            image_bytes: Raw image bytes

        Returns:
            Tuple of (is_valid, message)
        """
        image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Is this image a photo of an interior room (living room, bedroom, kitchen, bathroom, office, etc.)?

Respond with JSON only:
{"is_room": true/false, "reason": "brief explanation"}""",
                        },
                    ],
                }
            ],
        )

        try:
            result = json.loads(response.content[0].text)
            is_valid = result.get("is_room", False)
            reason = result.get("reason", "Unknown")

            if is_valid:
                return True, "Valid room photo"
            else:
                return False, f"This doesn't appear to be a room photo: {reason}"
        except json.JSONDecodeError:
            # If we can't parse, assume it's valid
            return True, "Image accepted"


# Singleton instance
room_analyzer = RoomAnalyzer()
