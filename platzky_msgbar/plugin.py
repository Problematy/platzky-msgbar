"""Platzky msgbar plugin that injects a message bar into the page body."""

import logging
import re
from typing import Any

import bleach
import markdown
from platzky.plugin.html_injector import HtmlInjectorPluginBase, PageSection
from platzky.plugin.plugin import ConfigPluginError
from pydantic import ValidationError

from platzky_msgbar.config import MsgBarConfig

logger = logging.getLogger(__name__)

MSG_BAR_ID = "MsgBar"
MSG_BAR_STYLE_ID = "MsgBarStyle"
MSG_BAR_SCRIPT_ID = "MsgBarScript"
MSG_BAR_Z_INDEX = 9999
CLOSE_BUTTON_FONT_SIZE = "16px"

ALLOWED_TAGS = ["a", "strong", "em", "b", "i", "code", "br", "span"]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "span": ["class"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def _render_message(message_markdown: str) -> str:
    """Convert markdown message to sanitized HTML.

    Args:
        message_markdown: Markdown-formatted message string

    Returns:
        Sanitized HTML string safe for injection
    """
    message_html = markdown.markdown(
        message_markdown,
        extensions=["extra", "attr_list"],
        output_format="html",
    ).strip()
    # Strip all wrapping <p> tags for inline rendering in the bar
    message_html = re.sub(r"</?p>", "", message_html).strip()

    return bleach.clean(
        message_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )


def _build_bar_html(
    message: str,
    background_color: str,
    text_color: str,
    font_size: str,
    font_family: str,
    bar_height: str,
) -> str:
    """Generate the full HTML/CSS/JS block for the message bar.

    Args:
        message: Sanitized HTML message content
        background_color: CSS color for bar background
        text_color: CSS color for text
        font_size: CSS font-size value
        font_family: CSS font-family value
        bar_height: CSS height value for body padding

    Returns:
        HTML string containing style, div, and script elements
    """
    return f"""
<style id="{MSG_BAR_STYLE_ID}">

#{MSG_BAR_ID} {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: {background_color};
    color: {text_color};
    font-size: {font_size};
    font-family: {font_family};
    z-index: {MSG_BAR_Z_INDEX};
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);

    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px 10px;
}}

#{MSG_BAR_ID} .msg-content {{
    flex: 1;             /* takes full width */
    text-align: center;  /* centers the text */
}}

#{MSG_BAR_ID} .msg-content a {{
    color: inherit;
    text-decoration: underline;
    font-weight: bold;
}}

#{MSG_BAR_ID} .msg-content a:hover {{
    text-decoration: none;
    opacity: 0.8;
}}

#{MSG_BAR_ID} .close-btn {{
    position: relative;  /* required by tests */
    margin-left: auto;   /* pushes to the right */
    font-weight: bold;
    font-size: {CLOSE_BUTTON_FONT_SIZE};
    color: {text_color};
    cursor: pointer;
    background: none;
    border: none;
}}

body {{
    padding-top: {bar_height} !important;
}}

</style>
<div id="{MSG_BAR_ID}">
    <div class="msg-content">{message}</div>
    <button class="close-btn">&times;</button>
</div>
<script id="{MSG_BAR_SCRIPT_ID}">
(function() {{
    var bar = document.getElementById("{MSG_BAR_ID}");
    bar.querySelector(".close-btn").addEventListener("click", function() {{
        document.getElementById("{MSG_BAR_ID}").remove();
        document.getElementById("{MSG_BAR_STYLE_ID}").remove();
        document.getElementById("{MSG_BAR_SCRIPT_ID}").remove();
    }});
}})();
</script>
"""


class MsgBarPlugin(HtmlInjectorPluginBase):
    """Plugin that displays a customizable message bar at the top of web pages."""

    accepted_page_sections: frozenset[PageSection] = frozenset({"body"})

    def __init__(self, config: dict[str, Any]) -> None:
        """Validate the configuration and precompute the message bar HTML.

        Args:
            config: Raw configuration dict from the platzky engine.

        Raises:
            ConfigPluginError: If the configuration is invalid.
        """
        super().__init__(config)
        try:
            msgbar_config = MsgBarConfig.model_validate(config)
        except ValidationError as e:
            raise ConfigPluginError(f"Invalid configuration: {e}") from e

        # TODO: HtmlInjectorPluginBase gives plugins no access to the engine/db,
        # so the site's theme colors/font can no longer be used as a fallback
        # here (only hardcoded defaults, from MsgBarConfig's own field defaults).
        self._bar_html = _build_bar_html(
            message=_render_message(msgbar_config.message),
            background_color=msgbar_config.get_validated_background_color(),
            text_color=msgbar_config.get_validated_text_color(),
            font_size=msgbar_config.get_validated_font_size(),
            font_family=msgbar_config.get_validated_font_family(),
            bar_height=msgbar_config.get_validated_bar_height(),
        )

    def get_body_html(self) -> str:
        """Return the message bar HTML to inject at the start of the page body."""
        return self._bar_html
