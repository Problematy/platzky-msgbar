from platzky.platzky import create_app as base_create_app


def create_app(config_path: str):
    return base_create_app(config_path=config_path)
