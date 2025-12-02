import re
from typing import Any, Dict, Optional
from platzky.platzky import create_app_from_config, Config
from flask import Flask


def _get_test_page():
    """Helper to create a minimal test page for unit tests"""
    return {
        "title": "Test Page",
        "slug": "test",
        "coverImage": {"url": "", "alternateText": ""},
        "date": "01-01-2024",
        "author": "",
        "comments": [],
        "excerpt": "",
        "tags": [],
        "language": "en",
        "contentInMarkdown": "Test content",
    }


def _create_test_config(
    plugin_config: Dict[str, Any],
    site_content: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create test configuration with plugin settings.

    Args:
        plugin_config: Plugin configuration dictionary
        site_content: Optional site content overrides (for theme defaults)

    Returns:
        Complete configuration dictionary for Platzky
    """
    base_site_content = {"pages": [_get_test_page()]}
    if site_content:
        base_site_content.update(site_content)

    return {
        "APP_NAME": "testingApp",
        "SECRET_KEY": "secret",
        "USE_WWW": False,
        "BLOG_PREFIX": "/",
        "TRANSLATION_DIRECTORIES": ["/some/fake/dir"],
        "DB": {
            "TYPE": "json",
            "DATA": {
                "site_content": base_site_content,
                "plugins": [{"name": "msgbar", "config": plugin_config}],
            },
        },
    }


def _create_app_with_plugin(
    plugin_config: Dict[str, Any], site_content: Optional[Dict[str, Any]] = None
) -> Flask:
    """
    Create Flask app with msgbar plugin configured.

    Args:
        plugin_config: Plugin configuration dictionary
        site_content: Optional site content overrides (for theme defaults)

    Returns:
        Configured Flask application
    """
    data = _create_test_config(plugin_config, site_content)
    config = Config.model_validate(data)
    return create_app_from_config(config)


def _get_response_html(app: Flask, path: str = "/page/test") -> str:
    """
    Get decoded HTML response from app.

    Args:
        app: Flask application
        path: Request path (default: /page/test)

    Returns:
        Decoded HTML response as string
    """
    response = app.test_client().get(path)
    assert response.status_code == 200
    return response.data.decode()


def _extract_msgbar_content(html: str) -> str:
    """
    Extract message bar content from HTML response.

    Args:
        html: Full HTML response

    Returns:
        Message bar content (text inside msg-content div)
    """
    match = re.search(r'<div class="msg-content">(.*?)</div>', html, re.DOTALL)
    assert match is not None, "MsgBar content not found in HTML"
    return match.group(1)


def _extract_msgbar_style(html: str) -> str:
    """
    Extract message bar CSS from HTML response.

    Args:
        html: Full HTML response

    Returns:
        Message bar CSS (content inside MsgBarStyle tag)
    """
    match = re.search(r'<style id="MsgBarStyle">(.*?)</style>', html, re.DOTALL)
    assert match is not None, "MsgBarStyle not found in HTML"
    return match.group(1)


def test_that_plugin_loads_msgbar():
    """Test that the plugin loads and injects the message bar."""
    app = _create_app_with_plugin({"message": "Your custom message goes here"})
    html = _get_response_html(app)

    assert "MsgBar" in html
    assert "Your custom message goes here" in html


def test_msgbar_with_custom_styling():
    """Test that custom styling options are applied correctly."""
    app = _create_app_with_plugin(
        {
            "message": "Styled message",
            "background_color": "#ff5733",
            "text_color": "#ffffff",
            "font_family": "'Courier New', monospace",
            "font_size": "16px",
            "bar_height": "40px",
        }
    )
    html = _get_response_html(app)

    # Check that custom styling is applied
    assert "background-color: #ff5733" in html
    assert "color: #ffffff" in html
    assert "font-family: 'Courier New', monospace" in html
    assert "font-size: 16px" in html
    assert "padding-top: 40px" in html
    assert "Styled message" in html


def test_msgbar_with_platzky_theme_defaults():
    """Test that Platzky theme defaults from DB are used when plugin config is not provided."""
    site_content = {
        "primary_color": "#123456",
        "secondary_color": "#abcdef",
        "font": "Roboto",
    }
    app = _create_app_with_plugin(
        {"message": "Message with theme defaults"}, site_content
    )
    html = _get_response_html(app)

    # Check that Platzky theme defaults from DB are used
    assert "background-color: #123456" in html
    assert "color: #abcdef" in html
    assert "font-family: 'Roboto', sans-serif" in html
    assert "Message with theme defaults" in html


def test_msgbar_with_markdown_links():
    """Test that markdown links are converted to HTML."""
    app = _create_app_with_plugin(
        {
            "message": "Check out [our website](https://example.com) for more info!",
        }
    )
    html = _get_response_html(app)

    # Check that markdown link is converted to HTML
    assert '<a href="https://example.com">' in html
    assert "our website</a>" in html
    # Check that the original markdown syntax is NOT present
    assert "[our website]" not in html
    assert "(https://example.com)" not in html


def test_msgbar_with_multiple_markdown_links():
    """Test that multiple markdown links are converted to HTML."""
    app = _create_app_with_plugin(
        {
            "message": "Visit [Google](https://google.com) or [GitHub](https://github.com)",
        }
    )
    html = _get_response_html(app)

    # Check that both markdown links are converted to HTML
    assert '<a href="https://google.com">' in html
    assert "Google</a>" in html
    assert '<a href="https://github.com">' in html
    assert "GitHub</a>" in html


def test_msgbar_with_markdown_link_attributes():
    """Test that markdown link attributes are properly converted."""
    app = _create_app_with_plugin(
        {
            "message": 'Visit [our site](https://example.com){:target="_blank" rel="noopener"}',
        }
    )
    html = _get_response_html(app)

    # Check that markdown link with attributes is converted correctly
    assert 'target="_blank"' in html
    assert 'rel="noopener"' in html
    assert '<a href="https://example.com"' in html
    assert "our site</a>" in html


def test_msgbar_sanitizes_script_tags():
    """Test that script tags are stripped to prevent XSS attacks"""
    app = _create_app_with_plugin(
        {
            "message": "Hello <script>alert('XSS')</script> World",
        }
    )
    html = _get_response_html(app)
    msgbar_content = _extract_msgbar_content(html)

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
    app = _create_app_with_plugin(
        {
            "message": "[Click me](javascript:alert('XSS'))",
        }
    )
    html = _get_response_html(app)

    # javascript: URL should be blocked - the entire href should be removed
    assert "javascript:" not in html
    assert "alert('XSS')" not in html
    # The link text should still be present but without the dangerous href
    assert "Click me" in html


def test_msgbar_sanitizes_event_handlers():
    """Test that event handlers like onclick are stripped"""
    app = _create_app_with_plugin(
        {
            "message": "[Link](https://example.com){:onclick=\"alert('XSS')\"}",
        }
    )
    html = _get_response_html(app)
    msgbar_content = _extract_msgbar_content(html)

    # onclick attribute should be stripped from the message content links
    # The malicious onclick should not appear in the message link
    # No inline onclick handlers are allowed inside message content
    assert "onclick" not in msgbar_content
    # But the close button's onclick (outside msg-content) should still exist
    assert 'onclick="document.getElementById' in html
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
    app = _create_app_with_plugin(
        {
            "message": "Safe <strong>bold</strong> and <iframe src='evil.com'></iframe> unsafe",
        }
    )
    html = _get_response_html(app)

    # Allowed tag (strong) should be present
    assert "<strong>bold</strong>" in html
    # Disallowed tag (iframe) should be stripped
    assert "<iframe" not in html
    assert "</iframe>" not in html
    assert "evil.com" not in html
    # The safe content should remain
    assert "Safe" in html
    assert "unsafe" in html


def test_msgbar_blocks_css_injection_in_background_color():
    """Test that CSS injection attempts in background_color are blocked"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "background_color": "red; } body { display: none; } #foo {",
        }
    )
    html = _get_response_html(app)
    msgbar_style = _extract_msgbar_style(html)

    # CSS injection should be blocked - the malicious CSS should not appear in MsgBar styles
    assert "display: none" not in msgbar_style
    assert "} #foo {" not in msgbar_style
    # The injected content should not break out of the MsgBar styling
    assert "#MsgBar {" in msgbar_style
    # Background should be a valid color (not containing injection)
    assert re.search(r"background-color:\s*[^;{]+;", msgbar_style) is not None


