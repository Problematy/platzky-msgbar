from flask import Flask, Response
from typing import Any, Dict


def process(app: Flask, plugin_config: Dict[str, Any]):

    app.config["msgbar"] = plugin_config or {}
    message = app.config["msgbar"].get(
        "message", "This is a default notification message."
    )

    @app.after_request
    def inject_msg_bar(response: Response) -> Response:
        if "text/html" in response.headers.get("Content-Type", ""):
            bar_html = f"""
<style id="MsgBarStyle">
#MsgBar {{
    background-color: #245466;
    color: white;
    width: 100%;
    text-align: center;
    padding: 5px 40px 5px 10px;
    font-size: 14px;
    font-family: 'Arial', sans-serif;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 9999;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
#MsgBar .close-btn {{
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-weight: bold;
    font-size: 16px;
    color: white;
    cursor: pointer;
    background: none;
    border: none;
}}
body {{
    padding-top: 30px !important;
}}
body[data-cy-test="true"] #MsgBar {{
    position: relative !important;
    top: auto !important;
    overflow: visible !important;
}}
body[data-cy-test="true"] #MsgBar .close-btn {{
    top: 5px !important;
    transform: none !important;
}}
</style>
<div id="MsgBar">
    {message}
    <button class="close-btn" onclick="document.getElementById('MsgBar').remove();document.getElementById('MsgBarStyle').remove();">&times;</button>
</div>
"""

            html = response.get_data(as_text=True)
            html = html.replace("</head>", bar_html + "</head>")
            response.set_data(html)

        return response

    return app
