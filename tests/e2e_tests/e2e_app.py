from flask import render_template_string
from platzky.platzky import create_app as base_create_app
from platzky_msgbar.entrypoint import process as msgbar_process


def create_app(config_path: str):
    # Base app
    app = base_create_app(config_path=config_path)

    # Inject MsgBar plugin with a test message
    msgbar_process(app, {"message": "Hello from MsgBar!"})

    @app.route("/")
    def index():
        # Minimal HTML with <head> so MsgBar plugin can inject CSS + div
        return render_template_string(
            """
            <html>
            <head>
                <title>E2E Test Page</title>
            </head>
            <body>
                <h1>Welcome to E2E Test</h1>
                <p>This page includes the MsgBar plugin for testing.</p>
            </body>
            </html>
        """
        )

    return app
