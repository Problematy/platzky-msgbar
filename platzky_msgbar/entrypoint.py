from flask import Flask, Response
from typing import Any, Dict
import markdown


def process(app: Flask, plugin_config: Dict[str, Any]):

    app.config["msgbar"] = plugin_config or {}

    print(plugin_config)

    # Get message and convert markdown to HTML
    message_raw = app.config["msgbar"].get(
        "message", "This is a default notification message."
    )
    # Convert markdown to HTML (inline only, no <p> tags)
    message = markdown.markdown(
        message_raw, extensions=["extra"], output_format="html"
    ).strip()
    # Remove wrapping <p> tags if present (for inline rendering)
    if message.startswith("<p>") and message.endswith("</p>"):
        message = message[3:-4]

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
        app.config["msgbar"].get("background_color")
        or platzky_primary_color
        or "#245466"
    )

    text_color = (
        app.config["msgbar"].get("text_color") or platzky_secondary_color or "white"
    )

    font_family = (
        app.config["msgbar"].get("font_family")
        or (f"'{platzky_font}', sans-serif" if platzky_font else None)
        or "'Arial', sans-serif"
    )

    font_size = app.config["msgbar"].get("font_size") or "14px"

    bar_height = app.config["msgbar"].get("bar_height") or "30px"

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