def test_msgbar_blocks_css_injection_in_font_family():
    """Test that CSS injection attempts in font_family are blocked"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "font_family": "Arial'; } body { background: url('http://evil.com'); } #foo { font-family: '",
        }
    )
    html = _get_response_html(app)

    # CSS injection should be blocked
    assert "evil.com" not in html
    # Default font family should be used
    assert "font-family: 'Arial', sans-serif" in html


def test_msgbar_blocks_css_url_function():
    """Test that url() functions in CSS values are blocked"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "font_family": "url('http://evil.com/font.woff')",
        }
    )
    html = _get_response_html(app)
    msgbar_style = _extract_msgbar_style(html)

    # url() function should be blocked in MsgBar CSS
    assert "url(" not in msgbar_style
    assert "evil.com" not in html


def test_msgbar_validates_css_size_values():
    """Test that invalid CSS size values are rejected"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "font_size": "14px; color: red;",
            "bar_height": "calc(100vh - 10px)",
        }
    )
    html = _get_response_html(app)

    # Invalid size values should be rejected and defaults used
    assert "font-size: 14px" in html  # Default
    assert "color: red" not in html  # CSS injection blocked
    assert "calc(" not in html  # CSS function blocked
    assert "padding-top: 30px" in html  # Default height


def test_msgbar_accepts_valid_css_colors():
    """Test that valid CSS color values are accepted"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "background_color": "#ff5733",
            "text_color": "rgb(255, 255, 255)",
        }
    )
    html = _get_response_html(app)

    # Valid colors should be accepted
    assert "background-color: #ff5733" in html
    assert "color: rgb(255, 255, 255)" in html


def test_msgbar_accepts_valid_css_sizes():
    """Test that valid CSS size values are accepted"""
    app = _create_app_with_plugin(
        {
            "message": "Test",
            "font_size": "16px",
            "bar_height": "2rem",
        }
    )
    html = _get_response_html(app)

    # Valid sizes should be accepted
    assert "font-size: 16px" in html
    assert "padding-top: 2rem" in html


def test_msgbar_requires_message_field():
    """Test that omitting the message field causes a validation error"""
    import pytest
    from platzky.plugin_loader import PluginError

    data = _create_test_config({})  # Missing required 'message' field
    config = Config.model_validate(data)

    # Creating the app should raise a PluginError wrapping the ValidationError
    with pytest.raises(PluginError) as exc_info:
        create_app_from_config(config)

    # Verify the error is about the missing 'message' field
    assert "message" in str(exc_info.value).lower()
    assert "field required" in str(exc_info.value).lower()
