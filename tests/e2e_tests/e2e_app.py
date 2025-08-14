from platzky.platzky import create_app as base_create_app


def create_app(config_path: str):
    app = base_create_app(config_path=config_path)

    @app.route("/")
    def index():
        return "Hello from Flask (E2E)"

    return app
