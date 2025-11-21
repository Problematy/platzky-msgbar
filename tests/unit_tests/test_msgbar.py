from typing import Any, Dict
from platzky.platzky import create_app_from_config, Config


def test_that_plugin_loads_msgbar():

    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {"pages": []},
                "plugins": [
                    {
                        "name": "msgbar",
                        "config": {
                            "message": "Your custom message goes here",
                        },
                    }
                ],
            },
        },
    }

    # expected data
    msgbar_function = "MsgBar"
    custom_message = "Your custom message goes here"

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")

    assert response.status_code == 404
    decoded_response = response.data.decode()

    assert msgbar_function in decoded_response
    assert custom_message in decoded_response


def test_msgbar_with_custom_styling():

    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {"pages": []},
                "plugins": [
                    {
                        "name": "msgbar",
                        "config": {
                            "message": "Styled message",
                            "background_color": "#ff5733",
                            "text_color": "#ffffff",
                            "font_family": "'Courier New', monospace",
                            "font_size": "16px",
                            "bar_height": "40px",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")

    assert response.status_code == 404
    decoded_response = response.data.decode()

    # Check that custom styling is applied
    assert "background-color: #ff5733" in decoded_response
    assert "color: #ffffff" in decoded_response
    assert "font-family: 'Courier New', monospace" in decoded_response
    assert "font-size: 16px" in decoded_response
    assert "padding-top: 40px" in decoded_response
    assert "Styled message" in decoded_response


def test_msgbar_with_platzky_theme_defaults():

    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {
                    "pages": [],
                    "primary_color": "#123456",
                    "secondary_color": "#abcdef",
                    "font": "Roboto",
                },
                "plugins": [
                    {
                        "name": "msgbar",
                        "config": {
                            "message": "Message with theme defaults",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")

    assert response.status_code == 404
    decoded_response = response.data.decode()

    # Check that Platzky theme defaults from DB are used
    assert "background-color: #123456" in decoded_response
    assert "color: #abcdef" in decoded_response
    assert "font-family: 'Roboto', sans-serif" in decoded_response
    assert "Message with theme defaults" in decoded_response


def test_msgbar_with_markdown_links():

    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {"pages": []},
                "plugins": [
                    {
                        "name": "msgbar",
                        "config": {
                            "message": "Check out [our website](https://example.com) for more info!",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")

    assert response.status_code == 404
    decoded_response = response.data.decode()

    # Check that markdown link is converted to HTML
    assert '<a href="https://example.com">' in decoded_response
    assert "our website</a>" in decoded_response
    # Check that the original markdown syntax is NOT present
    assert "[our website]" not in decoded_response
    assert "(https://example.com)" not in decoded_response


def test_msgbar_with_multiple_markdown_links():

    data_with_plugin: Dict[str, Any] = {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": {"pages": []},
                "plugins": [
                    {
                        "name": "msgbar",
                        "config": {
                            "message": "Visit [Google](https://google.com) or [GitHub](https://github.com)",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")

    assert response.status_code == 404
    decoded_response = response.data.decode()

    # Check that both markdown links are converted to HTML
    assert '<a href="https://google.com">' in decoded_response
    assert "Google</a>" in decoded_response
    assert '<a href="https://github.com">' in decoded_response
    assert "GitHub</a>" in decoded_response
