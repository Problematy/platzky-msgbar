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
