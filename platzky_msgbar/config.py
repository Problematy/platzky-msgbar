"""Pydantic configuration model for msgbar plugin with CSS injection protection."""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_extra_types.color import Color


class MsgBarConfig(BaseModel):
    """
    Configuration model for the msgbar plugin.

    All CSS values are validated to prevent CSS injection attacks.
    """

    message: str = Field(
        description="The message to display in the bar (supports Markdown)",
    )

    background_color: Optional[str] = Field(
        default=None,
        description="CSS color value for background (hex, rgb/rgba, hsl/hsla, or color name)",
    )

    text_color: Optional[str] = Field(
        default=None,
        description="CSS color value for text (hex, rgb/rgba, hsl/hsla, or color name)",
    )

    font_family: Optional[str] = Field(
        default=None, description="CSS font-family value"
    )

    font_size: Optional[str] = Field(
        default=None, description="CSS font-size value (e.g., '14px', '1rem')"
    )

    bar_height: Optional[str] = Field(
        default=None, description="CSS height value (e.g., '30px', '2rem')"
    )

    @field_validator("background_color", "text_color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate color values using Pydantic's Color type.

        Accepts hex, rgb/rgba, hsl/hsla, and named colors.
        Returns the original valid value or None if invalid.
        """
        if v is None:
            return None

        try:
            # Use Pydantic's Color validator to check if the color is valid
            # We only care if it raises an exception, not the parsed result
            Color(v)
            # Return the original value if valid (preserves user's format choice)
            return v
        except Exception:
            # If validation fails, return None to use defaults
            return None

    @field_validator("font_size", "bar_height")
    @classmethod
    def validate_size(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate CSS size values.

        Accepts: number + unit (px, em, rem, %, vh, vw)
        Rejects dangerous patterns that could break CSS context.
        """
        if v is None:
            return None

        v = v.strip()

        # Validate format: positive number + safe unit
        if not re.match(r"^\d+(\.\d+)?(px|em|rem|%|vh|vw)$", v):
            return None

        # Additional check: ensure no dangerous characters
        if re.search(r"[;{}\\<>]", v):
            return None

        return v

    @field_validator("font_family")
    @classmethod
    def validate_font_family(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate CSS font-family value.

        Prevents CSS injection by:
        - Rejecting dangerous characters (;, {, }, \\, <, >)
        - Rejecting CSS functions (url, calc, var, attr)
        - Limiting length to prevent DoS
        """
        if v is None:
            return None

        v = v.strip()

        # Reject if too long (DoS prevention)
        if len(v) > 200:
            return None

        # Reject dangerous characters that could break CSS context
        if re.search(r"[;{}\\<>]", v):
            return None

        # Reject CSS functions that could be exploited
        if re.search(r"(url|calc|var|attr|expression)\s*\(", v, re.IGNORECASE):
            return None

        return v

    def get_validated_background_color(self, fallback: str = "#245466") -> str:
        """Get validated background color or fallback."""
        return self.background_color or fallback

    def get_validated_text_color(self, fallback: str = "white") -> str:
        """Get validated text color or fallback."""
        return self.text_color or fallback

    def get_validated_font_family(self, fallback: str = "'Arial', sans-serif") -> str:
        """Get validated font family or fallback."""
        return self.font_family or fallback

    def get_validated_font_size(self, fallback: str = "14px") -> str:
        """Get validated font size or fallback."""
        return self.font_size or fallback

    def get_validated_bar_height(self, fallback: str = "30px") -> str:
        """Get validated bar height or fallback."""
        return self.bar_height or fallback
