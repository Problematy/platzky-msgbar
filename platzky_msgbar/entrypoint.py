from flask import Flask, Response
from typing import Any, Dict

def process(app: Flask, plugin_config: Dict[str, Any]):

    app.config["msgbar"] = plugin_config or {}
    message = app.config["msgbar"].get("message", "This is a default notification message.")

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
    background-color: #245466;
    color: white;
    font-size: 14px;
    font-family: 'Arial', sans-serif;
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

#MsgBar .close-btn {{
    position: relative;  /* wymagane przez testy */
    margin-left: auto;   /* dociąga maksymalnie w prawo */
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