from flask import Response
from typing import Any, Dict
import markdown
import bleach
from platzky import Engine


def process(app: Engine, plugin_config: Dict[str, Any]):

    message_raw = plugin_config.get(
        "message", "This is a default notification message."
    )
    # Convert markdown to HTML (inline only, no <p> tags)
    # attr_list extension allows syntax like: [link](url){:target="_blank"}
    message_html = markdown.markdown(
        message_raw, extensions=["extra", "attr_list"], output_format="html"
    ).strip()
    # Remove wrapping <p> tags if present (for inline rendering)
    if message_html.startswith("<p>") and message_html.endswith("</p>"):
        message_html = message_html[3:-4]

    # Sanitize HTML to prevent XSS attacks
    # Allow only safe tags and attributes needed for message bar functionality
    allowed_tags = ["a", "strong", "em", "b", "i", "code", "br", "span"]
    allowed_attributes = {
        "a": ["href", "title", "target", "rel"],
        "span": ["class"],
    }
    # Sanitize and ensure no javascript: URLs or dangerous protocols
    message = bleach.clean(
        message_html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=["http", "https", "mailto"],
        strip=True,
    )

    # Get styling configuration with Platzky defaults fallback
    # Priority: plugin config > Platzky DB defaults > hardcoded defaults

    # Get Platzky defaults from database if available
    platzky_primary_color = None
    platzky_secondary_color = None
    platzky_font = None

    if hasattr(app, "db"):
        try:
            platzky_primary_color = app.db.get_primary_color()
            platzky_secondary_color = app.db.get_secondary_color()
            platzky_font = app.db.get_font()
        except Exception:
            pass  # If DB not available or methods don't exist, use hardcoded defaults

    background_color = (
        plugin_config.get("background_color") or platzky_primary_color or "#245466"
    )

    text_color = plugin_config.get("text_color") or platzky_secondary_color or "white"

    font_family = (
        plugin_config.get("font_family")
        or (f"'{platzky_font}', sans-serif" if platzky_font else None)
        or "'Arial', sans-serif"
    )

    font_size = plugin_config.get("font_size") or "14px"

    bar_height = plugin_config.get("bar_height") or "30px"

    @app.after_request
    def inject_msg_bar(response: Response) -> Response:
        if "text/html" in response.headers.get("Content-Type", ""):
            bar_html = f"""
<style id="MsgBarStyle">

#MsgBar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: {background_color};
    color: {text_color};
    font-size: {font_size};
    font-family: {font_family};
    z-index: 9999;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);

    display: flex;
    align-items: center;
    justify-content: center;
    padding: 5px 10px;
}}

#MsgBar .msg-content {{
    flex: 1;             /* zajmuje całą szerokość */
    text-align: center;  /* wyśrodkowanie napisu */
}}

#MsgBar .msg-content a {{
    color: inherit;
    text-decoration: underline;
    font-weight: bold;
}}

#MsgBar .msg-content a:hover {{
    text-decoration: none;
    opacity: 0.8;
}}

#MsgBar .close-btn {{
    position: relative;  /* wymagane przez testy */
    margin-left: auto;   /* dociąga maksymalnie w prawo */
    font-weight: bold;
    font-size: 16px;
    color: {text_color};
    cursor: pointer;
    background: none;
    border: none;
}}

body {{
    padding-top: {bar_height} !important;
}}

</style>
<div id="MsgBar">
    <div class="msg-content">{message}</div>
    <button class="close-btn" onclick="document.getElementById('MsgBar').remove();document.getElementById('MsgBarStyle').remove();">&times;</button>
</div>
"""

            html = response.get_data(as_text=True)
            html = html.replace("</head>", bar_html + "</head>")
            response.set_data(html)

        return response

    return app
