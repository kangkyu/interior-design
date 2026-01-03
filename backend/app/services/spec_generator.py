"""
Specification Generator - Creates actionable specs for contractors
"""

import json
import io
import base64
from datetime import datetime
from typing import Optional

import anthropic
import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
)

from app.config import settings
from app.models.schemas import (
    DesignSpecification,
    PaintSpec,
    PaintMatch,
    FurnitureSpec,
    BudgetEstimate,
)


# Paint brand color databases (sample data - in production, use full databases)
PAINT_COLORS = {
    "benjamin_moore": [
        {"name": "White Dove", "code": "OC-17", "hex": "#F3EEE4"},
        {"name": "Sage Green", "code": "2144-40", "hex": "#9DC183"},
        {"name": "Hale Navy", "code": "HC-154", "hex": "#3A4B5C"},
        {"name": "Revere Pewter", "code": "HC-172", "hex": "#CCC7B9"},
        {"name": "Simply White", "code": "OC-117", "hex": "#F4F0E5"},
        {"name": "Chantilly Lace", "code": "OC-65", "hex": "#F5F2EB"},
        {"name": "Gray Owl", "code": "OC-52", "hex": "#C4C4BC"},
        {"name": "Kendall Charcoal", "code": "HC-166", "hex": "#4E5152"},
    ],
    "sherwin_williams": [
        {"name": "Pure White", "code": "SW 7005", "hex": "#F4F0E7"},
        {"name": "Agreeable Gray", "code": "SW 7029", "hex": "#D1CBC1"},
        {"name": "Sea Salt", "code": "SW 6204", "hex": "#C6D4CE"},
        {"name": "Alabaster", "code": "SW 7008", "hex": "#F2EDE3"},
        {"name": "Naval", "code": "SW 6244", "hex": "#2E3E4E"},
        {"name": "Repose Gray", "code": "SW 7015", "hex": "#C2BEB6"},
    ],
    "behr": [
        {"name": "Ultra Pure White", "code": "PPU18-06", "hex": "#F5F2ED"},
        {"name": "Silver Drop", "code": "PPU18-14", "hex": "#D2CCC3"},
        {"name": "Sage Green", "code": "S390-4", "hex": "#8BA888"},
        {"name": "Blueprint", "code": "S470-5", "hex": "#415C74"},
    ],
}


DESIGN_ANALYSIS_PROMPT = """Analyze this interior design image and extract detailed specifications that a contractor or designer could use to recreate this room.

Provide your analysis in this JSON format:
{
    "colors": [
        {"element": "walls", "hex": "#9DC183", "name": "sage green", "finish": "eggshell"},
        {"element": "trim", "hex": "#FFFFFF", "name": "white", "finish": "semi-gloss"}
    ],
    "flooring": {
        "type": "hardwood",
        "color": "medium oak",
        "finish": "matte",
        "pattern": "wide plank"
    },
    "furniture": [
        {
            "item": "sectional sofa",
            "style": "modern",
            "color": "charcoal gray",
            "material": "performance fabric",
            "dimensions": "110 x 85 inches"
        }
    ],
    "lighting": {
        "ambient": "recessed ceiling lights",
        "task": "floor lamp",
        "accent": "pendant light",
        "color_temperature": "2700K warm white"
    },
    "decor": [
        {"item": "area rug", "style": "geometric", "color": "cream and gray"},
        {"item": "indoor plant", "type": "fiddle leaf fig", "size": "large"}
    ],
    "summary": ["Changed walls to sage green", "Added modern gray sectional"]
}

Be specific about colors (use hex codes), dimensions, and styles.
Only respond with valid JSON."""


