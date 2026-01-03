"""
Design Orchestrator - The brain of the application
Coordinates chat understanding, image generation, and responses
"""

import json
from typing import Optional
from dataclasses import dataclass

import anthropic

from app.config import settings
from app.models.schemas import (
    RoomAnalysis,
    DesignChange,
    DesignUnderstanding,
    ChangeType,
)
from app.services.image_generator import image_generator, GeneratedImage


@dataclass
class DesignResponse:
    """Response from the orchestrator"""
    type: str  # "design", "clarification", "error"
    message: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    version: Optional[int] = None
    changes: Optional[list[DesignChange]] = None


@dataclass
class DesignSession:
    """Current state of a design session"""
    project_id: str
    room_analysis: Optional[RoomAnalysis] = None
    current_image_url: Optional[str] = None
    original_image_url: Optional[str] = None
    depth_map_url: Optional[str] = None
    current_version: int = 0
    conversation_history: list = None

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []


UNDERSTANDING_SYSTEM_PROMPT = """You are an AI interior design assistant. Your job is to understand what design changes the user wants and translate them into actionable instructions for image generation.

Given the user's message, determine:

1. CHANGES: What specific elements to modify
   - walls, floor, ceiling, furniture, lighting, decor, style

2. CHANGE_TYPE: How significant is the change?
   - "minor": Color/material change only (wall paint, floor stain)
   - "moderate": Adding/removing/replacing items (new sofa, remove table)
   - "major": Complete style overhaul (modern to bohemian)

3. GENERATION_PROMPT: A detailed prompt for image generation
   - Include ALL visible elements from the room analysis
   - Describe the requested changes specifically
   - Keep elements that should stay the same
   - Use descriptive adjectives for style, color, material

4. NEEDS_CLARIFICATION: Is the request too vague?
   - If yes, provide a natural clarifying question

Respond ONLY in this JSON format:
{
    "changes": [
        {"element": "walls", "action": "change_color", "value": "sage green"}
    ],
    "change_type": "minor",
    "generation_prompt": "Interior photo of a modern living room with sage green walls, hardwood floors, gray sectional sofa, natural lighting...",
    "needs_clarification": false,
    "clarification_question": null
}"""


RESPONSE_SYSTEM_PROMPT = """You are a friendly interior design assistant. Generate a brief, conversational response about the design changes that were just made.

Be warm and helpful. Mention what was changed and suggest what they might want to adjust next.
Keep it to 2-3 sentences max."""


class DesignOrchestrator:
    """
    The brain of the app - takes chat input, produces design output
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def process_message(
        self,
        user_message: str,
        session: DesignSession,
    ) -> DesignResponse:
        """
        Main entry point - process user's chat message

        Args:
            user_message: What the user said
            session: Current design session state

        Returns:
            DesignResponse with message, image, etc.
        """
        # Check if we have a room to work with
        if not session.current_image_url:
            return DesignResponse(
                type="error",
                message="Please upload a room photo first so I can help you redesign it!",
            )

        # Step 1: Understand what user wants
        understanding = await self._understand_request(
            message=user_message,
            session=session,
        )

        # Step 2: Check if we need clarification
        if understanding.needs_clarification:
            return DesignResponse(
                type="clarification",
                message=understanding.clarification_question,
            )

        # Step 3: Generate new design
        try:
            new_image = await image_generator.generate(
                prompt=understanding.generation_prompt,
                base_image_url=session.current_image_url,
                depth_map_url=session.depth_map_url,
                change_type=understanding.change_type.value,
            )
        except Exception as e:
            return DesignResponse(
                type="error",
                message=f"I had trouble generating the design. Let me try again. Error: {str(e)}",
            )

        # Step 4: Generate conversational response
        response_message = await self._generate_response(
            changes=understanding.changes,
            change_type=understanding.change_type,
        )

        # Update session
        new_version = session.current_version + 1

        return DesignResponse(
            type="design",
            message=response_message,
            image_url=new_image.url,
            thumbnail_url=new_image.thumbnail_url,
            version=new_version,
            changes=understanding.changes,
        )

    async def _understand_request(
        self,
        message: str,
        session: DesignSession,
    ) -> DesignUnderstanding:
        """
        Use Claude to understand what the user wants
        """
        # Build context from room analysis
        room_context = ""
        if session.room_analysis:
            room_context = f"""
Room Type: {session.room_analysis.room_type}
Current Style: {session.room_analysis.style}
Furniture: {', '.join([f.type for f in session.room_analysis.furniture])}
Wall Color: {session.room_analysis.colors.walls}
Floor: {session.room_analysis.colors.floor}
Features: {', '.join(session.room_analysis.features)}
"""

        # Build conversation history context
        history_context = ""
        if session.conversation_history:
            recent_history = session.conversation_history[-6:]  # Last 3 exchanges
            history_context = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in recent_history
            ])

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=UNDERSTANDING_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"""
ROOM CONTEXT:
{room_context}

RECENT CONVERSATION:
{history_context}

CURRENT DESIGN VERSION: {session.current_version}

USER'S REQUEST: "{message}"

Analyze this request and provide structured instructions for image generation.
""",
                }
            ],
        )

        # Parse response
        response_text = response.content[0].text

        try:
            # Clean up JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            data = json.loads(response_text.strip())
        except json.JSONDecodeError:
            # Fallback if parsing fails
            return DesignUnderstanding(
                changes=[DesignChange(element="general", action="update", value=message)],
                change_type=ChangeType.MODERATE,
                generation_prompt=f"Interior design photo, {message}, professional photography, high quality",
                needs_clarification=False,
            )

        # Convert to Pydantic model
        changes = [DesignChange(**c) for c in data.get("changes", [])]

        change_type_str = data.get("change_type", "moderate")
        try:
            change_type = ChangeType(change_type_str)
        except ValueError:
            change_type = ChangeType.MODERATE

        return DesignUnderstanding(
            changes=changes,
            change_type=change_type,
            generation_prompt=data.get("generation_prompt", ""),
            needs_clarification=data.get("needs_clarification", False),
            clarification_question=data.get("clarification_question"),
        )

    async def _generate_response(
        self,
        changes: list[DesignChange],
        change_type: ChangeType,
    ) -> str:
        """
        Generate a conversational response about the changes made
        """
        changes_description = ", ".join([
            f"{c.action} {c.element}" + (f" to {c.value}" if c.value else "")
            for c in changes
        ])

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=RESPONSE_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Changes made: {changes_description}. Change magnitude: {change_type.value}.",
                }
            ],
        )

        return response.content[0].text

    async def generate_initial_suggestions(
        self,
        room_analysis: RoomAnalysis,
    ) -> str:
        """
        Generate initial suggestions based on room analysis
        """
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[
                {
                    "role": "user",
                    "content": f"""As an interior designer, I've analyzed this room:
- Type: {room_analysis.room_type}
- Style: {room_analysis.style}
- Main furniture: {', '.join([f.type for f in room_analysis.furniture[:3]])}
- Wall color: {room_analysis.colors.walls}

Generate a brief, friendly greeting acknowledging what I see and asking what changes they'd like to make. 2-3 sentences max.""",
                }
            ],
        )

        return response.content[0].text


# Singleton instance
orchestrator = DesignOrchestrator()
