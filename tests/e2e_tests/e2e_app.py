from platzky.platzky import create_app as base_create_app
from platzky_msgbar.entrypoint import process as msgbar_process
from flask import Flask, render_template_string


def create_app(config_path: str):
    app = base_create_app(config_path=config_path)

    msgbar_process(app, {"message": "Hello from MsgBar!"})

    def index():
        # Make sure the MsgBar element exists in the page for Cypress
        return render_template_string("""
            <html>
            <body>
                <div id="MsgBar">{{ app.config['msgbar']['message'] }}</div>
            </body>
            </html>
        """, app=app)

    return app
