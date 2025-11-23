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


def test_msgbar_with_markdown_link_attributes():

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
                            "message": 'Visit [our site](https://example.com){:target="_blank" rel="noopener"}',
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

    # Check that markdown link with attributes is converted correctly
    assert 'target="_blank"' in decoded_response
    assert 'rel="noopener"' in decoded_response
    assert '<a href="https://example.com"' in decoded_response
    assert "our site</a>" in decoded_response


def test_msgbar_sanitizes_script_tags():
    """Test that script tags are stripped to prevent XSS attacks"""
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
                            "message": "Hello <script>alert('XSS')</script> World",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Extract the message bar content specifically
    import re

    msgbar_match = re.search(r'<div class="msg-content">(.*?)</div>', decoded_response)
    assert msgbar_match is not None
    msgbar_content = msgbar_match.group(1)

    # Script tags should be completely removed from message content
    assert "<script>" not in msgbar_content
    assert "</script>" not in msgbar_content
    assert (
        "alert('XSS')" in msgbar_content
    )  # Text content remains but tags are stripped
    # The safe content should still be present
    assert "Hello" in msgbar_content
    assert "World" in msgbar_content


def test_msgbar_sanitizes_javascript_urls():
    """Test that javascript: URLs are blocked"""
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
                            "message": "[Click me](javascript:alert('XSS'))",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # javascript: URL should be blocked - the entire href should be removed
    assert "javascript:" not in decoded_response
    assert "alert('XSS')" not in decoded_response
    # The link text should still be present but without the dangerous href
    assert "Click me" in decoded_response


def test_msgbar_sanitizes_event_handlers():
    """Test that event handlers like onclick are stripped"""
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
                            "message": "[Link](https://example.com){:onclick=\"alert('XSS')\"}",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Extract the message bar content specifically
    import re

    msgbar_match = re.search(
        r'<div class="msg-content">(.*?)</div>', decoded_response, re.DOTALL
    )
    assert msgbar_match is not None
    msgbar_content = msgbar_match.group(1)

    # onclick attribute should be stripped from the message content links
    # The malicious onclick should not appear in the message link
    assert (
        "onclick" not in msgbar_content
        or 'onclick="document.getElementById' in decoded_response
    )  # Allow close button onclick
    assert "alert('XSS')" not in msgbar_content
    # The safe parts should still be present in the message content
    assert '<a href="https://example.com"' in msgbar_content
    assert "Link</a>" in msgbar_content
    # Verify no onclick on the link itself
    link_match = re.search(r'<a href="https://example.com"[^>]*>', msgbar_content)
    assert link_match is not None
    assert "onclick" not in link_match.group(0)


def test_msgbar_sanitizes_raw_html():
    """Test that raw HTML tags not in allowlist are stripped"""
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
                            "message": "Safe <strong>bold</strong> and <iframe src='evil.com'></iframe> unsafe",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Allowed tag (strong) should be present
    assert "<strong>bold</strong>" in decoded_response
    # Disallowed tag (iframe) should be stripped
    assert "<iframe" not in decoded_response
    assert "</iframe>" not in decoded_response
    assert "evil.com" not in decoded_response
    # The safe content should remain
    assert "Safe" in decoded_response
    assert "unsafe" in decoded_response


def test_msgbar_blocks_css_injection_in_background_color():
    """Test that CSS injection attempts in background_color are blocked"""
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
                            "message": "Test",
                            "background_color": "red; } body { display: none; } #foo {",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Extract the MsgBar CSS specifically
    import re

    msgbar_style_match = re.search(
        r'<style id="MsgBarStyle">(.*?)</style>', decoded_response, re.DOTALL
    )
    assert msgbar_style_match is not None
    msgbar_style = msgbar_style_match.group(1)

    # CSS injection should be blocked - the malicious CSS should not appear in MsgBar styles
    assert "display: none" not in msgbar_style
    assert "} #foo {" not in msgbar_style
    # The injected content should not break out of the MsgBar styling
    assert "#MsgBar {" in msgbar_style
    # Background should be a valid color (not containing injection)
    assert re.search(r"background-color:\s*[^;{]+;", msgbar_style) is not None


def test_msgbar_blocks_css_injection_in_font_family():
    """Test that CSS injection attempts in font_family are blocked"""
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
                            "message": "Test",
                            "font_family": "Arial'; } body { background: url('http://evil.com'); } #foo { font-family: '",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # CSS injection should be blocked
    assert "evil.com" not in decoded_response
    # Default font family should be used
    assert "font-family: 'Arial', sans-serif" in decoded_response


def test_msgbar_blocks_css_url_function():
    """Test that url() functions in CSS values are blocked"""
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
                            "message": "Test",
                            "font_family": "url('http://evil.com/font.woff')",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # url() function should be blocked
    assert (
        "url(" not in decoded_response or "url(data:" in decoded_response
    )  # Allow data URLs from other sources
    assert "evil.com" not in decoded_response


def test_msgbar_validates_css_size_values():
    """Test that invalid CSS size values are rejected"""
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
                            "message": "Test",
                            "font_size": "14px; color: red;",
                            "bar_height": "calc(100vh - 10px)",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Invalid size values should be rejected and defaults used
    assert "font-size: 14px" in decoded_response  # Default
    assert "color: red" not in decoded_response  # CSS injection blocked
    assert "calc(" not in decoded_response  # CSS function blocked
    assert "padding-top: 30px" in decoded_response  # Default height


def test_msgbar_accepts_valid_css_colors():
    """Test that valid CSS color values are accepted"""
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
                            "message": "Test",
                            "background_color": "#ff5733",
                            "text_color": "rgb(255, 255, 255)",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Valid colors should be accepted
    assert "background-color: #ff5733" in decoded_response
    assert "color: rgb(255, 255, 255)" in decoded_response


def test_msgbar_accepts_valid_css_sizes():
    """Test that valid CSS size values are accepted"""
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
                            "message": "Test",
                            "font_size": "16px",
                            "bar_height": "2rem",
                        },
                    }
                ],
            },
        },
    }

    config_with_plugin = Config.model_validate(data_with_plugin)
    app_with_plugin = create_app_from_config(config_with_plugin)

    response = app_with_plugin.test_client().get("/")
    decoded_response = response.data.decode()

    # Valid sizes should be accepted
    assert "font-size: 16px" in decoded_response
    assert "padding-top: 2rem" in decoded_response