class SpecificationGenerator:
    """Generate actionable specifications from final design"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def generate_spec(
        self,
        final_image_url: str,
        original_image_url: str,
        project_id: str,
        project_name: str,
        conversation_summary: Optional[list[str]] = None,
    ) -> DesignSpecification:
        """
        Generate complete specification from final design

        Args:
            final_image_url: URL of the final design image
            original_image_url: URL of the original room photo
            project_id: Project UUID
            project_name: Project name
            conversation_summary: List of changes discussed

        Returns:
            DesignSpecification with all details
        """
        # Step 1: Analyze the final design image
        analysis = await self._analyze_design(final_image_url)

        # Step 2: Match colors to paint brands
        paint_specs = self._match_paints(analysis.get("colors", []))

        # Step 3: Generate furniture specs with product suggestions
        furniture_specs = self._generate_furniture_specs(analysis.get("furniture", []))

        # Step 4: Calculate budget estimates
        budget = self._estimate_budget(paint_specs, furniture_specs, analysis)

        # Step 5: Build the specification
        return DesignSpecification(
            project_id=project_id,
            project_name=project_name,
            generated_at=datetime.utcnow(),
            before_image_url=original_image_url,
            after_image_url=final_image_url,
            summary_of_changes=analysis.get("summary", conversation_summary or []),
            paint=paint_specs,
            flooring=analysis.get("flooring"),
            furniture=furniture_specs,
            lighting=analysis.get("lighting"),
            decor=analysis.get("decor", []),
            budget=budget,
            total_budget_low=sum(b.low for b in budget),
            total_budget_high=sum(b.high for b in budget),
        )

    async def _analyze_design(self, image_url: str) -> dict:
        """Use Claude Vision to analyze the design image"""
        # Download image and convert to base64
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = base64.standard_b64encode(response.content).decode("utf-8")
            media_type = response.headers.get("content-type", "image/jpeg")

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": DESIGN_ANALYSIS_PROMPT},
                    ],
                }
            ],
        )

        response_text = response.content[0].text

        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            return {}

    def _match_paints(self, colors: list[dict]) -> list[PaintSpec]:
        """Match hex colors to paint brand codes"""
        paint_specs = []

        for color in colors:
            hex_code = color.get("hex", "#FFFFFF")
            element = color.get("element", "walls")
            finish = color.get("finish", "eggshell")

            matches = []
            for brand, brand_colors in PAINT_COLORS.items():
                closest = self._find_closest_color(hex_code, brand_colors)
                if closest:
                    matches.append(
                        PaintMatch(
                            brand=brand.replace("_", " ").title(),
                            name=closest["name"],
                            code=closest["code"],
                            hex=closest["hex"],
                        )
                    )

            paint_specs.append(
                PaintSpec(
                    element=element,
                    hex=hex_code,
                    matches=matches,
                    finish=finish,
                    coverage_sqft=self._estimate_coverage(element),
                    gallons_needed=self._estimate_gallons(element),
                )
            )

        return paint_specs

    def _find_closest_color(
        self,
        target_hex: str,
        colors: list[dict],
    ) -> Optional[dict]:
        """Find the closest color match using simple RGB distance"""

        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip("#")
            return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

        def color_distance(hex1: str, hex2: str) -> float:
            r1, g1, b1 = hex_to_rgb(hex1)
            r2, g2, b2 = hex_to_rgb(hex2)
            return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

        closest = None
        min_distance = float("inf")

        for color in colors:
            try:
                distance = color_distance(target_hex, color["hex"])
                if distance < min_distance:
                    min_distance = distance
                    closest = color
            except (ValueError, KeyError):
                continue

        return closest

    def _estimate_coverage(self, element: str) -> float:
        """Estimate square footage for different elements"""
        estimates = {
            "walls": 400.0,
            "accent_wall": 100.0,
            "ceiling": 300.0,
            "trim": 50.0,
        }
        return estimates.get(element, 200.0)

    def _estimate_gallons(self, element: str) -> float:
        """Estimate gallons needed (350 sqft per gallon, 2 coats)"""
        sqft = self._estimate_coverage(element)
        return round((sqft / 350) * 2, 1)

    def _generate_furniture_specs(self, furniture: list[dict]) -> list[FurnitureSpec]:
        """Generate furniture specs with product suggestions"""
        specs = []

        # Product suggestions database (simplified)
        suggestions = {
            "sofa": [
                {"store": "West Elm", "product": "Andes Sectional", "price": "$2,999"},
                {"store": "Article", "product": "Sven Sectional", "price": "$2,399"},
                {"store": "IKEA", "product": "Söderhamn", "price": "$1,299"},
            ],
            "coffee table": [
                {"store": "CB2", "product": "Frame Coffee Table", "price": "$599"},
                {"store": "West Elm", "product": "Mid-Century Pop-Up", "price": "$499"},
                {"store": "IKEA", "product": "Stockholm", "price": "$249"},
            ],
            "chair": [
                {"store": "Herman Miller", "product": "Eames Lounge", "price": "$6,995"},
                {"store": "Article", "product": "Sven Chair", "price": "$999"},
                {"store": "IKEA", "product": "Poäng", "price": "$149"},
            ],
            "rug": [
                {"store": "Ruggable", "product": "Area Rug 8x10", "price": "$499"},
                {"store": "West Elm", "product": "Abstract Rug", "price": "$799"},
                {"store": "Rugs USA", "product": "Contemporary", "price": "$299"},
            ],
        }

        for item in furniture:
            item_type = item.get("item", "").lower()
            similar = []

            # Find matching suggestions
            for key, products in suggestions.items():
                if key in item_type:
                    similar = products
                    break

            specs.append(
                FurnitureSpec(
                    item=item.get("item", "Unknown"),
                    style=item.get("style", "Modern"),
                    color=item.get("color", "Neutral"),
                    material=item.get("material"),
                    dimensions=item.get("dimensions"),
                    similar_products=similar,
                    price_range=self._get_price_range(item_type),
                )
            )

        return specs

    def _get_price_range(self, item_type: str) -> str:
        """Get typical price range for furniture type"""
        ranges = {
            "sofa": "$1,000 - $4,000",
            "sectional": "$1,500 - $5,000",
            "chair": "$200 - $1,500",
            "table": "$200 - $800",
            "coffee table": "$150 - $600",
            "rug": "$200 - $1,000",
            "lamp": "$50 - $300",
            "plant": "$30 - $200",
        }

        for key, price in ranges.items():
            if key in item_type.lower():
                return price

        return "$100 - $500"

    def _estimate_budget(
        self,
        paint_specs: list[PaintSpec],
        furniture_specs: list[FurnitureSpec],
        analysis: dict,
    ) -> list[BudgetEstimate]:
        """Estimate total project budget"""
        budget = []

        # Paint
        if paint_specs:
            gallons = sum(p.gallons_needed or 0 for p in paint_specs)
            budget.append(
                BudgetEstimate(
                    category="Paint & Supplies",
                    low=gallons * 40,  # $40/gallon budget paint
                    high=gallons * 80,  # $80/gallon premium paint
                )
            )

        # Flooring (if mentioned)
        if analysis.get("flooring"):
            budget.append(
                BudgetEstimate(
                    category="Flooring",
                    low=2000,
                    high=5000,
                )
            )

        # Furniture
        if furniture_specs:
            # Parse price ranges and sum
            low = 0
            high = 0
            for spec in furniture_specs:
                if spec.price_range:
                    try:
                        parts = spec.price_range.replace("$", "").replace(",", "").split(" - ")
                        low += float(parts[0])
                        high += float(parts[1]) if len(parts) > 1 else float(parts[0])
                    except (ValueError, IndexError):
                        low += 200
                        high += 500

            budget.append(
                BudgetEstimate(
                    category="Furniture",
                    low=low,
                    high=high,
                )
            )

        # Lighting
        if analysis.get("lighting"):
            budget.append(
                BudgetEstimate(
                    category="Lighting",
                    low=200,
                    high=800,
                )
            )

        # Decor
        if analysis.get("decor"):
            budget.append(
                BudgetEstimate(
                    category="Decor & Plants",
                    low=len(analysis["decor"]) * 50,
                    high=len(analysis["decor"]) * 200,
                )
            )

        # Labor (optional)
        budget.append(
            BudgetEstimate(
                category="Labor (optional)",
                low=500,
                high=2000,
            )
        )

        return budget

    async def generate_pdf(
        self,
        spec: DesignSpecification,
    ) -> bytes:
        """Generate a professional PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=24,
            spaceAfter=30,
        )
        heading_style = ParagraphStyle(
            "Heading",
            parent=styles["Heading1"],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
        )
        body_style = styles["Normal"]

        story = []

        # Title
        story.append(Paragraph("Interior Design Specification", title_style))
        story.append(Paragraph(f"Project: {spec.project_name}", body_style))
        story.append(
            Paragraph(
                f"Generated: {spec.generated_at.strftime('%B %d, %Y')}",
                body_style,
            )
        )
        story.append(Spacer(1, 30))

        # Summary of Changes
        story.append(Paragraph("Summary of Changes", heading_style))
        for change in spec.summary_of_changes:
            story.append(Paragraph(f"• {change}", body_style))
        story.append(Spacer(1, 20))

        # Paint Specifications
        if spec.paint:
            story.append(Paragraph("Paint Specifications", heading_style))
            for paint in spec.paint:
                story.append(
                    Paragraph(
                        f"<b>{paint.element.title()}</b> - {paint.hex}",
                        body_style,
                    )
                )
                if paint.finish:
                    story.append(Paragraph(f"  Finish: {paint.finish}", body_style))
                if paint.gallons_needed:
                    story.append(
                        Paragraph(
                            f"  Estimated: {paint.gallons_needed} gallons",
                            body_style,
                        )
                    )
                for match in paint.matches:
                    story.append(
                        Paragraph(
                            f"  • {match.brand}: {match.name} ({match.code})",
                            body_style,
                        )
                    )
                story.append(Spacer(1, 10))

        # Furniture
        if spec.furniture:
            story.append(PageBreak())
            story.append(Paragraph("Furniture Shopping List", heading_style))
            for i, item in enumerate(spec.furniture, 1):
                story.append(
                    Paragraph(f"<b>{i}. {item.item}</b>", body_style)
                )
                story.append(
                    Paragraph(
                        f"   Style: {item.style} | Color: {item.color}",
                        body_style,
                    )
                )
                if item.dimensions:
                    story.append(
                        Paragraph(f"   Dimensions: {item.dimensions}", body_style)
                    )
                if item.price_range:
                    story.append(
                        Paragraph(f"   Price Range: {item.price_range}", body_style)
                    )
                if item.similar_products:
                    story.append(Paragraph("   Where to Buy:", body_style))
                    for product in item.similar_products[:3]:
                        story.append(
                            Paragraph(
                                f"     • {product['store']}: {product['product']} ({product['price']})",
                                body_style,
                            )
                        )
                story.append(Spacer(1, 10))

        # Budget
        story.append(PageBreak())
        story.append(Paragraph("Budget Estimate", heading_style))

        budget_data = [["Category", "Low", "High"]]
        for item in spec.budget:
            budget_data.append(
                [item.category, f"${item.low:,.0f}", f"${item.high:,.0f}"]
            )
        budget_data.append(
            [
                "TOTAL",
                f"${spec.total_budget_low:,.0f}",
                f"${spec.total_budget_high:,.0f}",
            ]
        )

        budget_table = Table(budget_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
        budget_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(budget_table)

        # Build PDF
        doc.build(story)
        return buffer.getvalue()


# Singleton instance
spec_generator = SpecificationGenerator()
