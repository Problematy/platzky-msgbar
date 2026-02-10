"""Platzky msgbar plugin that injects a message bar into HTML responses."""

import logging
import re
from typing import cast

import bleach
import markdown
from flask import Response
from platzky.plugin.plugin import PluginBase

from platzky_msgbar.config import MsgBarConfig

logger = logging.getLogger(__name__)

MSG_BAR_ID = "MsgBar"
MSG_BAR_STYLE_ID = "MsgBarStyle"
MSG_BAR_SCRIPT_ID = "MsgBarScript"
MSG_BAR_Z_INDEX = 9999
CLOSE_BUTTON_FONT_SIZE = "16px"
SKIP_MSGBAR_HEADER = "X-Skip-MsgBar"

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


def _get_theme_defaults(app) -> tuple[str | None, str | None, str | None]:
    """Retrieve theme defaults from the Platzky database.

    Wraps DB calls in try-except so that a database failure
    never prevents the message bar from rendering.

    Args:
        app: The Platzky Engine instance

    Returns:
        Tuple of (primary_color, secondary_color, font), any of which may be None
    """
    try:
        primary_color = app.db.get_primary_color()
        secondary_color = app.db.get_secondary_color()
        font = app.db.get_font()
        return primary_color, secondary_color, font
    except Exception:
        logger.warning("Failed to retrieve theme defaults from database, using hardcoded defaults")
        return None, None, None


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


class MsgBarPlugin(PluginBase[MsgBarConfig]):
    """Plugin that displays a customizable message bar at the top of web pages."""

    @classmethod
    def get_config_model(cls) -> type[MsgBarConfig]:
        """Return the configuration model for this plugin."""
        return MsgBarConfig

    def process(self, app):
        """Process and inject a message bar into the Flask application.

        This method configures the msgbar plugin by:
        1. Validating the plugin configuration using Pydantic (prevents CSS injection)
        2. Converting markdown message to HTML and sanitizing it (prevents XSS)
        3. Retrieving theme defaults from the Platzky database
        4. Registering an after_request hook to inject the message bar HTML/CSS

        Args:
            app: The Platzky Engine instance to modify

        Returns:
            The modified Engine instance with message bar functionality
        """
        config = cast(MsgBarConfig, self.config)

        message = _render_message(config.message)

        # Get Platzky defaults from database (gracefully handles DB failures)
        platzky_primary_color, platzky_secondary_color, platzky_font = _get_theme_defaults(app)

        # Get validated CSS values with fallback priority:
        # 1. Validated plugin config (from Pydantic model)
        # 2. Platzky DB defaults
        # 3. Hardcoded defaults
        background_color = config.get_validated_background_color(platzky_primary_color or "#245466")

        text_color = config.get_validated_text_color(platzky_secondary_color or "white")

        font_family = config.get_validated_font_family(
            f"'{platzky_font}', sans-serif" if platzky_font else "'Arial', sans-serif"
        )

        font_size = config.get_validated_font_size("14px")

        bar_height = config.get_validated_bar_height("30px")

        bar_html = _build_bar_html(
            message=message,
            background_color=background_color,
            text_color=text_color,
            font_size=font_size,
            font_family=font_family,
            bar_height=bar_height,
        )

        @app.after_request
        def inject_msg_bar(response: Response) -> Response:
            """Inject message bar HTML and CSS into HTML responses.

            This Flask after_request hook intercepts HTML responses and injects
            the message bar styles and HTML before the closing </head> tag.

            Args:
                response: The Flask Response object to modify

            Returns:
                The modified Response object with injected message bar (if HTML)
                or the original response unchanged (if not HTML)
            """
            if "text/html" not in response.headers.get("Content-Type", ""):
                return response

            if response.headers.get(SKIP_MSGBAR_HEADER):
                return response

            try:
                html = response.get_data(as_text=True)
            except UnicodeDecodeError:
                logger.warning("Failed to decode response data, msgbar not injected")
                return response

            try:
                if "</head>" not in html:
                    logger.warning("No </head> tag found, msgbar not injected")
                    return response

                html = html.replace("</head>", bar_html + "</head>", 1)
                response.set_data(html)
            except Exception:
                logger.exception("Failed to inject message bar")

            return response

        return app
